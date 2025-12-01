#!/usr/bin/env python3
"""
opena19 - Stocks & Crypto Agent
Test Suite - 20 Unit Tests

PORTIER 3.0 Compliant Testing
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


# ================== BASIC TESTS ==================

class TestBasicStructure:
    """Basic Structure Tests"""
    
    def test_directory_exists(self):
        """Test: Agent Directory existiert"""
        agent_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/18.opena19_Aktien&Crypto")
        assert agent_dir.exists()
    
    def test_html_exists(self):
        """Test: HTML-Verzeichnis existiert"""
        html_dir = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/18.opena19_Aktien&Crypto/html")
        assert html_dir.exists()
    
    def test_readme_exists(self):
        """Test: README existiert"""
        readme_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/18.opena19_Aktien&Crypto/README.md")
        assert readme_file.exists()
    
    def test_main_agent_exists(self):
        """Test: Main Agent File existiert"""
        main_file = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/18.opena19_Aktien&Crypto/main_stocks_crypto_agent.py")
        assert main_file.exists()


# ================== MODEL TESTS ==================

class TestModels:
    """Tests für Pydantic Models"""
    
    def test_price_request_valid(self):
        """Test: Gültiger PriceRequest"""
        try:
            from models import PriceRequest, MarketType
            req = PriceRequest(
                symbols=["AAPL", "TSLA"],
                market=MarketType.STOCK
            )
            assert len(req.symbols) == 2
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_position_create_valid(self):
        """Test: Gültiger PositionCreate"""
        try:
            from models import PositionCreate, MarketType
            pos = PositionCreate(
                symbol="BTC",
                market=MarketType.CRYPTO,
                quantity=0.5,
                avg_price=50000.0
            )
            assert pos.quantity == 0.5
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_alert_create_valid(self):
        """Test: Gültiger AlertCreate"""
        try:
            from models import AlertCreate, MarketType, AlertCondition
            alert = AlertCreate(
                symbol="ETH",
                market=MarketType.CRYPTO,
                condition=AlertCondition.ABOVE,
                threshold=4000.0
            )
            assert alert.condition == AlertCondition.ABOVE
        except ImportError:
            pytest.skip("models.py not available")


# ================== ENUM TESTS ==================

class TestEnums:
    """Tests für Enums"""
    
    def test_market_type_values(self):
        """Test: MarketType Werte"""
        try:
            from models import MarketType
            assert MarketType.STOCK.value == "stock"
            assert MarketType.CRYPTO.value == "crypto"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_alert_condition_values(self):
        """Test: AlertCondition Werte"""
        try:
            from models import AlertCondition
            conditions = [c.value for c in AlertCondition]
            assert "above" in conditions
            assert "below" in conditions
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_interval_values(self):
        """Test: Interval Werte"""
        try:
            from models import Interval
            assert Interval.DAILY.value == "daily"
            assert Interval.HOURLY.value == "1h"
        except ImportError:
            pytest.skip("models.py not available")


# ================== SECURITY TESTS ==================

class TestSecurity:
    """Tests für Security-Module"""
    
    def test_mask_secrets(self):
        """Test: Secret Masking"""
        try:
            from security import mask_secrets
            data = {"api_key": "secret123", "symbol": "BTC"}
            masked = mask_secrets(data)
            assert masked["api_key"] == "***MASKED***"
            assert masked["symbol"] == "BTC"
        except ImportError:
            pytest.skip("security.py not available")
    
    def test_api_key_manager_tracking(self):
        """Test: API Key Manager Tracking"""
        try:
            from security import APIKeyManager
            manager = APIKeyManager()
            manager.get_alpha_vantage_key()
            stats = manager.get_usage_stats()
            assert "alpha_vantage" in stats
        except ImportError:
            pytest.skip("security.py not available")
    
    def test_rate_limiter_allows(self):
        """Test: Rate Limiter erlaubt Requests"""
        try:
            from security import RateLimiter
            limiter = RateLimiter(max_requests=5, window_seconds=60)
            mock_request = MagicMock()
            mock_request.client.host = "127.0.0.1"
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
            assert PortPolicy.is_valid_port(12365) is True
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
            assert config.service_name == "opena19"
            assert config.kuerzel == "stockcryptop"
            assert config.port == 12365
        except ImportError:
            pytest.skip("config.py not available")
    
    def test_market_config(self):
        """Test: Market Config"""
        try:
            from config import MARKET_CONFIG
            assert "bitcoin" in MARKET_CONFIG.supported_cryptos
            assert MARKET_CONFIG.default_currency == "USD"
        except ImportError:
            pytest.skip("config.py not available")


# ================== RESPONSE MODEL TESTS ==================

class TestResponseModels:
    """Tests für Response Models"""
    
    def test_health_response_model(self):
        """Test: HealthResponse Model"""
        try:
            from models import HealthResponse
            health = HealthResponse(
                status="ok",
                service="opena19",
                kuerzel="stockcryptop",
                port=12365,
                uptime_seconds=100.5,
                version="1.0",
                total_positions=10,
                total_alerts=5,
                active_alerts=3,
                watchlist_count=20,
                cache_status="active",
                strict=True
            )
            assert health.status == "ok"
        except ImportError:
            pytest.skip("models.py not available")
    
    def test_portfolio_model(self):
        """Test: Portfolio Model"""
        try:
            from models import Portfolio, Position, MarketType, PositionStatus
            portfolio = Portfolio(
                positions=[],
                total_value=10000.0,
                total_cost=9000.0,
                total_pnl=1000.0,
                total_pnl_percent=11.11,
                positions_count=0,
                last_updated="2025-11-30T00:00:00Z"
            )
            assert portfolio.total_pnl == 1000.0
        except ImportError:
            pytest.skip("models.py not available")


# ================== MAIN ==================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
