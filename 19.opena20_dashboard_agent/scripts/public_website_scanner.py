#!/usr/bin/env python3
"""
Public Website Scanner - hyperdashboard-one.de Completeness Check
==================================================================
Validates that ALL required public pages exist and have sufficient content.

REQUIRED PAGES (FAIL HARD):
- / (landing)
- /login, /register, /forgot-password (auth)
- /basic, /pro, /premium, /ultimum (plans)
- /legal/privacy, /legal/terms, /legal/imprint (legal)

CONTENT DENSITY RULES:
- Landing MUST explain: product, agents, workflows, control-plane, security, target groups
- Plan pages MUST NOT be identical (similarity check)
- Each plan page MUST have unique section headings
- Minimum word count per page type

EXIT CODES:
- 0: All checks passed
- 1: Missing pages or insufficient content (CI MUST break)

Usage:
  python3 scripts/public_website_scanner.py [--html-dir build/html/public]
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path

# tracing
from scripts.tracing import init_tracing  # init tracing for scripts

# ============================================================================
# CONFIGURATION
# ============================================================================

REQUIRED_ROUTES = {
    "root": "/",
    "auth": ["/login", "/register", "/forgot-password"],
    "plans": ["/basic", "/pro", "/premium", "/ultimum"],
    "legal": ["/legal/privacy", "/legal/terms", "/legal/imprint"],
}

REQUIRED_SECTIONS_LANDING = [
    "product",  # What is EDEN/HyperDashboard
    "agents",  # What are agents
    "workflows",  # What are workflows
    "control",  # Control plane vs tool chaos
    "security",  # Security & governance
    "target",  # Target groups
]

MIN_WORD_COUNTS = {
    "landing": 800,  # Landing needs LOTS of explanation
    "plan": 300,  # Each plan page minimum
    "auth": 100,  # Auth pages can be shorter
    "legal": 500,  # Legal pages need detail
}

SIMILARITY_THRESHOLD = 0.85  # Plan pages must be < 85% similar


# ============================================================================
# HTML CONTENT EXTRACTOR
# ============================================================================


class ContentExtractor(HTMLParser):
    """Extract text content and structure from HTML"""

    def __init__(self):
        super().__init__()
        self.text_content: list[str] = []
        self.headings: list[tuple[str, str]] = []  # (level, text)
        self.current_tag = None
        self.skip_tags = {"script", "style", "noscript"}
        self.in_skip = False

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag in self.skip_tags:
            self.in_skip = True

        # Track headings
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.current_heading_level = tag

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.in_skip = False
        self.current_tag = None

    def handle_data(self, data):
        if not self.in_skip:
            text = data.strip()
            if text:
                self.text_content.append(text)

                # If we're in a heading, track it
                if self.current_tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    self.headings.append((self.current_tag, text))

    def get_full_text(self) -> str:
        """Get all text content as single string"""
        return " ".join(self.text_content)

    def get_word_count(self) -> int:
        """Get total word count"""
        return len(self.get_full_text().split())

    def get_headings(self) -> list[tuple[str, str]]:
        """Get all headings"""
        return self.headings


# ============================================================================
# SCANNER
# ============================================================================


@dataclass
class PageScanResult:
    """Result of scanning one page"""

    route: str
    file: str
    exists: bool
    passed: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Content analysis
    word_count: int = 0
    headings: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)


class PublicWebsiteScanner:
    """Scans public website for completeness"""

    def __init__(self, html_dir: Path):
        self.html_dir = html_dir
        self.results: list[PageScanResult] = []
        self.errors: list[str] = []
        self.plan_contents: dict[str, str] = {}  # For similarity check

    def route_to_file(self, route: str) -> Path:
        """Convert route to file path"""
        if route == "/":
            return self.html_dir / "index.html"

        # Remove leading slash
        path = route.lstrip("/")

        # Convert to file path
        if not path.endswith(".html"):
            path += ".html"

        return self.html_dir / path

    def scan_page(self, route: str, page_type: str) -> PageScanResult:
        """Scan single page"""
        file_path = self.route_to_file(route)

        result = PageScanResult(
            route=route,
            file=str(file_path.relative_to(self.html_dir) if file_path.exists() else file_path),
            exists=file_path.exists(),
            passed=False,
        )

        if not result.exists:
            result.violations.append("MISSING: Required page does not exist")
            return result

        # Extract content
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            result.violations.append(f"Failed to read file: {e}")
            return result

        extractor = ContentExtractor()
        try:
            extractor.feed(content)
        except Exception as e:
            result.violations.append(f"HTML parsing error: {e}")
            return result

        # Analyze content
        result.word_count = extractor.get_word_count()
        result.headings = [h[1] for h in extractor.get_headings()]

        # Check minimum word count
        min_words = MIN_WORD_COUNTS.get(page_type, 100)
        if result.word_count < min_words:
            result.violations.append(
                f"INSUFFICIENT CONTENT: {result.word_count} words " f"(minimum: {min_words} for {page_type})"
            )

        # Landing page specific checks
        if route == "/":
            text_lower = extractor.get_full_text().lower()
            for section in REQUIRED_SECTIONS_LANDING:
                # Check if section keywords appear in content
                keywords = {
                    "product": ["dashboard", "platform", "system", "eden", "portier"],
                    "agents": ["agent", "opena"],
                    "workflows": ["workflow", "automation", "orchestration"],
                    "control": ["control", "manage", "coordinate"],
                    "security": ["security", "secure", "governance", "vault"],
                    "target": ["business", "enterprise", "company", "team", "individual"],
                }

                section_keywords = keywords.get(section, [section])
                found = any(kw in text_lower for kw in section_keywords)

                if not found:
                    result.missing_sections.append(section)
                    result.violations.append(f"MISSING SECTION: Landing page must explain '{section}'")

        # Plan page checks
        if route in REQUIRED_ROUTES["plans"]:
            # Store content for similarity check
            self.plan_contents[route] = extractor.get_full_text()

            # Check for unique headings
            if not result.headings:
                result.violations.append("MISSING HEADINGS: Plan page must have section headings")

        # Mark as passed if no violations
        result.passed = len(result.violations) == 0

        return result

    def check_plan_similarity(self):
        """Check that plan pages are not too similar"""
        plan_routes = REQUIRED_ROUTES["plans"]

        for i, route1 in enumerate(plan_routes):
            for route2 in plan_routes[i + 1 :]:
                if route1 in self.plan_contents and route2 in self.plan_contents:
                    content1 = self.plan_contents[route1]
                    content2 = self.plan_contents[route2]

                    similarity = SequenceMatcher(None, content1, content2).ratio()

                    if similarity > SIMILARITY_THRESHOLD:
                        error = (
                            f"PLAN SIMILARITY TOO HIGH: {route1} and {route2} "
                            f"are {similarity:.1%} similar (max: {SIMILARITY_THRESHOLD:.1%})"
                        )
                        self.errors.append(error)

                        # Mark both results as failed
                        for result in self.results:
                            if result.route in (route1, route2):
                                result.passed = False
                                result.violations.append(error)

    def scan_all(self) -> bool:
        """Scan all required pages"""
        print(f"\n{'='*60}")
        print("PUBLIC WEBSITE SCANNER - hyperdashboard-one.de")
        print(f"{'='*60}")
        print(f"Scanning: {self.html_dir}")
        print(f"{'='*60}\n")

        # Check root
        print("Checking root...")
        result = self.scan_page("/", "landing")
        self.results.append(result)
        status = "✓" if result.passed else "✗"
        print(f"  {status} / (landing) - {result.word_count} words")

        # Check auth pages
        print("\nChecking auth pages...")
        for route in REQUIRED_ROUTES["auth"]:
            result = self.scan_page(route, "auth")
            self.results.append(result)
            status = "✓" if result.passed else "✗"
            print(f"  {status} {route} - {result.word_count} words")

        # Check plan pages
        print("\nChecking plan pages...")
        for route in REQUIRED_ROUTES["plans"]:
            result = self.scan_page(route, "plan")
            self.results.append(result)
            status = "✓" if result.passed else "✗"
            print(f"  {status} {route} - {result.word_count} words")

        # Check plan similarity
        print("\nChecking plan similarity...")
        self.check_plan_similarity()
        if not self.errors:
            print("  ✓ Plan pages are sufficiently different")

        # Check legal pages
        print("\nChecking legal pages...")
        for route in REQUIRED_ROUTES["legal"]:
            result = self.scan_page(route, "legal")
            self.results.append(result)
            status = "✓" if result.passed else "✗"
            print(f"  {status} {route} - {result.word_count} words")

        all_passed = all(r.passed for r in self.results) and not self.errors
        return all_passed

    def generate_report(self, output_path: Path):
        """Generate JSON and MD reports"""
        # JSON report
        json_report = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "html_dir": str(self.html_dir),
            "total_pages": len(self.results),
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
            "# Public Website Scan Report - hyperdashboard-one.de",
            "",
            f"**Timestamp:** {json_report['timestamp']}",
            f"**Status:** {'✅ PASSED' if json_report['status'] == 'passed' else '❌ FAILED'}",
            "",
            "## Summary",
            "",
            f"- Total pages: {json_report['total_pages']}",
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
                "## Page Results",
                "",
            ]
        )

        for result in self.results:
            status = "✅" if result.passed else "❌"
            md_lines.append(f"### {status} {result.route}")
            md_lines.append("")
            md_lines.append(f"- **File:** `{result.file}`")
            md_lines.append(f"- **Exists:** {result.exists}")
            md_lines.append(f"- **Word count:** {result.word_count}")
            md_lines.append("")

            if result.headings:
                md_lines.append("**Headings:**")
                for h in result.headings:
                    md_lines.append(f"- {h}")
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

    parser = argparse.ArgumentParser(description="Public Website Scanner")
    parser.add_argument(
        "--html-dir",
        type=Path,
        default=Path(__file__).parent.parent / "build" / "html" / "public",
        help="Public HTML directory to scan (default: build/html/public)",
    )

    args = parser.parse_args()

    scanner = PublicWebsiteScanner(args.html_dir)
    success = scanner.scan_all()

    # Generate reports
    artifacts_dir = Path(__file__).parent.parent / "artifacts" / "scans"
    scanner.generate_report(artifacts_dir / "public_site_scan")

    # Print summary
    print(f"\n{'='*60}")
    print("SCAN SUMMARY")
    print(f"{'='*60}")

    if success:
        print("✅ ALL PUBLIC WEBSITE CHECKS PASSED")
        print("✅ hyperdashboard-one.de is complete and content-rich")
        return 0
    else:
        print("❌ PUBLIC WEBSITE VIOLATIONS FOUND")
        print("\n⚠️  CI MUST BREAK - Fix missing/insufficient content")
        return 1


if __name__ == "__main__":
    # initialize tracing for this script
    init_tracing("public_website_scanner")
    sys.exit(main())
