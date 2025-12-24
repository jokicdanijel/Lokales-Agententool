#!/usr/bin/env python3
"""
ELION Hyper-Dashboard – Preflight Check System
Vollständige Validierung vor jedem Build/Deploy

Principles:
- Ports sind Gesetze (unveränderlich)
- Agentennamen sind Canonical IDs
- Ordnerstruktur = Source of Truth
- HTML wird aus Analyse generiert
- KEINE Annahmen, KEINE Abkürzungen
- Fail fast bei ANY Abweichung

Exit Codes:
- 0: All checks passed
- 1: Critical failure (blocks deployment)
"""

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ============================================================================
# CANONICAL AGENT REGISTRY (IMMUTABLE)
# ============================================================================

CANONICAL_AGENTS = {
    "opena1": 12344,
    "opena2": 12345,
    "opena3": 12347,
    "opena4": 12346,
    "opena5": 12351,
    "opena6": 12352,
    "opena7": 12350,
    "opena8": 12354,
    "opena9": 12355,
    "opena10": 12356,
    "opena11": 12357,
    "opena12": 12358,
    "opena13": 12359,
    "opena14": 12360,
    "opena15": 12361,
    "opena16": 12362,
    "opena17": 12366,
    "opena18": 12363,
    "opena19": 12367,
    "opena20": 12349,
    "opena21": 12368,
}

FORBIDDEN_PORTS = [8080, 3000]

# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class AgentCapability:
    """Agent capability manifest"""

    agent_id: str
    port: int
    folder: str

    # Discovered capabilities
    has_main: bool = False
    has_requirements: bool = False
    has_readme: bool = False
    has_dockerfile: bool = False

    features: dict[str, bool] = field(default_factory=dict)
    endpoints: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    # Validation
    port_matches: bool = False
    folder_exists: bool = False
    no_forbidden_ports: bool = True


@dataclass
class PreflightResult:
    """Complete preflight check result"""

    success: bool
    timestamp: str

    agents_checked: int = 0
    agents_passed: int = 0
    agents_failed: int = 0

    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    capabilities: list[AgentCapability] = field(default_factory=list)


# ============================================================================
# STEP 1: AGENT FOLDER FULL SCAN
# ============================================================================


class AgentScanner:
    """Complete agent folder scanner"""

    def __init__(self, root: Path):
        self.root = root
        self.violations = []
        self.warnings = []

    def scan_all_agents(self) -> list[AgentCapability]:
        """Scan all agent folders"""
        print("=" * 80)
        print("STEP 1: AGENT FOLDER FULL SCAN")
        print("=" * 80)

        capabilities = []

        for agent_id, canonical_port in CANONICAL_AGENTS.items():
            print(f"\n🔍 Scanning {agent_id} (Port {canonical_port})...")

            capability = self._scan_agent(agent_id, canonical_port)
            capabilities.append(capability)

            self._print_agent_status(capability)

        print(f"\n✅ Scanned {len(capabilities)}/21 agents")
        return capabilities

    def _scan_agent(self, agent_id: str, canonical_port: int) -> AgentCapability:
        """Scan single agent folder"""
        # Find folder
        folder = self._find_agent_folder(agent_id)

        capability = AgentCapability(agent_id=agent_id, port=canonical_port, folder=str(folder) if folder else "")

        if not folder:
            self.violations.append(f"❌ {agent_id}: Folder not found")
            return capability

        capability.folder_exists = True

        # Check files
        capability.has_main = self._has_main_file(folder)
        capability.has_requirements = (folder / "requirements.txt").exists()
        capability.has_readme = self._has_readme(folder)
        capability.has_dockerfile = (folder / "Dockerfile").exists()

        # Extract capabilities
        if capability.has_main:
            main_file = self._find_main_file(folder)
            if main_file:
                capability.endpoints = self._extract_endpoints(main_file)
                declared_port = self._extract_port(main_file)

                # Validate port
                if declared_port and declared_port != canonical_port:
                    self.violations.append(
                        f"❌ {agent_id}: Port mismatch! " f"Canonical={canonical_port}, Declared={declared_port}"
                    )
                    capability.port_matches = False
                else:
                    capability.port_matches = True

                # Check for forbidden ports
                all_ports = self._extract_all_ports(main_file)
                forbidden_found = set(all_ports) & set(FORBIDDEN_PORTS)
                if forbidden_found:
                    self.violations.append(f"❌ {agent_id}: Forbidden ports found: {forbidden_found}")
                    capability.no_forbidden_ports = False

        # Extract dependencies
        if capability.has_requirements:
            capability.dependencies = self._extract_dependencies(folder / "requirements.txt")

        # Extract features
        capability.features = self._detect_features(folder)

        return capability

    def _find_agent_folder(self, agent_id: str) -> Path | None:
        """Find agent folder by ID"""
        # Pattern: *openaX* or openaX_*
        patterns = [f"*{agent_id}*", f"{agent_id}_*", f"*_{agent_id}"]

        for pattern in patterns:
            matches = list(self.root.glob(pattern))
            if matches:
                # Return first directory match
                for match in matches:
                    if match.is_dir():
                        return match

        return None

    def _has_main_file(self, folder: Path) -> bool:
        """Check if main file exists"""
        candidates = ["main.py", "app.py", "server.py", "__init__.py"]
        return any((folder / name).exists() for name in candidates)

    def _find_main_file(self, folder: Path) -> Path | None:
        """Find main file"""
        candidates = ["main.py", "app.py", "server.py", "__init__.py"]
        for name in candidates:
            path = folder / name
            if path.exists():
                return path
        return None

    def _has_readme(self, folder: Path) -> bool:
        """Check if README exists"""
        return any((folder / name).exists() for name in ["README.md", "README.rst", "README.txt"])

    def _extract_endpoints(self, main_file: Path) -> list[str]:
        """Extract API endpoints from main file"""
        try:
            content = main_file.read_text()

            endpoints = []

            # FastAPI patterns
            fastapi_pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)'
            for match in re.findall(fastapi_pattern, content):
                method, path = match
                endpoints.append(f"{method.upper()} {path}")

            # Flask patterns
            flask_pattern = r'@app\.route\(["\']([^"\']+)'
            for path in re.findall(flask_pattern, content):
                endpoints.append(f"GET {path}")

            return sorted(set(endpoints))

        except Exception as e:
            self.warnings.append(f"⚠️ Could not extract endpoints from {main_file}: {e}")
            return []

    def _extract_port(self, main_file: Path) -> int | None:
        """Extract declared port from main file"""
        try:
            content = main_file.read_text()

            # Pattern: PORT = 12345 or port=12345
            port_patterns = [
                r"PORT\s*=\s*(\d+)",
                r"port\s*=\s*(\d+)",
                r"uvicorn\.run\([^,]*,\s*port\s*=\s*(\d+)",
            ]

            for pattern in port_patterns:
                match = re.search(pattern, content)
                if match:
                    return int(match.group(1))

            return None

        except Exception:
            return None

    def _extract_all_ports(self, main_file: Path) -> list[int]:
        """Extract all port numbers from file"""
        try:
            content = main_file.read_text()
            # Match port numbers in typical range
            port_pattern = r"\b(12[3-4]\d{2}|8080|3000)\b"
            ports = [int(p) for p in re.findall(port_pattern, content)]
            return list(set(ports))
        except Exception:
            return []

    def _extract_dependencies(self, req_file: Path) -> list[str]:
        """Extract dependencies from requirements.txt"""
        try:
            deps = []
            for line in req_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    pkg = re.split(r"[=<>!]", line)[0].strip()
                    if pkg:
                        deps.append(pkg)
            return sorted(deps)
        except Exception:
            return []

    def _detect_features(self, folder: Path) -> dict[str, bool]:
        """Detect agent features"""
        features = {"status": False, "logs": False, "settings": False, "workflows": False, "vault": False}

        main_file = self._find_main_file(folder)
        if not main_file:
            return features

        try:
            content = main_file.read_text().lower()

            features["status"] = "/health" in content or "/status" in content
            features["logs"] = "/logs" in content or "logging" in content
            features["settings"] = "/settings" in content or "/config" in content
            features["workflows"] = "workflow" in content
            features["vault"] = "vault" in content or "encrypt" in content

        except Exception:
            pass

        return features

    def _print_agent_status(self, capability: AgentCapability):
        """Print agent scan status"""
        status_icon = "✅" if capability.folder_exists and capability.has_main else "❌"

        files = []
        if capability.has_main:
            files.append("main")
        if capability.has_requirements:
            files.append(f"deps({len(capability.dependencies)})")
        if capability.has_readme:
            files.append("readme")

        endpoints_str = f", {len(capability.endpoints)} endpoints" if capability.endpoints else ""

        print(
            f"{status_icon} {capability.agent_id:8} | Port {capability.port} | {', '.join(files) if files else 'missing'}{endpoints_str}"
        )


# ============================================================================
# STEP 2: CAPABILITY EXTRACTION & MANIFEST GENERATION
# ============================================================================


class CapabilityExtractor:
    """Extract and generate capability manifests"""

    @staticmethod
    def generate_manifests(capabilities: list[AgentCapability], output_path: Path):
        """Generate capability manifests JSON"""
        print("\n" + "=" * 80)
        print("STEP 2: CAPABILITY EXTRACTION & MANIFEST GENERATION")
        print("=" * 80)

        manifests = {"generated_at": datetime.now(UTC).isoformat(), "agents": {}}

        for cap in capabilities:
            manifests["agents"][cap.agent_id] = {
                "port": cap.port,
                "folder": cap.folder,
                "features": cap.features,
                "endpoints": cap.endpoints,
                "dependencies": cap.dependencies[:10],  # Top 10
                "has_main": cap.has_main,
                "has_requirements": cap.has_requirements,
                "has_readme": cap.has_readme,
            }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(manifests, f, indent=2)

        print(f"✅ Capability manifests generated: {output_path}")
        print(f"   Agents documented: {len(manifests['agents'])}")


# ============================================================================
# MAIN PREFLIGHT ORCHESTRATOR
# ============================================================================


class PreflightOrchestrator:
    """Main preflight orchestration"""

    def __init__(self, root: Path):
        self.root = root
        self.result = PreflightResult(success=False, timestamp=datetime.now(UTC).isoformat())

    def run_all_checks(self) -> PreflightResult:
        """Run all preflight checks"""
        print("\n" + "=" * 80)
        print("🚀 ELION HYPER-DASHBOARD – PREFLIGHT CHECK")
        print("=" * 80)
        print(f"Root: {self.root}")
        print(f"Canonical Agents: {len(CANONICAL_AGENTS)}")
        print()

        # STEP 1: Agent scan
        scanner = AgentScanner(self.root)
        capabilities = scanner.scan_all_agents()

        self.result.capabilities = capabilities
        self.result.agents_checked = len(capabilities)
        self.result.agents_passed = sum(1 for c in capabilities if c.folder_exists and c.has_main)
        self.result.agents_failed = self.result.agents_checked - self.result.agents_passed
        self.result.violations.extend(scanner.violations)
        self.result.warnings.extend(scanner.warnings)

        # STEP 2: Generate manifests
        manifest_path = self.root / "artifacts" / "agent_capabilities.json"
        CapabilityExtractor.generate_manifests(capabilities, manifest_path)

        # Final verdict
        self.result.success = len(self.result.violations) == 0

        self._print_summary()

        return self.result

    def _print_summary(self):
        """Print preflight summary"""
        print("\n" + "=" * 80)
        print("PREFLIGHT SUMMARY")
        print("=" * 80)

        print("\n📊 Agents:")
        print(f"   Checked: {self.result.agents_checked}")
        print(f"   Passed:  {self.result.agents_passed}")
        print(f"   Failed:  {self.result.agents_failed}")

        if self.result.violations:
            print(f"\n❌ VIOLATIONS ({len(self.result.violations)}):")
            for violation in self.result.violations:
                print(f"   {violation}")

        if self.result.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.result.warnings)}):")
            for warning in self.result.warnings[:10]:  # Show max 10
                print(f"   {warning}")

        print("\n" + "=" * 80)
        if self.result.success:
            print("✅ PREFLIGHT PASSED – System ready for deployment")
        else:
            print("❌ PREFLIGHT FAILED – Fix violations before proceeding")
        print("=" * 80)


# ============================================================================
# MAIN
# ============================================================================


def main():
    root = Path(__file__).parent.parent

    orchestrator = PreflightOrchestrator(root)
    result = orchestrator.run_all_checks()

    # Save result
    output_path = root / "artifacts" / "preflight_result.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(asdict(result), f, indent=2)

    print(f"\n📄 Preflight result saved: {output_path}")

    # Exit with appropriate code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
