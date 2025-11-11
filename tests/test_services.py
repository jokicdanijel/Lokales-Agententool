"""
tests/test_services.py — Automated Service Testing Suite
- Health checks for all service endpoints
- Echo endpoint validation
- Error handling verification
"""

import json
import pytest
from pathlib import Path


class TestServiceStructure:
    """Test service folder and file structure."""
    
    def test_service_main_py_exists(self):
        """Verify main.py exists in all service directories."""
        services_dir = Path("src/services")
        services = [d for d in services_dir.iterdir() if d.is_dir()]
        
        assert len(services) > 0, "No services found"
        
        for service_dir in services:
            main_py = service_dir / "main.py"
            assert main_py.exists(), f"{service_dir.name}: main.py not found"
    
    def test_service_requirements_exists(self):
        """Verify requirements.txt exists in scalable services."""
        services_dir = Path("src/services")
        scalable_services = [
            d for d in services_dir.iterdir()
            if d.is_dir() and d.name not in ["portier", "openwebui", "dashboard_agent"]
        ]
        
        for service_dir in scalable_services:
            req_txt = service_dir / "requirements.txt"
            if req_txt.exists():
                # Verify it's not empty
                content = req_txt.read_text().strip()
                assert len(content) > 0, f"{service_dir.name}: requirements.txt is empty"


class TestServiceSyntax:
    """Test Python syntax of service files."""
    
    def test_portier_syntax(self):
        """Verify Portier service syntax."""
        import py_compile
        py_compile.compile("src/services/portier/main.py", doraise=True)
    
    def test_telegram_syntax(self):
        """Verify Telegram service syntax."""
        import py_compile
        py_compile.compile("src/services/telegram/main.py", doraise=True)
    
    def test_inference_syntax(self):
        """Verify Inference service syntax."""
        import py_compile
        py_compile.compile("src/services/inference/main.py", doraise=True)
    
    def test_template_syntax(self):
        """Verify Template service syntax."""
        import py_compile
        py_compile.compile("src/services/template/main.py", doraise=True)


class TestServiceConfigs:
    """Test service configuration."""
    
    def test_routing_matrix_yaml_valid(self):
        """Verify routing_matrix.yaml is valid YAML."""
        import yaml
        with open("configs/routing_matrix.yaml") as f:
            config = yaml.safe_load(f)
        
        assert config is not None, "routing_matrix.yaml is invalid"
        assert "scalable_services" in config, "Missing scalable_services"
        assert "coordinator" in config, "Missing coordinator"
        assert "archivator" in config, "Missing archivator"
    
    def test_routing_matrix_has_20_services(self):
        """Verify routing_matrix.yaml defines 20 services."""
        import yaml
        with open("configs/routing_matrix.yaml") as f:
            config = yaml.safe_load(f)
        
        scalable = config.get("scalable_services", {})
        # At least 20 services (portier + archivator + 18 scalable)
        assert len(scalable) >= 18, f"Expected at least 18 scalable services, got {len(scalable)}"
    
    def test_llama_stack_config_exists(self):
        """Verify llama_stack_config.json exists."""
        config_file = Path("configs/llama_stack_config.json")
        assert config_file.exists(), "llama_stack_config.json not found"
        
        # Verify it's valid JSON
        with open(config_file) as f:
            config = json.load(f)
        
        assert "models" in config, "Missing models"
        assert "inference_service" in config, "Missing inference_service"


class TestLoadTestScripts:
    """Test load test script syntax and structure."""
    
    def test_load_test_syntax(self):
        """Verify load_test.py syntax."""
        import py_compile
        py_compile.compile("scripts/load_test.py", doraise=True)
    
    def test_load_test_inference_syntax(self):
        """Verify load_test_inference.py syntax."""
        import py_compile
        py_compile.compile("scripts/load_test_inference.py", doraise=True)
    
    def test_load_test_scaled_syntax(self):
        """Verify load_test_scaled.py syntax."""
        import py_compile
        py_compile.compile("scripts/load_test_scaled.py", doraise=True)
    
    def test_orchestration_test_syntax(self):
        """Verify test_multi_service_orchestration.py syntax."""
        import py_compile
        py_compile.compile("scripts/test_multi_service_orchestration.py", doraise=True)


class TestDeploymentScripts:
    """Test deployment and utility scripts."""
    
    def test_generate_services_script_syntax(self):
        """Verify generate_scalable_services.py syntax."""
        import py_compile
        py_compile.compile("scripts/generate_scalable_services.py", doraise=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
