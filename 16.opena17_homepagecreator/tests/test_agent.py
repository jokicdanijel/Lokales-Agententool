#!/usr/bin/env python3
import pytest
import asyncio
from pathlib import Path

class Test16Opena17_Homepagecreator:
    def test_directory_exists(self):
        agent_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/16.opena17_homepagecreator")
        assert agent_dir.exists()
    
    def test_html_exists(self):
        html_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/16.opena17_homepagecreator/html/index.html")
        assert html_file.exists()
    
    def test_readme_exists(self):
        readme_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/16.opena17_homepagecreator/README.md")
        assert readme_file.exists()
    
    def test_html_content_valid(self):
        html_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/16.opena17_homepagecreator/html/index.html")
        if html_file.exists():
            content = html_file.read_text()
            assert "<!DOCTYPE html>" in content
            assert "16.opena17_homepagecreator" in content

if __name__ == "__main__":
    pytest.main([__file__])
