#!/usr/bin/env python3
"""
Deterministic Agent Discovery Script
=====================================

ROLE: Deterministic Discovery Engineer

HARD CONSTRAINTS:
- Read-only analysis: NO code execution, NO network calls
- Deterministic output: hashing + stable ordering
- Missing/empty agent folders => FAIL
- Port mismatches vs baseline => FAIL (unless no port references exist)

INPUTS: system_baseline.yaml
OUTPUTS: artifacts/agent_inventory.json

FEATURES:
- Recursive file enumeration with SHA256 hashing
- Static AST-based Python analysis (imports, endpoints, ports, agent refs)
- HTML parsing (data-* attrs, forms/nav, ports, agent refs)
- JSON/YAML/ENV parsing (ports, agent refs)
- Validation: unknown agents, forbidden ports, port mismatches
- Fail-fast with explicit violation lists
"""

import ast
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class FileInfo:
    """Information about a single file."""

    path: str
    relative_path: str
    sha256: str
    size_bytes: int
    file_type: str

    # Static analysis results
    imports: list[str] = field(default_factory=list)
    endpoints: list[str] = field(default_factory=list)
    ports_detected: list[int] = field(default_factory=list)
    agent_references: list[str] = field(default_factory=list)

    # Flags
    has_main: bool = False
    has_requirements: bool = False
    has_dockerfile: bool = False
    has_config: bool = False


@dataclass
class AgentInventory:
    """Complete inventory for a single agent."""

    agent_id: str
    baseline_port: int
    baseline_role: str
    baseline_visibility: str
    folder_path: str

    # File statistics
    file_count: int = 0
    total_size_bytes: int = 0

    # Files by type
    python_files: int = 0
    html_files: int = 0
    json_files: int = 0
    yaml_files: int = 0
    other_files: int = 0

    # Discovered data
    all_imports: list[str] = field(default_factory=list)
    all_endpoints: list[str] = field(default_factory=list)
    ports_detected: set[int] = field(default_factory=set)
    agent_references: set[str] = field(default_factory=set)

    # Flags
    has_main: bool = False
    has_requirements: bool = False
    has_dockerfile: bool = False
    has_config: bool = False

    # Detailed file list
    files: list[FileInfo] = field(default_factory=list)

    # Violations
    violations: list[str] = field(default_factory=list)


@dataclass
class DiscoveryReport:
    """Complete discovery report for all agents."""

    baseline_hash: str
    discovery_timestamp: str
    agents: dict[str, AgentInventory] = field(default_factory=dict)
    global_violations: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# FILE ANALYZERS
# ============================================================================


class PythonAnalyzer:
    """Static analysis of Python files using AST."""

    @staticmethod
    def analyze(file_path: Path) -> FileInfo:
        """Analyze a Python file."""
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        file_info = FileInfo(
            path=str(file_path),
            relative_path=file_path.name,
            sha256=hashlib.sha256(content.encode()).hexdigest(),
            size_bytes=file_path.stat().st_size,
            file_type="python",
        )

        # AST-based import extraction
        try:
            tree = ast.parse(content, filename=str(file_path))
            file_info.imports = PythonAnalyzer._extract_imports(tree)
            file_info.has_main = PythonAnalyzer._has_main_block(tree)
        except SyntaxError:
            # Invalid Python syntax - skip AST analysis
            pass

        # Endpoint detection (FastAPI/Flask)
        file_info.endpoints = PythonAnalyzer._extract_endpoints(content)

        # Port literal detection
        file_info.ports_detected = PythonAnalyzer._extract_ports(content)

        # Agent reference detection (opena1, opena2, ...)
        file_info.agent_references = PythonAnalyzer._extract_agent_refs(content)

        return file_info

    @staticmethod
    def _extract_imports(tree: ast.AST) -> list[str]:
        """Extract all import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return sorted(set(imports))

    @staticmethod
    def _has_main_block(tree: ast.AST) -> bool:
        """Check if file has if __name__ == '__main__' block."""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if isinstance(node.test, ast.Compare):
                    if isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__":
                        return True
        return False

    @staticmethod
    def _extract_endpoints(content: str) -> list[str]:
        """Extract API endpoints from decorators."""
        endpoints = []

        # FastAPI patterns: @app.get("/path"), @router.post("/path")
        fastapi_pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)'
        matches = re.findall(fastapi_pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                endpoints.append(match[1])

        # Flask patterns: @app.route("/path")
        flask_pattern = r'@app\.route\(["\']([^"\']+)'
        endpoints.extend(re.findall(flask_pattern, content))

        return sorted(set(endpoints))

    @staticmethod
    def _extract_ports(content: str) -> list[int]:
        """Extract port number literals."""
        ports = []

        # Pattern 1: port=12345
        port_assign = re.findall(r"port\s*=\s*(\d{4,5})", content, re.IGNORECASE)
        ports.extend([int(p) for p in port_assign])

        # Pattern 2: :12345 in URLs
        port_url = re.findall(r':(\d{4,5})(?:/|"|\'|\s)', content)
        ports.extend([int(p) for p in port_url])

        # Pattern 3: PORT = 12345
        port_const = re.findall(r"PORT\s*=\s*(\d{4,5})", content)
        ports.extend([int(p) for p in port_const])

        return sorted(set([p for p in ports if 1024 <= p <= 65535]))

    @staticmethod
    def _extract_agent_refs(content: str) -> list[str]:
        """Extract references to other agents (opena1, opena2, ...)."""
        agent_refs = re.findall(r"\bopena(\d{1,2})\b", content, re.IGNORECASE)
        return sorted(set([f"opena{ref}" for ref in agent_refs]))


class HTMLAnalyzer:
    """Static analysis of HTML files."""

    @staticmethod
    def analyze(file_path: Path) -> FileInfo:
        """Analyze an HTML file."""
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        file_info = FileInfo(
            path=str(file_path),
            relative_path=file_path.name,
            sha256=hashlib.sha256(content.encode()).hexdigest(),
            size_bytes=file_path.stat().st_size,
            file_type="html",
        )

        # data-* attribute detection
        data_attrs = re.findall(r"data-[\w-]+", content)
        file_info.endpoints.extend(sorted(set(data_attrs)))

        # Port detection
        file_info.ports_detected = PythonAnalyzer._extract_ports(content)

        # Agent reference detection
        file_info.agent_references = PythonAnalyzer._extract_agent_refs(content)

        # Check for forms and navigation
        file_info.has_main = bool(re.search(r"<form", content, re.IGNORECASE))

        return file_info


class ConfigAnalyzer:
    """Static analysis of JSON/YAML/ENV files."""

    @staticmethod
    def analyze(file_path: Path, file_type: str) -> FileInfo:
        """Analyze a config file."""
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        file_info = FileInfo(
            path=str(file_path),
            relative_path=file_path.name,
            sha256=hashlib.sha256(content.encode()).hexdigest(),
            size_bytes=file_path.stat().st_size,
            file_type=file_type,
        )

        # Port detection
        file_info.ports_detected = PythonAnalyzer._extract_ports(content)

        # Agent reference detection
        file_info.agent_references = PythonAnalyzer._extract_agent_refs(content)

        return file_info


# ============================================================================
# AGENT SCANNER
# ============================================================================


class AgentScanner:
    """Scans an agent folder recursively."""

    def __init__(self, agent_id: str, baseline_info: dict, root_path: Path):
        self.agent_id = agent_id
        self.baseline_info = baseline_info
        self.root_path = root_path

        # Try to find agent folder from baseline or use naming pattern
        folder_path = baseline_info.get("folder_path", "")
        if folder_path:
            self.agent_folder = root_path / folder_path
        else:
            # Search for folder matching agent ID pattern
            self.agent_folder = self._find_agent_folder()

    def _find_agent_folder(self) -> Path:
        """Find agent folder using naming conventions."""
        # Pattern 1: X.openaY_*
        agent_num = self.agent_id.replace("opena", "")
        patterns = [f"*{self.agent_id}*", f"*opena{agent_num}*", f"{agent_num}.opena{agent_num}_*"]

        for pattern in patterns:
            matches = list(self.root_path.glob(pattern))
            if matches:
                # Return first match that's a directory
                for match in matches:
                    if match.is_dir():
                        return match

        # Default fallback
        return self.root_path / f"agents/{self.agent_id}"

    def scan(self) -> AgentInventory:
        """Scan the agent folder and return inventory."""
        inventory = AgentInventory(
            agent_id=self.agent_id,
            baseline_port=self.baseline_info.get("port", 0),
            baseline_role=self.baseline_info.get("role", "unknown"),
            baseline_visibility=self.baseline_info.get("visibility", "unknown"),
            folder_path=str(self.agent_folder),
        )

        # Check if folder exists
        if not self.agent_folder.exists():
            inventory.violations.append(f"Agent folder does not exist: {self.agent_folder}")
            return inventory

        if not self.agent_folder.is_dir():
            inventory.violations.append(f"Agent path is not a directory: {self.agent_folder}")
            return inventory

        # Check if folder is empty
        files_list = list(self.agent_folder.rglob("*"))
        if not files_list:
            inventory.violations.append(f"Agent folder is empty: {self.agent_folder}")
            return inventory

        # Scan all files recursively
        for file_path in files_list:
            if not file_path.is_file():
                continue

            # Skip hidden files and cache directories
            if any(part.startswith(".") for part in file_path.parts):
                continue
            if "__pycache__" in file_path.parts:
                continue

            file_info = self._analyze_file(file_path)
            if file_info:
                inventory.files.append(file_info)
                inventory.file_count += 1
                inventory.total_size_bytes += file_info.size_bytes

                # Update type counters
                if file_info.file_type == "python":
                    inventory.python_files += 1
                elif file_info.file_type == "html":
                    inventory.html_files += 1
                elif file_info.file_type == "json":
                    inventory.json_files += 1
                elif file_info.file_type == "yaml":
                    inventory.yaml_files += 1
                else:
                    inventory.other_files += 1

                # Aggregate data
                inventory.all_imports.extend(file_info.imports)
                inventory.all_endpoints.extend(file_info.endpoints)
                inventory.ports_detected.update(file_info.ports_detected)
                inventory.agent_references.update(file_info.agent_references)

                # Update flags
                if file_info.has_main:
                    inventory.has_main = True
                if file_info.file_type == "python" and "requirements" in file_path.name.lower():
                    inventory.has_requirements = True
                if "dockerfile" in file_path.name.lower():
                    inventory.has_dockerfile = True
                if file_info.file_type in ("json", "yaml", "env"):
                    inventory.has_config = True

        # Deduplicate and sort
        inventory.all_imports = sorted(set(inventory.all_imports))
        inventory.all_endpoints = sorted(set(inventory.all_endpoints))
        inventory.ports_detected = sorted(inventory.ports_detected)
        inventory.agent_references = sorted(inventory.agent_references)

        return inventory

    def _analyze_file(self, file_path: Path) -> FileInfo | None:
        """Analyze a single file based on its type."""
        suffix = file_path.suffix.lower()

        try:
            if suffix == ".py":
                return PythonAnalyzer.analyze(file_path)
            elif suffix in (".html", ".htm"):
                return HTMLAnalyzer.analyze(file_path)
            elif suffix == ".json":
                return ConfigAnalyzer.analyze(file_path, "json")
            elif suffix in (".yaml", ".yml"):
                return ConfigAnalyzer.analyze(file_path, "yaml")
            elif ".env" in file_path.name.lower():
                return ConfigAnalyzer.analyze(file_path, "env")
            else:
                # Generic file info
                content = file_path.read_bytes()
                return FileInfo(
                    path=str(file_path),
                    relative_path=file_path.name,
                    sha256=hashlib.sha256(content).hexdigest(),
                    size_bytes=len(content),
                    file_type="other",
                )
        except Exception as e:
            print(f"WARNING: Failed to analyze {file_path}: {e}", file=sys.stderr)
            return None


# ============================================================================
# VALIDATOR
# ============================================================================


class DiscoveryValidator:
    """Validates discovery results against baseline and policies."""

    FORBIDDEN_PORTS = [8080, 3000]
    PORT_RANGE_MIN = 12344
    PORT_RANGE_MAX = 12399

    def __init__(self, baseline: dict, all_agent_ids: set[str]):
        self.baseline = baseline
        self.all_agent_ids = all_agent_ids

    def validate(self, inventory: AgentInventory) -> list[str]:
        """Validate a single agent inventory."""
        violations = []

        # Check for forbidden ports
        for port in inventory.ports_detected:
            if port in self.FORBIDDEN_PORTS:
                violations.append(
                    f"[{inventory.agent_id}] Forbidden port detected: {port} " f"(forbidden: {self.FORBIDDEN_PORTS})"
                )

        # Check for port mismatches (only if ports are detected)
        if inventory.ports_detected:
            expected_port = inventory.baseline_port
            if expected_port not in inventory.ports_detected:
                violations.append(
                    f"[{inventory.agent_id}] Port mismatch: expected {expected_port}, "
                    f"found {sorted(inventory.ports_detected)}"
                )

        # Check for unknown agent references
        for agent_ref in inventory.agent_references:
            if agent_ref not in self.all_agent_ids:
                violations.append(f"[{inventory.agent_id}] Unknown agent reference: {agent_ref}")

        # Check port range policy (12344-12399)
        for port in inventory.ports_detected:
            if not (self.PORT_RANGE_MIN <= port <= self.PORT_RANGE_MAX):
                violations.append(
                    f"[{inventory.agent_id}] Port {port} outside allowed range "
                    f"({self.PORT_RANGE_MIN}-{self.PORT_RANGE_MAX})"
                )

        return violations


# ============================================================================
# MAIN DISCOVERY ENGINE
# ============================================================================


class DiscoveryEngine:
    """Main discovery orchestrator."""

    def __init__(self, root_path: Path, baseline_path: Path):
        self.root_path = root_path
        self.baseline_path = baseline_path
        self.baseline = None
        self.baseline_hash = None

    def load_baseline(self) -> dict:
        """Load and hash system_baseline.yaml."""
        if not self.baseline_path.exists():
            print(f"ERROR: Baseline file not found: {self.baseline_path}", file=sys.stderr)
            sys.exit(1)

        content = self.baseline_path.read_text(encoding="utf-8")
        self.baseline_hash = hashlib.sha256(content.encode()).hexdigest()

        try:
            self.baseline = yaml.safe_load(content)
        except yaml.YAMLError as e:
            print(f"ERROR: Failed to parse baseline YAML: {e}", file=sys.stderr)
            sys.exit(1)

        return self.baseline

    def discover(self) -> DiscoveryReport:
        """Run full discovery process."""
        from datetime import datetime

        # Load baseline
        self.load_baseline()

        # Extract agent definitions (handle both legacy and new structure)
        agents_dict = {}

        # Try new structure first (nested agents dict)
        if "agents" in self.baseline:
            raw_agents = self.baseline["agents"]
            if isinstance(raw_agents, dict):
                # Already a dict
                agents_dict = raw_agents
            elif isinstance(raw_agents, list):
                # Convert list to dict
                agents_dict = {a["id"]: a for a in raw_agents if "id" in a}

        if not agents_dict:
            print("ERROR: No agents found in baseline", file=sys.stderr)
            sys.exit(1)

        all_agent_ids = set(agents_dict.keys())

        # Create report
        report = DiscoveryReport(
            baseline_hash=self.baseline_hash, discovery_timestamp=datetime.utcnow().isoformat() + "Z"
        )

        # Scan each agent
        validator = DiscoveryValidator(self.baseline, all_agent_ids)

        for agent_id, agent_info in sorted(agents_dict.items()):
            print(f"Scanning {agent_id}...", file=sys.stderr)

            scanner = AgentScanner(agent_id, agent_info, self.root_path)
            inventory = scanner.scan()

            # Validate
            validation_violations = validator.validate(inventory)
            inventory.violations.extend(validation_violations)

            # Add to report
            report.agents[agent_id] = inventory

            if inventory.violations:
                report.global_violations.extend(inventory.violations)

        # Generate summary
        report.summary = {
            "total_agents": len(agents_dict),
            "agents_scanned": len(report.agents),
            "agents_with_violations": sum(1 for inv in report.agents.values() if inv.violations),
            "total_files": sum(inv.file_count for inv in report.agents.values()),
            "total_violations": len(report.global_violations),
        }

        return report

    def write_report(self, report: DiscoveryReport, output_path: Path):
        """Write discovery report to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert dataclasses to dicts
        report_dict = {
            "baseline_hash": report.baseline_hash,
            "discovery_timestamp": report.discovery_timestamp,
            "summary": report.summary,
            "agents": {
                agent_id: {
                    "agent_id": inv.agent_id,
                    "baseline_port": inv.baseline_port,
                    "baseline_role": inv.baseline_role,
                    "baseline_visibility": inv.baseline_visibility,
                    "folder_path": inv.folder_path,
                    "file_count": inv.file_count,
                    "total_size_bytes": inv.total_size_bytes,
                    "python_files": inv.python_files,
                    "html_files": inv.html_files,
                    "json_files": inv.json_files,
                    "yaml_files": inv.yaml_files,
                    "other_files": inv.other_files,
                    "all_imports": inv.all_imports,
                    "all_endpoints": inv.all_endpoints,
                    "ports_detected": list(inv.ports_detected),
                    "agent_references": list(inv.agent_references),
                    "has_main": inv.has_main,
                    "has_requirements": inv.has_requirements,
                    "has_dockerfile": inv.has_dockerfile,
                    "has_config": inv.has_config,
                    "violations": inv.violations,
                    "files": [asdict(f) for f in inv.files],
                }
                for agent_id, inv in report.agents.items()
            },
            "global_violations": report.global_violations,
        }

        # Write with stable ordering
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, sort_keys=True)

        print(f"\nDiscovery report written to: {output_path}", file=sys.stderr)


# ============================================================================
# CLI
# ============================================================================


def main():
    """Main entry point."""
    # Determine project root (script is in scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    baseline_path = project_root / "system_baseline.yaml"
    output_path = project_root / "artifacts" / "agent_inventory.json"

    print("=== DETERMINISTIC AGENT DISCOVERY ===", file=sys.stderr)
    print(f"Project root: {project_root}", file=sys.stderr)
    print(f"Baseline: {baseline_path}", file=sys.stderr)
    print(f"Output: {output_path}", file=sys.stderr)
    print("", file=sys.stderr)

    # Run discovery
    engine = DiscoveryEngine(project_root, baseline_path)
    report = engine.discover()

    # Write report
    engine.write_report(report, output_path)

    # Print summary
    print("\n=== DISCOVERY SUMMARY ===", file=sys.stderr)
    print(f"Total agents: {report.summary['total_agents']}", file=sys.stderr)
    print(f"Agents scanned: {report.summary['agents_scanned']}", file=sys.stderr)
    print(f"Total files: {report.summary['total_files']}", file=sys.stderr)
    print(f"Total violations: {report.summary['total_violations']}", file=sys.stderr)

    # Print violations
    if report.global_violations:
        print("\n=== VIOLATIONS ===", file=sys.stderr)
        for violation in report.global_violations:
            print(f"  - {violation}", file=sys.stderr)

        print(f"\nERROR: Discovery failed with {len(report.global_violations)} violations", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n✓ Discovery completed successfully with no violations", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
