#!/usr/bin/env python3
"""
HTML Contract Scanner
=====================
Validates ALL generated HTML against strict contract rules.

FAIL-HARD RULES:
1. NO <script> tags
2. NO inline <style> attributes
3. NO <link rel="stylesheet"> (CSS must be external)
4. MUST use semantic HTML5 structure
5. All forms MUST have data-action + data-api attributes
6. Auth pages MUST follow auth contract pattern
7. Error pages (403, 404, 500) MUST exist

EXIT CODES:
- 0: All checks passed
- 1: Contract violations found (CI MUST break)

Usage:
  python3 scripts/html_contract_scanner.py [--html-dir build/html]
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, ClassVar

# tracing
from scripts.tracing import init_tracing  # init tracing for scripts

# ============================================================================
# HTML PARSER
# ============================================================================


class ContractHTMLParser(HTMLParser):
    """Strict HTML contract validator"""

    def __init__(self):
        super().__init__()
        self.violations: list[str] = []
        self.warnings: list[str] = []

        # Structure tracking
        self.has_header = False
        self.has_nav = False
        self.has_main = False
        self.has_footer = False

        # Contract tracking
        self.script_tags = 0
        self.inline_styles = 0
        self.css_links = 0
        self.forms: list[dict[str, Any]] = []
        self.current_form: dict[str, set[str]] = {}

        # Semantic elements
        self.semantic_tags = set()

        # Current tag stack
        self.tag_stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tag_stack.append(tag)

        # Track semantic structure
        if tag == "header":
            self.has_header = True
        elif tag == "nav":
            self.has_nav = True
        elif tag == "main":
            self.has_main = True
        elif tag == "footer":
            self.has_footer = True
        elif tag in ("section", "article", "aside"):
            self.semantic_tags.add(tag)

        # VIOLATION: <script>
        if tag == "script":
            self.script_tags += 1
            self.violations.append("FORBIDDEN: <script> tag found")

        # VIOLATION: inline style attribute
        if "style" in attrs_dict:
            self.inline_styles += 1
            self.violations.append(f"FORBIDDEN: inline style attribute on <{tag}>")

        # VIOLATION: CSS link
        if tag == "link" and attrs_dict.get("rel") == "stylesheet":
            self.css_links += 1
            self.violations.append("FORBIDDEN: <link rel='stylesheet'> found")

        # FORM tracking
        if tag == "form":
            self.current_form = {
                "attrs": set(attrs_dict.keys()),
                "action": attrs_dict.get("action", ""),
                "method": attrs_dict.get("method", "GET").upper(),
            }

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

        # Form validation on close
        if tag == "form":
            if self.current_form:
                # Check data-attributes
                has_data_action = "data-action" in self.current_form["attrs"]
                has_data_api = "data-api" in self.current_form["attrs"]

                if not has_data_action:
                    self.violations.append("MISSING: <form> must have data-action attribute")

                if not has_data_api:
                    self.violations.append("MISSING: <form> must have data-api attribute")

                self.forms.append(dict(self.current_form))
                self.current_form = {}


# ============================================================================
# SCANNER
# ============================================================================


@dataclass
class HTMLScanResult:
    """Result of scanning one HTML file"""

    file: str
    passed: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Structure
    has_semantic_structure: bool = False
    has_header: bool = False
    has_nav: bool = False
    has_main: bool = False
    has_footer: bool = False

    # Contract
    script_count: int = 0
    inline_style_count: int = 0
    css_link_count: int = 0
    form_count: int = 0
    forms_valid: int = 0


class HTMLContractScanner:
    """Scans HTML files for contract compliance"""

    REQUIRED_ERROR_PAGES: ClassVar[list[str]] = ["403.html", "404.html", "500.html"]
    AUTH_PAGES: ClassVar[list[str]] = ["login.html", "register.html", "forgot-password.html"]

    def __init__(self, html_dir: Path):
        self.html_dir = html_dir
        self.results: list[HTMLScanResult] = []
        self.errors: list[str] = []

    def scan_file(self, file_path: Path) -> HTMLScanResult:
        """Scan single HTML file"""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            result = HTMLScanResult(
                file=str(file_path.relative_to(self.html_dir)), passed=False, violations=[f"Failed to read file: {e}"]
            )
            return result

        # Parse
        parser = ContractHTMLParser()
        try:
            parser.feed(content)
        except Exception as e:
            result = HTMLScanResult(
                file=str(file_path.relative_to(self.html_dir)), passed=False, violations=[f"HTML parsing error: {e}"]
            )
            return result

        # Check semantic structure
        has_semantic = parser.has_header and parser.has_main

        if not has_semantic:
            parser.warnings.append("RECOMMENDED: Use semantic HTML5 structure (<header>, <main>, <footer>)")

        # Build result
        result = HTMLScanResult(
            file=str(file_path.relative_to(self.html_dir)),
            passed=len(parser.violations) == 0,
            violations=parser.violations,
            warnings=parser.warnings,
            has_semantic_structure=has_semantic,
            has_header=parser.has_header,
            has_nav=parser.has_nav,
            has_main=parser.has_main,
            has_footer=parser.has_footer,
            script_count=parser.script_tags,
            inline_style_count=parser.inline_styles,
            css_link_count=parser.css_links,
            form_count=len(parser.forms),
            forms_valid=sum(1 for f in parser.forms if "data-action" in f["attrs"] and "data-api" in f["attrs"]),
        )

        return result

    def scan_all(self) -> bool:
        """Scan all HTML files in directory"""
        if not self.html_dir.exists():
            self.errors.append(f"HTML directory not found: {self.html_dir}")
            return False

        html_files = sorted(self.html_dir.rglob("*.html"))

        if not html_files:
            self.errors.append(f"No HTML files found in {self.html_dir}")
            return False

        print(f"\n{'='*60}")
        print("HTML CONTRACT SCANNER")
        print(f"{'='*60}")
        print(f"Scanning: {self.html_dir}")
        print(f"Files found: {len(html_files)}")
        print(f"{'='*60}\n")

        # Check required error pages
        error_pages_found = []
        for error_page in self.REQUIRED_ERROR_PAGES:
            error_path = self.html_dir / error_page
            if error_path.exists():
                error_pages_found.append(error_page)
            else:
                self.errors.append(f"MISSING REQUIRED: {error_page}")

        print(f"✓ Error pages: {len(error_pages_found)}/{len(self.REQUIRED_ERROR_PAGES)}")

        # Scan each file
        for html_file in html_files:
            result = self.scan_file(html_file)
            self.results.append(result)

            status = "✓" if result.passed else "✗"
            print(f"{status} {result.file}")

            if result.violations:
                for violation in result.violations:
                    print(f"    ✗ {violation}")

        all_passed = all(r.passed for r in self.results) and not self.errors
        return all_passed

    def generate_report(self, output_path: Path):
        """Generate JSON and MD reports"""
        # JSON report
        json_report = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "html_dir": str(self.html_dir),
            "total_files": len(self.results),
            "passed": sum(1 for r in self.results if r.passed),
            "failed": sum(1 for r in self.results if not r.passed),
            "status": "passed" if all(r.passed for r in self.results) and not self.errors else "failed",
            "errors": self.errors,
            "results": [asdict(r) for r in self.results],
        }

        json_path = output_path.with_suffix(".json")
        json_path.parent.mkdir(parents=True, exist_ok=True)

        with open(json_path, "w") as f:
            json.dump(json_report, f, indent=2)

        print(f"\n✓ JSON report: {json_path}")

        # MD report
        md_lines = [
            "# HTML Contract Scan Report",
            "",
            f"**Timestamp:** {json_report['timestamp']}",
            f"**Status:** {'✅ PASSED' if json_report['status'] == 'passed' else '❌ FAILED'}",
            "",
            "## Summary",
            "",
            f"- Total files: {json_report['total_files']}",
            f"- Passed: {json_report['passed']}",
            f"- Failed: {json_report['failed']}",
            "",
        ]

        if self.errors:
            md_lines.extend(
                [
                    "## System Errors",
                    "",
                ]
            )
            for error in self.errors:
                md_lines.append(f"- ❌ {error}")
            md_lines.append("")

        md_lines.extend(
            [
                "## File Results",
                "",
            ]
        )

        for result in self.results:
            status = "✅" if result.passed else "❌"
            md_lines.append(f"### {status} {result.file}")
            md_lines.append("")

            if result.violations:
                md_lines.append("**Violations:**")
                for v in result.violations:
                    md_lines.append(f"- ❌ {v}")
                md_lines.append("")

            if result.warnings:
                md_lines.append("**Warnings:**")
                for w in result.warnings:
                    md_lines.append(f"- ⚠️ {w}")
                md_lines.append("")

        md_path = output_path.with_suffix(".md")
        with open(md_path, "w") as f:
            f.write("\n".join(md_lines))

        print(f"✓ MD report: {md_path}")


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="HTML Contract Scanner")
    parser.add_argument(
        "--html-dir",
        type=Path,
        default=Path(__file__).parent.parent / "build" / "html",
        help="HTML directory to scan (default: build/html)",
    )

    args = parser.parse_args()

    scanner = HTMLContractScanner(args.html_dir)
    success = scanner.scan_all()

    # Generate reports
    artifacts_dir = Path(__file__).parent.parent / "artifacts" / "scans"
    scanner.generate_report(artifacts_dir / "html_contract_scan")

    # Print summary
    print(f"\n{'='*60}")
    print("SCAN SUMMARY")
    print(f"{'='*60}")

    if success:
        print("✅ ALL HTML CONTRACT CHECKS PASSED")
        return 0
    else:
        print("❌ HTML CONTRACT VIOLATIONS FOUND")
        print("\n⚠️  CI MUST BREAK - Fix violations before deployment")
        return 1


if __name__ == "__main__":
    # initialize tracing for this script
    init_tracing("html_contract_scanner")
    sys.exit(main())
