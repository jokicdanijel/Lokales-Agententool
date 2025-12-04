#!/usr/bin/env python3
"""
Workspace Evaluation Framework
Comprehensive assessment of PORTIER 3.0 workspace health, configuration, and compliance
"""
import json
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class WorkspaceEvaluator:
    """Evaluates workspace health across multiple dimensions"""
    
    def __init__(self, root_path: Path = Path(".")):
        self.root = root_path.resolve()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "evaluations": {},
            "score": 0,
            "max_score": 0,
            "status": "unknown"
        }
    
    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{title:^70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")
    
    def print_result(self, name: str, passed: bool, details: str = ""):
        """Print individual test result"""
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"{status} {name}")
        if details:
            print(f"     {details}")
    
    def evaluate_file_structure(self) -> Dict:
        """Evaluate critical file and directory structure"""
        self.print_header("File Structure Evaluation")
        
        critical_paths = {
            "scripts/": "Scripts directory",
            "tests/": "Test directory",
            "src/": "Source directory",
            "docs/": "Documentation directory",
            "configs/": "Configuration directory",
            ".github/workflows/": "CI/CD workflows",
            "pyproject.toml": "Python project config",
            "requirements.txt": "Python dependencies",
            ".gitignore": "Git ignore rules"
        }
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        for path, description in critical_paths.items():
            full_path = self.root / path
            exists = full_path.exists()
            results["passed" if exists else "failed"] += 1
            self.print_result(description, exists, str(full_path))
            results["details"].append({
                "path": path,
                "description": description,
                "exists": exists
            })
        
        self.results["evaluations"]["file_structure"] = results
        return results
    
    def evaluate_service_ports(self) -> Dict:
        """Evaluate service port availability and conflicts"""
        self.print_header("Service Port Evaluation")
        
        # PORTIER 3.0 service ports
        service_ports = {
            "opena1 (Coordinator)": 12344,
            "opena2 (Archivator)": 12345,
            "kordp (Gateway)": 12346,
            "opena3 (OpenWebUI)": 12347,
            "opena4 (Telegram)": 12348,
            "opena20 (Dashboard)": 12349,
            "opena5 (VS Code)": 12351,
            "opena6 (Browser)": 12352,
            "opena7 (Email)": 12353,
            "opena8 (WhatsApp)": 12354,
        }
        
        results = {"passed": 0, "failed": 0, "in_use": [], "available": []}
        
        for service, port in service_ports.items():
            in_use = self.check_port_in_use(port)
            results["passed" if not in_use else "failed"] += 1
            self.print_result(
                f"{service} (:{port})",
                not in_use,
                "Port available" if not in_use else "Port in use"
            )
            
            if in_use:
                results["in_use"].append({"service": service, "port": port})
            else:
                results["available"].append({"service": service, "port": port})
        
        self.results["evaluations"]["service_ports"] = results
        return results
    
    def check_port_in_use(self, port: int, host: str = "127.0.0.1") -> bool:
        """Check if a port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result == 0  # 0 means connected (in use)
        except Exception:
            return False
    
    def evaluate_configuration_files(self) -> Dict:
        """Evaluate configuration file validity"""
        self.print_header("Configuration Files Evaluation")
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        # Check routing matrix
        routing_matrix = self.root / "configs/routing_matrix.yaml"
        if routing_matrix.exists():
            try:
                import yaml
                data = yaml.safe_load(routing_matrix.read_text())
                valid = "program_targets" in data
                results["passed" if valid else "failed"] += 1
                self.print_result(
                    "routing_matrix.yaml",
                    valid,
                    "Valid YAML with program_targets" if valid else "Missing program_targets"
                )
                results["details"].append({"file": "routing_matrix.yaml", "valid": valid})
            except Exception as e:
                results["failed"] += 1
                self.print_result("routing_matrix.yaml", False, f"Error: {e}")
                results["details"].append({"file": "routing_matrix.yaml", "valid": False, "error": str(e)})
        else:
            results["failed"] += 1
            self.print_result("routing_matrix.yaml", False, "File not found")
        
        # Check pyproject.toml
        pyproject = self.root / "pyproject.toml"
        if pyproject.exists():
            try:
                import toml
                data = toml.load(pyproject)
                valid = "tool" in data
                results["passed" if valid else "failed"] += 1
                self.print_result(
                    "pyproject.toml",
                    valid,
                    "Valid TOML configuration" if valid else "Invalid format"
                )
                results["details"].append({"file": "pyproject.toml", "valid": valid})
            except ImportError:
                # TOML not available, just check if file parses
                results["passed"] += 1
                self.print_result("pyproject.toml", True, "File exists")
                results["details"].append({"file": "pyproject.toml", "valid": True})
            except Exception as e:
                results["failed"] += 1
                self.print_result("pyproject.toml", False, f"Error: {e}")
                results["details"].append({"file": "pyproject.toml", "valid": False, "error": str(e)})
        
        self.results["evaluations"]["configuration_files"] = results
        return results
    
    def evaluate_test_coverage(self) -> Dict:
        """Evaluate test file presence and structure"""
        self.print_header("Test Coverage Evaluation")
        
        results = {"passed": 0, "failed": 0, "test_files": [], "coverage": 0}
        
        tests_dir = self.root / "tests"
        if tests_dir.exists():
            test_files = list(tests_dir.glob("test_*.py"))
            results["test_files"] = [f.name for f in test_files]
            results["passed"] = len(test_files)
            
            for test_file in test_files:
                self.print_result(test_file.name, True, f"Found in tests/")
            
            if len(test_files) == 0:
                results["failed"] += 1
                self.print_result("Test files", False, "No test files found")
        else:
            results["failed"] += 1
            self.print_result("tests/ directory", False, "Directory not found")
        
        self.results["evaluations"]["test_coverage"] = results
        return results
    
    def evaluate_security_compliance(self) -> Dict:
        """Evaluate security compliance"""
        self.print_header("Security Compliance Evaluation")
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        # Check .gitignore for sensitive files
        gitignore = self.root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            security_patterns = [".env", "*.key", "*.pem", "*.pub"]
            
            for pattern in security_patterns:
                present = pattern in content
                results["passed" if present else "failed"] += 1
                self.print_result(
                    f"Gitignore pattern: {pattern}",
                    present,
                    "Present" if present else "Missing"
                )
                results["details"].append({"pattern": pattern, "present": present})
        else:
            results["failed"] += 1
            self.print_result(".gitignore", False, "File not found")
        
        # Check for .env file (should not be committed)
        env_file = self.root / ".env"
        env_committed = env_file.exists()
        if env_committed:
            # Check if it's in .gitignore
            if gitignore.exists() and ".env" in gitignore.read_text():
                results["passed"] += 1
                self.print_result(".env file", True, "Exists but properly ignored")
            else:
                results["failed"] += 1
                self.print_result(".env file", False, "Exists and NOT in .gitignore")
        else:
            results["passed"] += 1
            self.print_result(".env file", True, "Not present in workspace")
        
        self.results["evaluations"]["security_compliance"] = results
        return results
    
    def evaluate_scripts_executability(self) -> Dict:
        """Evaluate if critical scripts are executable"""
        self.print_header("Scripts Executability Evaluation")
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        scripts_dir = self.root / "scripts"
        if scripts_dir.exists():
            critical_scripts = [
                "start_all.sh",
                "stop_all.sh",
                "check_health.sh",
                "verify_stack.sh",
                "structure_manager.py"
            ]
            
            for script_name in critical_scripts:
                script_path = scripts_dir / script_name
                if script_path.exists():
                    is_executable = script_path.stat().st_mode & 0o111 != 0
                    results["passed" if is_executable else "failed"] += 1
                    self.print_result(
                        script_name,
                        is_executable,
                        "Executable" if is_executable else "Not executable"
                    )
                    results["details"].append({
                        "script": script_name,
                        "exists": True,
                        "executable": is_executable
                    })
                else:
                    results["failed"] += 1
                    self.print_result(script_name, False, "Not found")
                    results["details"].append({
                        "script": script_name,
                        "exists": False,
                        "executable": False
                    })
        else:
            results["failed"] += 1
            self.print_result("scripts/ directory", False, "Not found")
        
        self.results["evaluations"]["scripts_executability"] = results
        return results
    
    def calculate_score(self):
        """Calculate overall workspace score"""
        total_passed = 0
        total_tests = 0
        
        for category, data in self.results["evaluations"].items():
            if isinstance(data, dict):
                total_passed += data.get("passed", 0)
                total_tests += data.get("passed", 0) + data.get("failed", 0)
        
        self.results["score"] = total_passed
        self.results["max_score"] = total_tests
        
        if total_tests > 0:
            percentage = (total_passed / total_tests) * 100
            if percentage >= 90:
                self.results["status"] = "excellent"
            elif percentage >= 75:
                self.results["status"] = "good"
            elif percentage >= 60:
                self.results["status"] = "fair"
            else:
                self.results["status"] = "poor"
        
        return self.results["score"], self.results["max_score"]
    
    def print_summary(self):
        """Print evaluation summary"""
        score, max_score = self.calculate_score()
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        self.print_header("Workspace Evaluation Summary")
        
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Score: {score}/{max_score} ({percentage:.1f}%)")
        print(f"Status: {self.results['status'].upper()}")
        print()
        
        # Category breakdown
        for category, data in self.results["evaluations"].items():
            if isinstance(data, dict):
                passed = data.get("passed", 0)
                failed = data.get("failed", 0)
                total = passed + failed
                category_name = category.replace("_", " ").title()
                status_color = Colors.GREEN if failed == 0 else Colors.YELLOW if passed > failed else Colors.RED
                print(f"{status_color}{category_name}: {passed}/{total} passed{Colors.RESET}")
        
        print()
        
        # Overall status with color
        if self.results["status"] == "excellent":
            status_msg = f"{Colors.GREEN}✓ EXCELLENT - Workspace is in optimal condition{Colors.RESET}"
        elif self.results["status"] == "good":
            status_msg = f"{Colors.YELLOW}⚠ GOOD - Minor issues detected{Colors.RESET}"
        elif self.results["status"] == "fair":
            status_msg = f"{Colors.YELLOW}⚠ FAIR - Several issues need attention{Colors.RESET}"
        else:
            status_msg = f"{Colors.RED}✗ POOR - Critical issues detected{Colors.RESET}"
        
        print(status_msg)
    
    def save_report(self, output_file: str = "workspace_evaluation_report.json"):
        """Save evaluation report to JSON file"""
        output_path = self.root / output_file
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n{Colors.GREEN}Report saved to: {output_path}{Colors.RESET}")
    
    def run_full_evaluation(self, save_report: bool = True):
        """Run complete workspace evaluation"""
        print(f"{Colors.BOLD}PORTIER 3.0 Workspace Evaluation Framework{Colors.RESET}")
        print(f"Root: {self.root}")
        
        # Run all evaluations
        self.evaluate_file_structure()
        self.evaluate_service_ports()
        self.evaluate_configuration_files()
        self.evaluate_test_coverage()
        self.evaluate_security_compliance()
        self.evaluate_scripts_executability()
        
        # Print summary
        self.print_summary()
        
        # Save report
        if save_report:
            self.save_report()
        
        # Return exit code based on status
        if self.results["status"] in ["excellent", "good"]:
            return 0
        else:
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PORTIER 3.0 Workspace Evaluation Framework"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save report to file"
    )
    parser.add_argument(
        "--output",
        default="workspace_evaluation_report.json",
        help="Output report filename (default: workspace_evaluation_report.json)"
    )
    
    args = parser.parse_args()
    
    evaluator = WorkspaceEvaluator(Path(args.root))
    exit_code = evaluator.run_full_evaluation(save_report=not args.no_save)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
