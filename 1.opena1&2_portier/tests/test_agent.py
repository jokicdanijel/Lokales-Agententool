#!/usr/bin/env python3
from pathlib import Path

import pytest


class TestPortierCore:
    def test_directory_exists(self):
        agent_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier")
        assert agent_dir.exists()

    def test_html_exists(self):
        html_file = Path(
            "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/html/index.html"
        )
        assert html_file.exists()

    def test_readme_exists(self):
        readme_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/README.md")
        assert readme_file.exists()

    def test_html_content_valid(self):
        html_file = Path(
            "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/html/index.html"
        )
        if html_file.exists():
            content = html_file.read_text()
            assert "<!DOCTYPE html>" in content
            # HTML updated: check for visible dashboard strings instead of repo-folder name
            assert ("Portier Dashboard" in content) or ("opena1: 12344" in content) or ("opena2: 12345" in content)


if __name__ == "__main__":
    pytest.main([__file__])
