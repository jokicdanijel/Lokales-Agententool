"""
tests/test_ops_and_register.py — Testing for ops.sh and register_agents.py

Tests:
- bin/ops.sh script syntax and commands
- scripts/register_agents.py syntax and structure
- .env file handling for OPENAI_API_KEY
"""

import os
import subprocess
import pytest
from pathlib import Path


class TestOpsScript:
    """Test bin/ops.sh script."""
    
    def test_ops_script_exists(self):
        """Verify bin/ops.sh exists."""
        ops_script = Path("bin/ops.sh")
        assert ops_script.exists(), "bin/ops.sh not found"
    
    def test_ops_script_executable(self):
        """Verify bin/ops.sh is executable."""
        ops_script = Path("bin/ops.sh")
        assert os.access(ops_script, os.X_OK), "bin/ops.sh is not executable"
    
    def test_ops_script_syntax(self):
        """Verify bin/ops.sh has valid bash syntax."""
        result = subprocess.run(
            ["bash", "-n", "bin/ops.sh"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error in bin/ops.sh: {result.stderr}"
    
    def test_ops_help_command(self):
        """Test bin/ops.sh help command."""
        result = subprocess.run(
            ["bash", "bin/ops.sh", "help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        assert "ELION Hyper-Dashboard OPS" in result.stdout, "Help text not found"
        assert "start" in result.stdout, "start command not in help"
        assert "stop" in result.stdout, "stop command not in help"
        assert "agents:register" in result.stdout, "agents:register command not in help"
    
    def test_ops_start_validates_openai_key(self):
        """Test that start command validates OPENAI_API_KEY."""
        result = subprocess.run(
            ["timeout", "5", "bash", "bin/ops.sh", "start"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should mention OPENAI_API_KEY
        output = result.stdout + result.stderr
        assert "OPENAI_API_KEY" in output, "Start command doesn't check OPENAI_API_KEY"


class TestRegisterAgentsScript:
    """Test scripts/register_agents.py script."""
    
    def test_register_script_exists(self):
        """Verify scripts/register_agents.py exists."""
        script = Path("scripts/register_agents.py")
        assert script.exists(), "scripts/register_agents.py not found"
    
    def test_register_script_executable(self):
        """Verify scripts/register_agents.py is executable."""
        script = Path("scripts/register_agents.py")
        assert os.access(script, os.X_OK), "scripts/register_agents.py is not executable"
    
    def test_register_script_has_shebang(self):
        """Verify scripts/register_agents.py has proper shebang."""
        script = Path("scripts/register_agents.py")
        with open(script, 'r') as f:
            first_line = f.readline()
        assert first_line.startswith("#!/usr/bin/env python3"), \
            f"Invalid shebang: {first_line}"
    
    def test_register_script_syntax(self):
        """Verify scripts/register_agents.py has valid Python syntax."""
        import py_compile
        py_compile.compile("scripts/register_agents.py", doraise=True)
    
    def test_register_script_imports(self):
        """Verify scripts/register_agents.py imports required modules."""
        script = Path("scripts/register_agents.py")
        content = script.read_text()
        
        # Check for required imports
        assert "import sys" in content, "Missing sys import"
        assert "import json" in content, "Missing json import"
        assert "import os" in content, "Missing os import"
        assert "import urllib.request" in content, "Missing urllib.request import"
    
    def test_register_script_has_token_function(self):
        """Verify scripts/register_agents.py has token() function."""
        script = Path("scripts/register_agents.py")
        content = script.read_text()
        assert "def token():" in content, "Missing token() function"
    
    def test_register_script_has_post_function(self):
        """Verify scripts/register_agents.py has post() function."""
        script = Path("scripts/register_agents.py")
        content = script.read_text()
        assert "def post(" in content, "Missing post() function"
    
    def test_register_script_registers_agents(self):
        """Verify scripts/register_agents.py registers opena1 and opena2."""
        script = Path("scripts/register_agents.py")
        content = script.read_text()
        
        # Check for agent registrations
        assert 'opena1' in content, "Missing opena1 registration"
        assert 'opena2' in content, "Missing opena2 registration"
        assert '12344' in content, "Missing opena1 port (12344)"
        assert '12345' in content, "Missing opena2 port (12345)"


class TestEnvironmentConfiguration:
    """Test .env file configuration."""
    
    def test_env_file_exists(self):
        """Verify .env file exists."""
        env_file = Path(".env")
        assert env_file.exists(), ".env file not found"
    
    def test_env_has_dashboard_token(self):
        """Verify .env has DASHBOARD_ADMIN_TOKEN."""
        env_file = Path(".env")
        content = env_file.read_text()
        assert "DASHBOARD_ADMIN_TOKEN=" in content, \
            "DASHBOARD_ADMIN_TOKEN not found in .env"
    
    def test_env_has_openai_key(self):
        """Verify .env has OPENAI_API_KEY."""
        env_file = Path(".env")
        content = env_file.read_text()
        assert "OPENAI_API_KEY=" in content, \
            "OPENAI_API_KEY not found in .env"
    
    def test_env_example_exists(self):
        """Verify .env.example exists as template."""
        env_example = Path(".env.example")
        assert env_example.exists(), ".env.example not found"


class TestScriptsIntegration:
    """Test integration between ops.sh and register_agents.py."""
    
    def test_ops_can_call_register_script(self):
        """Verify bin/ops.sh can delegate to scripts/register_agents.py."""
        ops_content = Path("bin/ops.sh").read_text()
        assert "register_agents.py" in ops_content, \
            "ops.sh doesn't reference register_agents.py"
    
    def test_ops_agents_register_command_exists(self):
        """Verify bin/ops.sh has agents:register command."""
        ops_content = Path("bin/ops.sh").read_text()
        assert "agents:register" in ops_content, \
            "ops.sh doesn't have agents:register command"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
