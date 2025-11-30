#!/usr/bin/env python3
import pytest
import asyncio
from pathlib import Path

class Test18Opena19_Aktien&Crypto:
    def test_directory_exists(self):
        agent_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/18.opena19_Aktien&Crypto")
        assert agent_dir.exists()
    
    def test_html_exists(self):
        html_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/18.opena19_Aktien&Crypto/html/index.html")
        assert html_file.exists()
    
    def test_readme_exists(self):
        readme_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/18.opena19_Aktien&Crypto/README.md")
        assert readme_file.exists()
    
    def test_html_content_valid(self):
        html_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/18.opena19_Aktien&Crypto/html/index.html")
        if html_file.exists():
            content = html_file.read_text()
            assert "<!DOCTYPE html>" in content
            assert "18.opena19_Aktien&Crypto" in content

if __name__ == "__main__":
    pytest.main([__file__])
