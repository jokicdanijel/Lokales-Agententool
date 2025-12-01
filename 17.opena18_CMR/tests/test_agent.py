#!/usr/bin/env python3
"""
opena18 - CRM Agent
Test Suite - 20 Unit Tests

PORTIER 3.0 Compliant Testing
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


# ================== BASIC TESTS ==================

class Test17Opena18_Cmr:
    """Basic Structure Tests"""
    
    def test_directory_exists(self):
        """Test: Agent Directory existiert"""
        agent_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/17.opena18_CMR")
        assert agent_dir.exists()
    
    def test_html_exists(self):
        """Test: HTML-Verzeichnis existiert"""
        html_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/17.opena18_CMR/html")
        assert html_dir.exists()
    
    def test_readme_exists(self):
        """Test: README existiert"""
        readme_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/17.opena18_CMR/README.md")
        assert readme_file.exists()
    
    def test_main_agent_exists(self):
        """Test: Main Agent File existiert"""
        main_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/17.opena18_CMR/main_crm_agent.py")
        assert main_file.exists()


# ================== MODEL TESTS ==================

class TestModels:
    """Tests für Pydantic Models"""
    
    def test_contact_create_valid(self):
        """Test: Gültiger ContactCreate"""
        try:
            from models import ContactCreate
            contact = ContactCreate(
                first_name="Max",
                last_name="Mustermann",
                email="max@example.com"
            )
            assert contact.first_name == "Max"
            assert contact.email == "max@example.com"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_organization_create_valid(self):
        """Test: Gültige OrganizationCreate"""
        try:
            from models import OrganizationCreate, OrganizationSize
            org = OrganizationCreate(
                name="ACME Corp",
                size=OrganizationSize.MEDIUM
            )
            assert org.name == "ACME Corp"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_deal_create_valid(self):
        """Test: Gültiger DealCreate"""
        try:
            from models import DealCreate, DealStage
            deal = DealCreate(
                title="Enterprise Deal",
                value=50000.0,
                stage=DealStage.PROPOSAL
            )
            assert deal.value == 50000.0
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_activity_create_valid(self):
        """Test: Gültige ActivityCreate"""
        try:
            from models import ActivityCreate, ActivityType
            activity = ActivityCreate(
                activity_type=ActivityType.CALL,
                subject="Follow-up Call"
            )
            assert activity.activity_type == ActivityType.CALL
        except ImportError:
            pytest.skip("models.py not available")


# ================== ENUM TESTS ==================

class TestEnums:
    """Tests für Enums"""
    
    def test_deal_stage_values(self):
        """Test: DealStage Werte"""
        try:
            from models import DealStage
            assert DealStage.LEAD.value == "lead"
            assert DealStage.CLOSED_WON.value == "closed_won"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_activity_type_values(self):
        """Test: ActivityType Werte"""
        try:
            from models import ActivityType
            types = [t.value for t in ActivityType]
            assert "call" in types
            assert "email" in types
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_organization_size_values(self):
        """Test: OrganizationSize Werte"""
        try:
            from models import OrganizationSize
            assert OrganizationSize.ENTERPRISE.value == "enterprise"
        except ImportError:
            pytest.skip("models.py not available")


# ================== SECURITY TESTS ==================

class TestSecurity:
    """Tests für Security-Module"""
    
    def test_mask_secrets_simple(self):
        """Test: Secret Masking"""
        try:
            from security import mask_secrets
            data = {"password": "secret123", "name": "test"}
            masked = mask_secrets(data)
            assert masked["password"] == "***MASKED***"
            assert masked["name"] == "test"
        except ImportError:
            pytest.skip("security.py not available")
    
    def test_gdpr_manager_consent(self):
        """Test: GDPR Consent Recording"""
        try:
            from security import GDPRComplianceManager
            manager = GDPRComplianceManager()
            consent = manager.record_consent(
                "contact123",
                "marketing",
                True
            )
            assert consent["granted"] is True
            assert manager.check_consent("contact123", "marketing") is True
        except ImportError:
            pytest.skip("security.py not available")
    
    def test_gdpr_manager_deletion_request(self):
        """Test: GDPR Deletion Request"""
        try:
            from security import GDPRComplianceManager
            manager = GDPRComplianceManager()
            request = manager.request_deletion("contact123", "User request")
            assert request["status"] == "pending"
        except ImportError:
            pytest.skip("security.py not available")
    
    def test_gdpr_manager_anonymize(self):
        """Test: GDPR Anonymization"""
        try:
            from security import GDPRComplianceManager
            manager = GDPRComplianceManager()
            contact = {
                "contact_id": "123",
                "first_name": "Max",
                "last_name": "Mustermann",
                "email": "max@example.com",
                "phone": "+49123456789"
            }
            anonymized = manager.anonymize_contact(contact)
            assert anonymized["first_name"] == "ANONYMIZED"
            assert "anon-123" in anonymized["email"]
        except ImportError:
            pytest.skip("security.py not available")


# ================== CONFIG TESTS ==================

class TestConfig:
    """Tests für Konfiguration"""
    
    def test_port_policy_valid(self):
        """Test: Gültige Ports"""
        try:
            from config import PortPolicy
            assert PortPolicy.is_valid_port(12363) is True
            assert PortPolicy.is_valid_port(12344) is True
        except ImportError:
            pytest.skip("config.py not available")
    
    def test_port_policy_invalid(self):
        """Test: Ungültige Ports"""
        try:
            from config import PortPolicy
            assert PortPolicy.is_valid_port(8080) is False
        except ImportError:
            pytest.skip("config.py not available")
    
    def test_load_config_defaults(self):
        """Test: Standard-Konfiguration"""
        try:
            from config import load_config
            config = load_config()
            assert config.service_name == "opena18"
            assert config.kuerzel == "crmp"
            assert config.port == 12363
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
                service="opena18",
                kuerzel="crmp",
                port=12363,
                uptime_seconds=100.5,
                version="1.0",
                total_contacts=100,
                total_organizations=50,
                total_deals=25,
                total_activities=500,
                gdpr_compliance=True,
                strict=True
            )
            assert health.status == "ok"
            assert health.gdpr_compliance is True
        except ImportError:
            pytest.skip("models.py not available")


class TestPipelineStats:
    """Tests für Pipeline-Statistiken"""
    
    def test_pipeline_stats_model(self):
        """Test: PipelineStats Model"""
        try:
            from models import PipelineStats
            stats = PipelineStats(
                total_deals=10,
                total_value=500000.0,
                weighted_value=250000.0,
                by_stage={"lead": 3, "proposal": 5, "closed_won": 2},
                average_deal_size=50000.0,
                win_rate=0.2
            )
            assert stats.total_deals == 10
        except ImportError:
            pytest.skip("models.py not available")


# ================== MAIN ==================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
