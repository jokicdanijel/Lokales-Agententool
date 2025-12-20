#!/usr/bin/env python3
"""
ELION Hyper-Dashboard – Workspace Evaluation Framework (v1.1)
Enterprise-grade assessment of production-readiness across 7 dimensions.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Configuration
EVALUATION_VERSION = "1.1"
REPORT_FILENAME = "workspace_evaluation_report.json"
PORT_POLICY_MIN, PORT_POLICY_MAX = 12344, 12399

# ============================================================================
# Core: Evaluation Category
# ============================================================================

class EvalCategory:
    def __init__(self, name: str, desc: str, weight: float = 1.0):
        self.name = name
        self.description = desc
        self.weight = weight
        self.checks: List[Tuple[str, bool, str]] = []
        self.score = 0.0

    def add_check(self, name: str, passed: bool, detail: str = ""):
        self.checks.append((name, passed, detail))

    def calculate_score(self) -> float:
        if not self.checks:
            return 100.0
        self.score = (sum(1 for _, p, _ in self.checks if p) / len(self.checks)) * 100
        return self.score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.name,
            "description": self.description,
            "weight": self.weight,
            "score": round(self.score, 2),
            "total_checks": len(self.checks),
            "passed_checks": sum(1 for _, p, _ in self.checks if p),
            "failed_checks": sum(1 for _, p, _ in self.checks if not p),
            "checks": [
                {"name": n, "passed": p, "detail": d}
                for n, p, d in self.checks
            ]
        }


# ============================================================================
# Evaluators: Policy, Python, Infrastructure, Config, Quality, Docs, Deploy
# ============================================================================

def eval_policy(root: str) -> EvalCategory:
    cat = EvalCategory("Policy & Governance", "Port-Policy, SoT, Secrets", 2.5)
    
    ops_sh = os.path.join(root, "bin", "ops.sh")
    if os.path.exists(ops_sh):
        with open(ops_sh, 'r') as f:
            ops_content = f.read()
        cat.add_check("No 8080", "8080" not in ops_content)
        cat.add_check("AGENTS mapping exists", "AGENTS=(" in ops_content)
    else:
        cat.add_check("ops.sh exists", False)
    
    # .env not sourced in scripts
    bad_scripts = []
    for script in Path(root).rglob("bin/start_*.sh"):
        with open(script, 'r') as f:
            if re.search(r'source.*\.env|export\s*\$\(.*grep.*\.env', f.read()):
                bad_scripts.append(str(script.relative_to(root)))
    cat.add_check(".env not sourced in scripts", len(bad_scripts) == 0,
                  f"Found: {bad_scripts[0]}" if bad_scripts else "")
    
    # .env permissions
    env_file = os.path.join(root, ".env")
    if os.path.exists(env_file):
        mode = os.stat(env_file).st_mode
        cat.add_check(".env not world-readable", not bool(mode & 0o004))
    else:
        cat.add_check(".env exists", False)
    
    cat.calculate_score()
    return cat


def eval_python(root: str) -> EvalCategory:
    cat = EvalCategory("Python Environment", "venv, Dependencies", 1.5)
    
    venv_exists = os.path.isdir(os.path.join(root, ".venv"))
    cat.add_check(".venv exists", venv_exists)
    
    req_file = os.path.join(root, "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            req = f.read().lower()
        cat.add_check("pydantic in requirements", "pydantic" in req)
        cat.add_check("pydantic-settings in requirements", "pydantic-settings" in req)
        cat.add_check("fastapi in requirements", "fastapi" in req)
    else:
        cat.add_check("requirements.txt exists", False)
    
    cat.calculate_score()
    return cat


def eval_infra(root: str) -> EvalCategory:
    cat = EvalCategory("Infrastructure & Operations", "ops.sh, Logs, Runbook", 1.5)
    
    ops_sh = os.path.join(root, "bin", "ops.sh")
    if os.path.exists(ops_sh):
        try:
            result = subprocess.run(["bash", "-n", ops_sh], capture_output=True, timeout=5)
            cat.add_check("ops.sh syntax valid", result.returncode == 0)
        except:
            cat.add_check("ops.sh syntax valid", False)
        cat.add_check("ops.sh executable", os.access(ops_sh, os.X_OK))
    else:
        cat.add_check("ops.sh exists", False)
    
    cat.add_check("logs/ exists", os.path.isdir(os.path.join(root, "logs")))
    
    runbook = os.path.join(root, "docs", "agent_startanleitung.html")
    if os.path.exists(runbook):
        with open(runbook, 'r') as f:
            html = f.read()
        cat.add_check("HTML Runbook valid", 
                      "<!doctype html>" in html.lower() and "</html>" in html.lower())
    else:
        cat.add_check("HTML Runbook exists", False)
    
    cat.calculate_score()
    return cat


def eval_config(root: str) -> EvalCategory:
    cat = EvalCategory("Configuration & Secrets", ".env, Keys, Tokens", 2.5)
    
    env_file = os.path.join(root, ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env = f.read()
        cat.add_check("DASHBOARD_ADMIN_TOKEN set", "DASHBOARD_ADMIN_TOKEN" in env)
        cat.add_check("OPENAI_API_KEY_OPENA1 set", "OPENAI_API_KEY_OPENA1" in env)
        cat.add_check("OPENAI_API_KEY_OPENA2 set", "OPENAI_API_KEY_OPENA2" in env)
        cat.add_check("No placeholders", 
                      not re.search(r'(YOUR_|CHANGE_ME|FIXME|TODO)', env, re.IGNORECASE))
    else:
        cat.add_check(".env exists", False)
    
    cat.calculate_score()
    return cat


def eval_quality(root: str) -> EvalCategory:
    cat = EvalCategory("Code Quality & Standards", "Tests, gitignore, README", 1.0)
    
    cat.add_check("tests/ exists", os.path.isdir(os.path.join(root, "tests")))
    
    gi_file = os.path.join(root, ".gitignore")
    if os.path.exists(gi_file):
        with open(gi_file, 'r') as f:
            gi = f.read()
        cat.add_check(".gitignore covers .env, venv, cache",
                      all(x in gi for x in [".env", ".venv", "__pycache__"]))
    else:
        cat.add_check(".gitignore exists", False)
    
    cat.add_check("README exists", 
                  any(os.path.exists(os.path.join(root, f)) for f in ["README.md", "README.rst"]))
    
    cat.calculate_score()
    return cat


def eval_docs(root: str) -> EvalCategory:
    cat = EvalCategory("Documentation & Accessibility", "Runbooks, Guides", 0.8)
    
    docs_dir = os.path.join(root, "docs")
    if os.path.isdir(docs_dir):
        docs = [f for f in os.listdir(docs_dir) if f.endswith(('.md', '.rst', '.html'))]
        cat.add_check("Doc files present", len(docs) > 0)
    else:
        cat.add_check("docs/ exists", False)
    
    runbook = os.path.join(root, "docs", "agent_startanleitung.html")
    cat.add_check("HTML Runbook present", os.path.exists(runbook))
    
    cat.calculate_score()
    return cat


def eval_deploy(root: str) -> EvalCategory:
    cat = EvalCategory("Deployment Readiness", "Monitoring, Logging, Scaling", 1.2)
    
    cat.add_check("logs/ exists", os.path.isdir(os.path.join(root, "logs")))
    
    env_ex = os.path.join(root, ".env.example")
    cat.add_check(".env.example present", os.path.exists(env_ex))
    
    compose = os.path.join(root, "docker-compose.prod.yml")
    cat.add_check("docker-compose.prod.yml present", os.path.exists(compose))
    
    cat.calculate_score()
    return cat


# ============================================================================
# Main: Runner & Reporter
# ============================================================================

def run_evaluation(root: str) -> Dict[str, Any]:
    print(f"\n{'='*80}")
    print(f"ELION Hyper-Dashboard – Workspace Evaluation v{EVALUATION_VERSION}")
    print(f"Project: {root}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*80}\n")
    
    evaluators = [
        eval_policy(root),
        eval_python(root),
        eval_infra(root),
        eval_config(root),
        eval_quality(root),
        eval_docs(root),
        eval_deploy(root),
    ]
    
    categories = [e.to_dict() for e in evaluators]
    total_score = sum(e.score * e.weight for e in evaluators)
    total_weight = sum(e.weight for e in evaluators)
    overall_score = total_score / total_weight if total_weight > 0 else 0
    
    if overall_score >= 90:
        readiness, emoji = "PRODUCTION_READY", "✅"
    elif overall_score >= 75:
        readiness, emoji = "PRODUCTION_READY_WITH_REVIEW", "⚠️"
    elif overall_score >= 60:
        readiness, emoji = "STAGING_READY", "🔶"
    else:
        readiness, emoji = "DEVELOPMENT_ONLY", "❌"
    
    return {
        "evaluation_version": EVALUATION_VERSION,
        "timestamp": datetime.now().isoformat(),
        "project_root": root,
        "overall_score": round(overall_score, 2),
        "readiness_level": readiness,
        "readiness_emoji": emoji,
        "categories": categories,
        "total_checks": sum(len(c["checks"]) for c in categories),
        "passed_checks": sum(c["passed_checks"] for c in categories),
        "failed_checks": sum(c["failed_checks"] for c in categories),
    }


def print_report(report: Dict[str, Any]) -> None:
    emoji = report["readiness_emoji"]
    readiness = report["readiness_level"]
    score = report["overall_score"]
    passed = report["passed_checks"]
    failed = report["failed_checks"]
    total = report["total_checks"]

    print(f"\n{'='*80}")
    print(f"{emoji} READINESS: {readiness}")
    print(f"{'='*80}")
    print(f"Score: {score}/100 | Passed: {passed}/{total} | Failed: {failed}\n")

    for cat in report["categories"]:
        name = cat["category"]
        score_val = cat["score"]
        p = cat["passed_checks"]
        t = cat["total_checks"]
        
        if score_val >= 90:
            st = "✅"
        elif score_val >= 75:
            st = "⚠️"
        elif score_val >= 60:
            st = "🔶"
        else:
            st = "❌"

        print(f"{st} {name:<40} {score_val:>5.1f}% ({p}/{t})")
        
        for check in cat["checks"]:
            if not check["passed"]:
                detail = f" – {check['detail']}" if check['detail'] else ""
                print(f"    ❌ {check['name']}{detail}")
        print()

    print(f"{'='*80}")
    print(f"Report: {REPORT_FILENAME}\n")


def main():
    root = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else os.getcwd()
    
    if not os.path.exists(os.path.join(root, "bin", "ops.sh")):
        print(f"❌ Not a valid ELION project root: {root}")
        sys.exit(1)
    
    report = run_evaluation(root)
    print_report(report)
    
    with open(os.path.join(root, REPORT_FILENAME), 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Report saved: {os.path.join(root, REPORT_FILENAME)}\n")
    sys.exit(0 if report["readiness_level"].startswith("PRODUCTION") else 1)


if __name__ == "__main__":
    main()
