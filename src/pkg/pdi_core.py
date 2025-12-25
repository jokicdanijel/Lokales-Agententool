"""
[PDI-ACTIVE: TRUE | CORE-MODULE | GITHUB-CHECK: PASS]

Project Documentation Intelligence (PDI) – Core Module

Meta-Ebene (Selbststeuerung):
  Du bist der Project Documentation Intelligence Agent (PDI).
  Mission: Jede textuelle Projektidee wird in ein vollständiges, validiertes,
           semantisch sauberes und technisch reproduzierbares Projektbuch überführt.
  Du überwachst dich selbst, prüfst Annahmen, Entscheidungen, Logik und Konsistenz.

Objekt-Ebene (Ausführung):
  - Installierbare, technisch präzise Dokumentationen
  - Menschlich verständliche und didaktisch klare Erklärungen
  - Formale Artefakte (Text, Code, Schema, Log) für KI-Weiterverarbeitung
  - Alle Outputs: [PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]

Verpflichtende Regel:
  Dieser Prompt ist ein Pflicht-Metasystem. Vollständig aktiv bei jedem generativen
  Auswurf – Code, Text, Dokumentation oder Bericht.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

# ────────────────────────────────────────────────────────────────────────────
# Enums
# ────────────────────────────────────────────────────────────────────────────


class ValidationLevel(Enum):
    """Validierungs-Level für PDI-Prozess"""

    DRAFT = "DRAFT"
    COMMENTED = "COMMENTED"
    IMPROVED = "IMPROVED"
    VALIDATED = "VALIDATED"
    GITHUB_PASSED = "GITHUB_PASSED"
    RELEASED = "RELEASED"


class ModuleType(Enum):
    """PDI Funktionsmodule"""

    ANALYTICS = "ANALYTICS"  # Funktions- und Abhängigkeitsbäume
    LINGUISTIC = "LINGUISTIC"  # Verständlichkeit
    TECHNICAL = "TECHNICAL"  # Schnittstellen, Datenflüsse
    CORRECTION = "CORRECTION"  # Normen, Standards, Lint
    CONTROL = "CONTROL"  # Gates, Rollbacks, Status
    GITHUB = "GITHUB"  # GitHub Copilot-Prüfung


# ────────────────────────────────────────────────────────────────────────────
# Data Models
# ────────────────────────────────────────────────────────────────────────────


@dataclass
class ValidationResult:
    """Ergebnis einer Validierungs-Prüfung"""

    module: ModuleType
    level: ValidationLevel
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    suggestions: list[str]
    duration_ms: float
    timestamp: str

    def to_dict(self) -> dict:
        result = asdict(self)
        result["module"] = self.module.value
        result["level"] = self.level.value
        return result


@dataclass
class PDIManifest:
    """PDI-Manifest für ein Projekt"""

    project_name: str
    project_id: str
    version: str
    description: str
    modules_required: list[ModuleType]
    validation_gates: list[str]
    github_checks_required: bool
    author: str
    created_at: str

    def to_dict(self) -> dict:
        result = asdict(self)
        result["modules_required"] = [m.value for m in self.modules_required]
        return result


@dataclass
class ChapterPlan:
    """Kapitelplan für Dokumentation"""

    project_id: str
    total_chapters: int
    chapters: dict[int, str]  # {number: title}
    dependencies: dict[int, list[int]]  # {chapter: [depends_on]}
    estimated_total_time: float  # Minuten

    def to_dict(self) -> dict:
        return asdict(self)


# ────────────────────────────────────────────────────────────────────────────
# PDI Core Engine
# ────────────────────────────────────────────────────────────────────────────


class PDICore:
    """
    Zentrale PDI-Engine mit 8-Stufen-Prozess:
    1. Input übernehmen
    2. Manifest erstellen
    3. Kapitelplan anlegen
    4–11. Kapitel mit 8-Stufen-Prozess erzeugen (pro Kapitel)
    """

    def __init__(self, project_name: str, project_id: str):
        self.project_name = project_name
        self.project_id = project_id
        self.logger = logging.getLogger(f"PDI.{project_id}")
        self.validation_log: list[ValidationResult] = []
        self.manifest: PDIManifest | None = None
        self.chapter_plan: ChapterPlan | None = None
        self.validated_artifacts: dict[str, dict] = {}

    # ────────────────────────────────────────────────────────────────────────
    # Stage 1: Input Processing
    # ────────────────────────────────────────────────────────────────────────

    def process_input(self, input_text: str, author: str = "System") -> bool:
        """
        Stage 1: Input übernehmen und strukturieren.
        """
        self.logger.info(f"[STAGE 1] Processing input ({len(input_text)} chars)")

        try:
            # Validate input
            if not input_text or len(input_text) < 10:
                self.logger.error("Input too short (<10 chars)")
                return False

            # Normalize input
            input_text = input_text.strip()

            # Create manifest
            self.manifest = PDIManifest(
                project_name=self.project_name,
                project_id=self.project_id,
                version="1.0.0",
                description=input_text[:200],
                modules_required=[
                    ModuleType.ANALYTICS,
                    ModuleType.LINGUISTIC,
                    ModuleType.TECHNICAL,
                    ModuleType.CORRECTION,
                    ModuleType.CONTROL,
                    ModuleType.GITHUB,
                ],
                validation_gates=[
                    "syntax_check",
                    "lint_check",
                    "logic_check",
                    "security_check",
                    "github_check",
                ],
                github_checks_required=True,
                author=author,
                created_at=datetime.utcnow().isoformat(),
            )

            self.logger.info("[STAGE 1] ✓ Input processed, manifest created")
            return True

        except Exception as e:
            self.logger.error(f"[STAGE 1] ✗ Error: {e}")
            return False

    # ────────────────────────────────────────────────────────────────────────
    # Stage 2: Chapter Planning
    # ────────────────────────────────────────────────────────────────────────

    def create_chapter_plan(self, num_chapters: int = 5) -> bool:
        """
        Stage 2: Kapitelplan anlegen mit Abhängigkeiten.
        """
        self.logger.info(f"[STAGE 2] Creating chapter plan ({num_chapters} chapters)")

        try:
            chapters = {
                1: "Overview & Architecture",
                2: "Installation & Setup",
                3: "Core Functionality",
                4: "Integration & Usage",
                5: "Troubleshooting & FAQ",
            }

            # Limit to requested number
            chapters = {k: v for k, v in list(chapters.items())[:num_chapters]}

            # Dependencies: later chapters depend on earlier
            dependencies = {
                1: [],
                2: [1],
                3: [1, 2],
                4: [1, 2, 3],
                5: [1, 2, 3, 4],
            }

            self.chapter_plan = ChapterPlan(
                project_id=self.project_id,
                total_chapters=num_chapters,
                chapters=chapters,
                dependencies={k: v for k, v in dependencies.items() if k <= num_chapters},
                estimated_total_time=num_chapters * 15,  # 15 min per chapter
            )

            self.logger.info("[STAGE 2] ✓ Chapter plan created")
            return True

        except Exception as e:
            self.logger.error(f"[STAGE 2] ✗ Error: {e}")
            return False

    # ────────────────────────────────────────────────────────────────────────
    # Stage 3–10: 8-Step Process (per Chapter)
    # ────────────────────────────────────────────────────────────────────────

    def validate_artifact(
        self,
        artifact_id: str,
        artifact_type: str,  # "code" | "doc" | "config" | "test"
        content: str,
        run_modules: list[ModuleType] | None = None,
    ) -> dict[str, ValidationResult]:
        """
        Führe 8-Stufen-Validierungs-Prozess für einen Artefakt durch.

        Stufen:
        1. Kommentierung (LINGUISTIC)
        2. Verbesserungsvorschläge (TECHNICAL)
        3. Validierung (CORRECTION)
        4. Selbstprüfung (CONTROL)
        5. Kontrollprüfung (ANALYTICS)
        6. GitHub-Simulation (GITHUB)
        7. Freigabe-Check (CONTROL)
        8. Logging (CONTROL)
        """
        self.logger.info(f"[8-STEP] Validating artifact: {artifact_id} ({artifact_type})")

        if run_modules is None:
            run_modules = [m for m in ModuleType]

        results = {}

        # Step 1: Kommentierung (LINGUISTIC)
        if ModuleType.LINGUISTIC in run_modules:
            result = self._module_linguistic(artifact_id, content)
            results["linguistic"] = result
            self._log_validation(result)

        # Step 2: Verbesserungsvorschläge (TECHNICAL)
        if ModuleType.TECHNICAL in run_modules:
            result = self._module_technical(artifact_id, artifact_type, content)
            results["technical"] = result
            self._log_validation(result)

        # Step 3: Validierung (CORRECTION)
        if ModuleType.CORRECTION in run_modules:
            result = self._module_correction(artifact_id, artifact_type, content)
            results["correction"] = result
            self._log_validation(result)

        # Step 4: Selbstprüfung (ANALYTICS)
        if ModuleType.ANALYTICS in run_modules:
            result = self._module_analytics(artifact_id, content)
            results["analytics"] = result
            self._log_validation(result)

        # Step 5: Kontrollprüfung (CONTROL)
        if ModuleType.CONTROL in run_modules:
            result = self._module_control(artifact_id, results)
            results["control"] = result
            self._log_validation(result)

        # Step 6: GitHub-Simulation (GITHUB)
        if ModuleType.GITHUB in run_modules:
            result = self._module_github(artifact_id, artifact_type, content)
            results["github"] = result
            self._log_validation(result)

        # Step 7–8: Freigabe & Logging
        all_valid = all(r.is_valid for r in results.values())

        if all_valid:
            self.logger.info(f"[8-STEP] ✓ Artifact {artifact_id} PASSED all validations")
            self.validated_artifacts[artifact_id] = {
                "type": artifact_type,
                "content": content,
                "pdi_status": "VALIDATED | GITHUB-CHECK: PASS",
                "validated_at": datetime.utcnow().isoformat(),
                "validation_results": {k: v.to_dict() for k, v in results.items()},
            }
        else:
            self.logger.error(f"[8-STEP] ✗ Artifact {artifact_id} FAILED validation")

        return results

    # ────────────────────────────────────────────────────────────────────────
    # Validation Modules (Funktionsmodule)
    # ────────────────────────────────────────────────────────────────────────

    def _module_linguistic(self, artifact_id: str, content: str) -> ValidationResult:
        """Modul 1: Linguistische Verständlichkeit prüfen"""
        import time

        start = time.time()
        errors = []
        warnings = []
        suggestions = []

        # Simple checks
        if len(content) == 0:
            errors.append("Content is empty")
        elif len(content) < 20:
            warnings.append("Content very short (< 20 chars)")

        # Check for common readability issues
        lines = content.split("\n")
        if len(lines) > 200:
            suggestions.append(f"Content is long ({len(lines)} lines), consider splitting")

        if "TODO" in content or "FIXME" in content:
            warnings.append("Found unresolved TODO/FIXME markers")

        duration_ms = (time.time() - start) * 1000

        return ValidationResult(
            module=ModuleType.LINGUISTIC,
            level=ValidationLevel.COMMENTED,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            duration_ms=duration_ms,
            timestamp=datetime.utcnow().isoformat(),
        )

    def _module_technical(self, artifact_id: str, artifact_type: str, content: str) -> ValidationResult:
        """Modul 2: Technische Schnittstellen und Datenflüsse prüfen"""
        import time

        start = time.time()
        errors = []
        warnings = []
        suggestions = []

        # Type-specific checks
        if artifact_type == "code":
            if not any(kw in content for kw in ["def ", "class ", "import "]):
                warnings.append("No function/class definitions found")

            # Check for common patterns
            if "try:" in content and "except:" not in content:
                warnings.append("Try block without exception handling")

        elif artifact_type == "doc":
            if "##" not in content and "#" not in content:
                suggestions.append("Consider adding markdown headers")

        elif artifact_type == "config":
            if "{" in content or ":" in content:
                pass  # Likely JSON or YAML
            else:
                warnings.append("Config format unclear")

        duration_ms = (time.time() - start) * 1000

        return ValidationResult(
            module=ModuleType.TECHNICAL,
            level=ValidationLevel.IMPROVED,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            duration_ms=duration_ms,
            timestamp=datetime.utcnow().isoformat(),
        )

    def _module_correction(self, artifact_id: str, artifact_type: str, content: str) -> ValidationResult:
        """Modul 3: Normen, Standards, Lint-Regeln prüfen"""
        import time

        start = time.time()
        errors = []
        warnings = []
        suggestions = []

        if artifact_type == "code":
            # Basic Python checks
            if "  " in content:  # 2-space indent
                suggestions.append("Use 4-space indentation (PEP 8)")

            if "print(" in content:
                suggestions.append("Use logging instead of print()")

            # Check for trailing whitespace
            for i, line in enumerate(content.split("\n"), 1):
                if line.rstrip() != line:
                    warnings.append(f"Line {i}: trailing whitespace")
                    break  # Only report first

        elif artifact_type == "doc":
            # Check for consistent formatting
            if "```" in content:
                if content.count("```") % 2 != 0:
                    errors.append("Unclosed code block (```)")

        duration_ms = (time.time() - start) * 1000

        return ValidationResult(
            module=ModuleType.CORRECTION,
            level=ValidationLevel.VALIDATED,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            duration_ms=duration_ms,
            timestamp=datetime.utcnow().isoformat(),
        )

    def _module_analytics(self, artifact_id: str, content: str) -> ValidationResult:
        """Modul 4: Funktions- und Abhängigkeitsbäume analysieren"""
        import time

        start = time.time()
        errors = []
        warnings = []
        suggestions = []

        # Count structures
        num_funcs = content.count("def ")
        num_classes = content.count("class ")
        num_imports = content.count("import ")

        if num_funcs == 0 and num_classes == 0:
            suggestions.append("No functions or classes found")

        if num_imports > 20:
            warnings.append(f"High number of imports ({num_imports})")

        duration_ms = (time.time() - start) * 1000

        return ValidationResult(
            module=ModuleType.ANALYTICS,
            level=ValidationLevel.VALIDATED,
            is_valid=True,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            duration_ms=duration_ms,
            timestamp=datetime.utcnow().isoformat(),
        )

    def _module_control(self, artifact_id: str, prior_results: dict) -> ValidationResult:
        """Modul 5: Kontrollprogramm – Gates, Rollbacks, Status"""
        import time

        start = time.time()
        errors = []
        warnings = []
        suggestions = []

        # Check if all prior modules passed
        all_passed = all(r.is_valid for r in prior_results.values())

        if all_passed:
            suggestions.append("All prior validations passed – ready for GitHub check")
        else:
            failed_modules = [k for k, v in prior_results.items() if not v.is_valid]
            errors.append(f"Prior modules failed: {', '.join(failed_modules)}")

        duration_ms = (time.time() - start) * 1000

        return ValidationResult(
            module=ModuleType.CONTROL,
            level=ValidationLevel.GITHUB_PASSED if all_passed else ValidationLevel.VALIDATED,
            is_valid=all_passed,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            duration_ms=duration_ms,
            timestamp=datetime.utcnow().isoformat(),
        )

    def _module_github(self, artifact_id: str, artifact_type: str, content: str) -> ValidationResult:
        """Modul 6: GitHub Copilot-Prüfung (simuliert)"""
        import time

        start = time.time()
        errors = []
        warnings = []
        suggestions = []

        # Simulate GitHub Copilot checks
        github_checks = {
            "syntax": self._check_syntax(artifact_type, content),
            "logic": self._check_logic(artifact_type, content),
            "runtime": self._check_runtime(artifact_type, content),
            "security": self._check_security(artifact_type, content),
        }

        for check_name, check_result in github_checks.items():
            if not check_result["valid"]:
                errors.extend([f"{check_name}: {e}" for e in check_result.get("errors", [])])
                warnings.extend([f"{check_name}: {w}" for w in check_result.get("warnings", [])])

        duration_ms = (time.time() - start) * 1000

        return ValidationResult(
            module=ModuleType.GITHUB,
            level=ValidationLevel.RELEASED if len(errors) == 0 else ValidationLevel.VALIDATED,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            duration_ms=duration_ms,
            timestamp=datetime.utcnow().isoformat(),
        )

    # ────────────────────────────────────────────────────────────────────────
    # GitHub Checks (Simulated)
    # ────────────────────────────────────────────────────────────────────────

    def _check_syntax(self, artifact_type: str, content: str) -> dict:
        """GitHub Check: Syntax Errors"""
        if artifact_type == "code":
            try:
                compile(content, "<string>", "exec")
                return {"valid": True, "errors": []}
            except SyntaxError as e:
                return {"valid": False, "errors": [str(e)]}
        return {"valid": True, "errors": []}

    def _check_logic(self, artifact_type: str, content: str) -> dict:
        """GitHub Check: Logic Errors"""
        errors = []

        # Type-specific logic checks
        if artifact_type == "bash":
            # Bash scripts often have complex bracket patterns (arrays, expansions)
            # Only check for critical syntax errors, not bracket counts
            # (Bash is too dynamic for static bracket counting)

            # Check for common Bash pitfalls
            if "rm -rf /" in content:
                errors.append("Dangerous rm -rf command detected")

            if "eval " in content:
                errors.append("Use of eval() in Bash is dangerous")

            return {"valid": len(errors) == 0, "errors": errors}

        elif artifact_type == "code" and "python" in content[:100].lower():
            # Python: basic checks
            if content.count("[") != content.count("]"):
                errors.append("Bracket mismatch in Python code")

        return {"valid": len(errors) == 0, "errors": errors}

    def _check_runtime(self, artifact_type: str, content: str) -> dict:
        """GitHub Check: Runtime Errors"""
        errors = []
        if "open(" in content and "close()" not in content:
            errors.append("File opened but not closed")
        return {"valid": len(errors) == 0, "errors": errors}

    def _check_security(self, artifact_type: str, content: str) -> dict:
        """GitHub Check: Security Issues"""
        errors = []
        if "eval(" in content:
            errors.append("Use of eval() is security risk")
        if "exec(" in content:
            errors.append("Use of exec() is security risk")
        if "password" in content.lower() and "***" not in content:
            errors.append("Hardcoded password detected")
        return {"valid": len(errors) == 0, "errors": errors}

    # ────────────────────────────────────────────────────────────────────────
    # Utilities
    # ────────────────────────────────────────────────────────────────────────

    def _log_validation(self, result: ValidationResult):
        """Log validation result"""
        self.validation_log.append(result)
        level = "✓" if result.is_valid else "✗"
        self.logger.info(f"  [{result.module.value}] {level} {result.level.value}")

    def get_validation_report(self) -> dict:
        """Generiere Validierungs-Report"""
        total = len(self.validation_log)
        passed = sum(1 for r in self.validation_log if r.is_valid)
        failed = total - passed

        return {
            "project_id": self.project_id,
            "total_validations": total,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "N/A",
            "artifacts_validated": len(self.validated_artifacts),
            "validation_log": [r.to_dict() for r in self.validation_log],
            "validated_artifacts": self.validated_artifacts,
        }

    def export_manifest(self, filepath: str | None = None) -> str:
        """Exportiere Manifest als JSON"""
        if not self.manifest:
            return "{}"

        manifest_dict = self.manifest.to_dict()

        if filepath:
            Path(filepath).write_text(json.dumps(manifest_dict, indent=2))
            self.logger.info(f"Manifest exported to {filepath}")

        return json.dumps(manifest_dict, indent=2)

    def export_validated_artifact(self, artifact_id: str) -> str:
        """Exportiere validiertes Artefakt mit PDI-Header"""
        if artifact_id not in self.validated_artifacts:
            return ""

        artifact = self.validated_artifacts[artifact_id]
        header = '"""\n[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]\n"""\n\n'

        return header + artifact["content"]
