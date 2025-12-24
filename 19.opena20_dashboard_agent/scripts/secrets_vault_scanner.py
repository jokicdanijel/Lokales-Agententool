#!/usr/bin/env python3
"""
Secrets & Vault Policy Scanner
================================
Detects cleartext secrets outside opena11 vault scope.

FAIL-HARD RULES:
1. NO cleartext secrets outside opena11 folder
2. NO API keys, tokens, private keys in non-vault code
3. NO plaintext/decrypted endpoints outside opena11
4. Vault endpoints ONLY exist under opena11

DETECTION PATTERNS:
- API keys (api_key, apikey, API_KEY)
- Tokens (token, access_token, auth_token)
- Private keys (BEGIN PRIVATE KEY, BEGIN RSA PRIVATE KEY)
- OAuth secrets (client_secret, oauth_secret)
- SMTP passwords (smtp_password, email_password)
- Webhook secrets (webhook_secret)
- Bearer tokens
- Database passwords

EXIT CODES:
- 0: No security violations
- 1: Secrets found outside vault (CI MUST break)

Usage:
  python3 scripts/secrets_vault_scanner.py
"""

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

# ============================================================================
# SECRET PATTERNS
# ============================================================================

SECRET_PATTERNS = [
    # API Keys
    (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([^"\']{8,})["\']', "API Key"),
    (r'(?i)API[_-]?KEY\s*=\s*["\']([^"\']{8,})["\']', "API Key (env)"),
    # Tokens
    (r'(?i)(access[_-]?token|auth[_-]?token|token)\s*[:=]\s*["\']([^"\']{16,})["\']', "Token"),
    (r"(?i)bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", "Bearer Token"),
    # Private Keys
    (r"-----BEGIN (?:RSA )?PRIVATE KEY-----", "Private Key"),
    (r"-----BEGIN CERTIFICATE-----", "Certificate"),
    # OAuth
    (r'(?i)(client[_-]?secret|oauth[_-]?secret)\s*[:=]\s*["\']([^"\']{8,})["\']', "OAuth Secret"),
    # SMTP
    (r'(?i)(smtp[_-]?password|email[_-]?password)\s*[:=]\s*["\']([^"\']+)["\']', "SMTP Password"),
    # Webhook
    (r'(?i)webhook[_-]?secret\s*[:=]\s*["\']([^"\']{8,})["\']', "Webhook Secret"),
    # Database
    (r'(?i)(db[_-]?password|database[_-]?password)\s*[:=]\s*["\']([^"\']+)["\']', "Database Password"),
    # Generic secrets
    (r'(?i)secret[_-]?key\s*[:=]\s*["\']([^"\']{8,})["\']', "Secret Key"),
    (r'(?i)password\s*[:=]\s*["\'](?!.*\$\{)[^"\']{4,}["\']', "Password"),
]

VAULT_VIOLATION_PATTERNS = [
    (r"(?i)return.*plaintext", "Returns plaintext"),
    (r"(?i)decrypted[_-]?payload", "Exposes decrypted payload"),
    (r"(?i)get.*secret.*cleartext", "Gets secret in cleartext"),
]


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class SecretDetection:
    """A detected secret"""

    file: str
    line_number: int
    pattern_type: str
    context: str  # Surrounding code
    severity: str = "critical"


@dataclass
class VaultViolation:
    """A vault policy violation"""

    file: str
    line_number: int
    violation_type: str
    context: str
    severity: str = "critical"


@dataclass
class ScanResult:
    """Overall scan result"""

    timestamp: str
    passed: bool
    files_scanned: int = 0
    secrets_detected: list[SecretDetection] = field(default_factory=list)
    vault_violations: list[VaultViolation] = field(default_factory=list)


# ============================================================================
# SCANNER
# ============================================================================


class SecretsVaultScanner:
    """Scanner for secrets and vault policy compliance"""

    VAULT_FOLDER: ClassVar[str] = "10.opena11_unlock"
    EXCLUDED_PATTERNS: ClassVar[set[str]] = {
        ".venv/",
        "node_modules/",
        "__pycache__/",
        ".git/",
        ".mypy_cache/",
        ".pytest_cache/",
        "build/",
        "dist/",
    }
    SCAN_EXTENSIONS: ClassVar[set[str]] = {".py", ".js", ".ts", ".json", ".yaml", ".yml", ".env", ".txt", ".md"}

    def __init__(self, project_root: Path):
        self.root = project_root
        self.result = ScanResult(timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"), passed=False)

        # Compile patterns
        self.secret_patterns = [(re.compile(p), name) for p, name in SECRET_PATTERNS]
        self.vault_patterns = [(re.compile(p), name) for p, name in VAULT_VIOLATION_PATTERNS]

    def should_scan_file(self, file_path: Path) -> bool:
        """Determine if file should be scanned"""
        # Check extension
        if file_path.suffix not in self.SCAN_EXTENSIONS:
            return False

        # Check excluded patterns
        path_str = str(file_path)
        for pattern in self.EXCLUDED_PATTERNS:
            if pattern in path_str:
                return False

        return True

    def is_vault_file(self, file_path: Path) -> bool:
        """Check if file is in vault scope (opena11)"""
        return self.VAULT_FOLDER in str(file_path)

    def scan_file(self, file_path: Path):
        """Scan single file for secrets"""
        is_vault = self.is_vault_file(file_path)

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return

        rel_path = str(file_path.relative_to(self.root))

        for line_num, line in enumerate(lines, 1):
            # Secret detection (skip if in vault)
            if not is_vault:
                for pattern, pattern_name in self.secret_patterns:
                    if pattern.search(line):
                        self.result.secrets_detected.append(
                            SecretDetection(
                                file=rel_path,
                                line_number=line_num,
                                pattern_type=pattern_name,
                                context=line.strip()[:100],
                            )
                        )

            # Vault violation detection (check everywhere except vault)
            if not is_vault:
                for pattern, violation_name in self.vault_patterns:
                    if pattern.search(line):
                        self.result.vault_violations.append(
                            VaultViolation(
                                file=rel_path,
                                line_number=line_num,
                                violation_type=violation_name,
                                context=line.strip()[:100],
                            )
                        )

    def run_scan(self) -> bool:
        """Run full security scan"""
        print(f"\n{'='*60}")
        print("SECRETS & VAULT POLICY SCANNER")
        print(f"{'='*60}\n")

        print(f"Scanning project: {self.root}")
        print(f"Vault folder: {self.VAULT_FOLDER}")
        print(f"Extensions: {', '.join(self.SCAN_EXTENSIONS)}\n")

        # Find all scannable files
        all_files = []
        for ext in self.SCAN_EXTENSIONS:
            all_files.extend(self.root.rglob(f"*{ext}"))

        scannable = [f for f in all_files if self.should_scan_file(f)]
        self.result.files_scanned = len(scannable)

        print(f"Files to scan: {len(scannable)}")

        # Scan each file
        for i, file_path in enumerate(scannable, 1):
            if i % 100 == 0:
                print(f"  Scanned {i}/{len(scannable)} files...")
            self.scan_file(file_path)

        print(f"\n✓ Scanned {self.result.files_scanned} files")

        # Determine pass/fail
        self.result.passed = len(self.result.secrets_detected) == 0 and len(self.result.vault_violations) == 0

        return self.result.passed

    def generate_report(self, output_path: Path):
        """Generate JSON and MD reports"""
        result_dict = asdict(self.result)

        # JSON
        json_path = output_path.with_suffix(".json")
        json_path.parent.mkdir(parents=True, exist_ok=True)

        with open(json_path, "w") as f:
            json.dump(result_dict, f, indent=2)

        print(f"\n✓ JSON report: {json_path}")

        # MD
        md_lines = [
            "# Secrets & Vault Policy Scan Report",
            "",
            f"**Timestamp:** {self.result.timestamp}",
            f"**Status:** {'✅ PASSED' if self.result.passed else '❌ FAILED'}",
            "",
            "## Summary",
            "",
            f"- Files scanned: {self.result.files_scanned}",
            f"- Secrets detected: {len(self.result.secrets_detected)}",
            f"- Vault violations: {len(self.result.vault_violations)}",
            "",
        ]

        if self.result.secrets_detected:
            md_lines.extend(
                [
                    "## 🔴 SECRETS DETECTED (Outside Vault)",
                    "",
                ]
            )
            for detection in self.result.secrets_detected:
                md_lines.append(f"### {detection.file}:{detection.line_number}")
                md_lines.append(f"- **Type:** {detection.pattern_type}")
                md_lines.append(f"- **Context:** `{detection.context}`")
                md_lines.append("")

        if self.result.vault_violations:
            md_lines.extend(
                [
                    "## ⚠️ VAULT POLICY VIOLATIONS",
                    "",
                ]
            )
            for violation in self.result.vault_violations:
                md_lines.append(f"### {violation.file}:{violation.line_number}")
                md_lines.append(f"- **Violation:** {violation.violation_type}")
                md_lines.append(f"- **Context:** `{violation.context}`")
                md_lines.append("")

        if self.result.passed:
            md_lines.extend(
                [
                    "## ✅ No Security Violations",
                    "",
                    "- No cleartext secrets detected outside vault",
                    "- No vault policy violations found",
                ]
            )

        md_path = output_path.with_suffix(".md")
        with open(md_path, "w") as f:
            f.write("\n".join(md_lines))

        print(f"✓ MD report: {md_path}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    scanner = SecretsVaultScanner(project_root)
    success = scanner.run_scan()

    # Generate reports
    artifacts_dir = project_root / "artifacts" / "scans"
    scanner.generate_report(artifacts_dir / "secrets_vault_scan")

    # Summary
    print(f"\n{'='*60}")
    print("SCAN SUMMARY")
    print(f"{'='*60}")

    if success:
        print("✅ NO SECURITY VIOLATIONS FOUND")
        print("✅ All secrets properly contained in vault (opena11)")
        return 0
    else:
        print("❌ SECURITY VIOLATIONS DETECTED")
        print(f"   Secrets: {len(scanner.result.secrets_detected)}")
        print(f"   Vault violations: {len(scanner.result.vault_violations)}")
        print("\n⚠️  CI MUST BREAK - Security policy violated")
        return 1


if __name__ == "__main__":
    sys.exit(main())
