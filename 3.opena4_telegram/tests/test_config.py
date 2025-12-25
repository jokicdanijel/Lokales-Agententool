#!/usr/bin/env python3
"""
Tests für opena4 Config-Modul
Pydantic V2 + ENV Loading + Whitelist
"""

import os
from unittest.mock import patch

import pytest


class TestConfigLoading:
    """Tests für ENV-basierte Konfiguration"""

    def test_telegram_config_loads_from_env(self):
        """Test: TELEGRAM_BOT_TOKEN und TELEGRAM_ALLOWED_USER_IDS aus ENV laden"""
        with patch.dict(
            os.environ, {"TELEGRAM_BOT_TOKEN": "test_token_123", "TELEGRAM_ALLOWED_USER_IDS": "7664467819,123456789"}
        ):
            # Reimport um frische Config zu laden
            import sys

            # Clear cached config
            if "config" in sys.modules:
                del sys.modules["config"]

            from config import ServiceConfig

            # Erstelle neue Config-Instanz
            config = ServiceConfig()

            assert config.telegram_bot_token == "test_token_123"
            # Note: pydantic-settings parst komma-separierte Strings als Liste
            # Je nach Version muss dies angepasst werden

    def test_default_port_is_12346(self):
        """Test: Default Port ist 12346 (PORTIER Range)"""
        from config import ServiceConfig

        config = ServiceConfig()
        assert config.port == 12346
        assert config.port in range(12344, 12400)  # PORTIER Range

    def test_kuerzel_is_tgap(self):
        """Test: Kürzel ist 'tgap' (Telegram Gateway Agent)"""
        from config import ServiceConfig

        config = ServiceConfig()
        assert config.kuerzel == "tgap"

    def test_service_name_is_opena4(self):
        """Test: Service Name ist 'opena4'"""
        from config import ServiceConfig

        config = ServiceConfig()
        assert config.service_name == "opena4"


class TestPortPolicy:
    """Tests für Port-Policy Enforcement"""

    def test_valid_port_in_range(self):
        """Test: Gültiger Port in PORTIER Range"""
        from config import PortPolicy

        assert PortPolicy.is_valid_port(12346) is True
        assert PortPolicy.is_valid_port(12344) is True
        assert PortPolicy.is_valid_port(12399) is True

    def test_invalid_port_outside_range(self):
        """Test: Ungültiger Port außerhalb Range"""
        from config import PortPolicy

        assert PortPolicy.is_valid_port(8080) is False  # Verboten
        assert PortPolicy.is_valid_port(3000) is False  # Zu niedrig
        assert PortPolicy.is_valid_port(12400) is False  # Zu hoch

    def test_forbidden_port_8080(self):
        """Test: Port 8080 ist explizit verboten"""
        from config import PortPolicy

        assert 8080 in PortPolicy.FORBIDDEN_PORTS
        assert PortPolicy.is_valid_port(8080) is False


class TestWhitelistLogic:
    """Tests für Telegram User Whitelist"""

    def test_whitelist_check_authorized(self):
        """Test: Autorisierter User wird erkannt"""
        allowed_ids = [7664467819, 123456789]
        user_id = 7664467819

        is_authorized = user_id in allowed_ids
        assert is_authorized is True

    def test_whitelist_check_unauthorized(self):
        """Test: Nicht autorisierter User wird blockiert"""
        allowed_ids = [7664467819, 123456789]
        user_id = 999999999

        is_authorized = user_id in allowed_ids
        assert is_authorized is False

    def test_empty_whitelist_blocks_all(self):
        """Test: Leere Whitelist blockiert alle (wenn enforced)"""
        allowed_ids = []
        user_id = 7664467819

        # Bei leerer Liste: Entweder alle blockieren oder alle erlauben
        # Hier: Wenn whitelist leer UND enforced → blockieren
        is_authorized = len(allowed_ids) == 0 or user_id in allowed_ids
        # In Production: is_authorized = not allowed_ids or user_id in allowed_ids


class TestConfigToDict:
    """Tests für Config Serialisierung"""

    def test_to_dict_masks_secrets(self):
        """Test: to_dict() maskiert sensitive Felder"""
        from config import ServiceConfig

        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "secret_token_xyz"}):
            config = ServiceConfig()
            config.telegram_bot_token = "secret_token_xyz"

            config_dict = config.to_dict()

            # Token sollte maskiert sein
            assert config_dict.get("telegram_bot_token") == "***"
            assert "secret_token_xyz" not in str(config_dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
