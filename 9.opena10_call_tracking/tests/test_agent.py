#!/usr/bin/env python3
from pathlib import Path

import pytest


class Test9Opena10_Call_Tracking:
    def test_directory_exists(self):
        agent_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/9.opena10_call_tracking")
        assert agent_dir.exists()

    def test_html_exists(self):
        html_file = Path(
            "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/9.opena10_call_tracking/html/index.html"
        )
        assert html_file.exists()

    def test_readme_exists(self):
        readme_file = Path(
            "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/9.opena10_call_tracking/README.md"
        )
        assert readme_file.exists()

    def test_html_content_valid(self):
        html_file = Path(
            "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/9.opena10_call_tracking/html/index.html"
        )
        if html_file.exists():
            content = html_file.read_text()
            assert "<!DOCTYPE html>" in content
            assert "9.opena10_call_tracking" in content


if __name__ == "__main__":
    pytest.main([__file__])
