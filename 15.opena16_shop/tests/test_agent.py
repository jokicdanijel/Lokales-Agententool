#!/usr/bin/env python3
from pathlib import Path

import pytest


class Test15Opena16_Shop:
    def test_directory_exists(self):
        agent_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/15.opena16_shop")
        assert agent_dir.exists()

    def test_html_exists(self):
        html_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/15.opena16_shop/html/index.html")
        assert html_file.exists()

    def test_readme_exists(self):
        readme_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/15.opena16_shop/README.md")
        assert readme_file.exists()

    def test_html_content_valid(self):
        html_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/15.opena16_shop/html/index.html")
        if html_file.exists():
            content = html_file.read_text()
            assert "<!DOCTYPE html>" in content
            assert "15.opena16_shop" in content


if __name__ == "__main__":
    pytest.main([__file__])
