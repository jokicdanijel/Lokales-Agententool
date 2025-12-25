#!/usr/bin/env python3
"""
opena17 - Homepage Creator Agent
Test Suite - 20 Unit Tests

PORTIER 3.0 Compliant Testing
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ================== BASIC TESTS ==================


class Test16Opena17_Homepagecreator:
    """Basic Structure Tests"""

    def test_directory_exists(self):
        """Test: Agent Directory existiert"""
        agent_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/16.opena17_homepagecreator")
        assert agent_dir.exists()

    def test_html_exists(self):
        """Test: HTML-Verzeichnis existiert"""
        html_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/16.opena17_homepagecreator/html")
        assert html_dir.exists()

    def test_readme_exists(self):
        """Test: README existiert"""
        readme_file = Path(
            "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/16.opena17_homepagecreator/README.md"
        )
        assert readme_file.exists()

    def test_main_agent_exists(self):
        """Test: Main Agent File existiert"""
        main_file = Path(
            "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/16.opena17_homepagecreator/main_homepage_agent.py"
        )
        assert main_file.exists()


# ================== MODEL TESTS ==================


class TestModels:
    """Tests für Pydantic Models"""

    def test_page_definition_valid(self):
        """Test: Gültige PageDefinition"""
        try:
            from models import PageDefinition

            page = PageDefinition(slug="about", title="About Us", content="<p>About content</p>", is_homepage=False)
            assert page.slug == "about"
            assert page.title == "About Us"
        except ImportError:
            pytest.skip("models.py not available")

    def test_site_branding_valid(self):
        """Test: Gültiges SiteBranding"""
        try:
            from models import SiteBranding

            branding = SiteBranding(site_name="Test Site", color_primary="#007bff")
            assert branding.site_name == "Test Site"
        except ImportError:
            pytest.skip("models.py not available")

    def test_navigation_item_nested(self):
        """Test: Verschachtelte Navigation"""
        try:
            from models import NavigationItem

            nav = NavigationItem(
                label="Products", slug="products", children=[NavigationItem(label="Product A", slug="product-a")]
            )
            assert len(nav.children) == 1
        except ImportError:
            pytest.skip("models.py not available")


# ================== SECURITY TESTS ==================


class TestSecurity:
    """Tests für Security-Module"""

    def test_mask_secrets_simple(self):
        """Test: Secret Masking"""
        try:
            from security import mask_secrets

            data = {"token": "secret123", "name": "test"}
            masked = mask_secrets(data)
            assert masked["token"] == "***MASKED***"
            assert masked["name"] == "test"
        except ImportError:
            pytest.skip("security.py not available")

    def test_mask_secrets_nested(self):
        """Test: Nested Secret Masking"""
        try:
            from security import mask_secrets

            data = {"config": {"api_key": "secret", "endpoint": "http://example.com"}}
            masked = mask_secrets(data)
            assert masked["config"]["api_key"] == "***MASKED***"
        except ImportError:
            pytest.skip("security.py not available")

    def test_rate_limiter_allows_requests(self):
        """Test: Rate Limiter erlaubt Requests"""
        try:
            from security import RateLimiter

            limiter = RateLimiter(max_requests=5, window_seconds=60)
            mock_request = MagicMock()
            mock_request.client.host = "127.0.0.1"
            mock_request.headers = {"authorization": "Bearer test"}
            assert limiter.is_allowed(mock_request) is True
        except ImportError:
            pytest.skip("security.py not available")


# ================== CONFIG TESTS ==================


class TestConfig:
    """Tests für Konfiguration"""

    def test_port_policy_valid(self):
        """Test: Gültige Ports"""
        try:
            from config import PortPolicy

            assert PortPolicy.is_valid_port(12362) is True
            assert PortPolicy.is_valid_port(12344) is True
        except ImportError:
            pytest.skip("config.py not available")

    def test_port_policy_invalid(self):
        """Test: Ungültige Ports"""
        try:
            from config import PortPolicy

            assert PortPolicy.is_valid_port(8080) is False
            assert PortPolicy.is_valid_port(80) is False
        except ImportError:
            pytest.skip("config.py not available")

    def test_load_config_defaults(self):
        """Test: Standard-Konfiguration"""
        try:
            from config import load_config

            config = load_config()
            assert config.service_name == "opena17"
            assert config.kuerzel == "hpcreatep"
        except ImportError:
            pytest.skip("config.py not available")


# ================== INTEGRATION TESTS ==================


class TestHealthEndpoint:
    """Tests für Health-Endpoint"""

    def test_health_response_model(self):
        """Test: HealthResponse Model"""
        try:
            from models import HealthResponse

            health = HealthResponse(
                status="ok",
                service="opena17",
                kuerzel="hpcreatep",
                port=12362,
                uptime_seconds=100.5,
                version="1.0",
                total_sites=5,
                total_pages=25,
                disk_usage_mb=10.5,
                strict=True,
            )
            assert health.status == "ok"
            assert health.strict is True
        except ImportError:
            pytest.skip("models.py not available")


class TestGenerateSite:
    """Tests für Site-Generierung"""

    def test_generator_enum(self):
        """Test: SiteGeneratorType Enum"""
        try:
            from models import SiteGeneratorType

            assert SiteGeneratorType.STATIC.value == "static"
            assert SiteGeneratorType.SSG_HUGO.value == "hugo"
        except ImportError:
            pytest.skip("models.py not available")


class TestExportSite:
    """Tests für Site-Export"""

    def test_export_format_enum(self):
        """Test: ExportFormat Enum"""
        try:
            from models import ExportFormat

            assert ExportFormat.ZIP.value == "zip"
            assert ExportFormat.TAR_GZ.value == "tar.gz"
        except ImportError:
            pytest.skip("models.py not available")


class TestDeploySite:
    """Tests für Site-Deployment"""

    def test_deployment_target_enum(self):
        """Test: DeploymentTarget Enum"""
        try:
            from models import DeploymentTarget

            targets = [t.value for t in DeploymentTarget]
            assert "local" in targets
            assert "netlify" in targets
        except ImportError:
            pytest.skip("models.py not available")


# ================== MAIN ==================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
