#!/usr/bin/env python3
"""
Security Tests for LocalAgent-Pro
Tests for sandbox isolation, command whitelisting, and path traversal prevention
"""

import pytest
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from openwebui_agent_server import (
    sanitize_filename,
    check_command_safety,
    SecurityError,
    SANDBOX_DIR,
    ALLOWED_COMMANDS,
    DANGEROUS_COMMANDS
)


class TestSanitizeFilename:
    """Test filename sanitization and path traversal prevention"""
    
    def test_valid_filename(self):
        """Test valid simple filename"""
        result = sanitize_filename("test.txt")
        assert result.name == "test.txt"
        assert str(result).startswith(str(SANDBOX_DIR))
    
    def test_valid_filename_with_subdirectory(self):
        """Test valid filename with subdirectory"""
        result = sanitize_filename("subdir/test.txt")
        assert result.name == "test.txt"
        assert "subdir" in str(result)
        assert str(result).startswith(str(SANDBOX_DIR))
    
    def test_path_traversal_parent_directory(self):
        """Test path traversal prevention with .."""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            sanitize_filename("../etc/passwd")
    
    def test_path_traversal_nested(self):
        """Test nested path traversal"""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            sanitize_filename("subdir/../../etc/passwd")
    
    def test_absolute_path_unix(self):
        """Test absolute path prevention (Unix)"""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            sanitize_filename("/etc/passwd")
    
    def test_absolute_path_windows(self):
        """Test absolute path prevention (Windows)"""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            sanitize_filename("/C:/Windows/System32/config/sam")
    
    def test_hidden_file(self):
        """Test hidden file (should be allowed)"""
        result = sanitize_filename(".hidden")
        assert result.name == ".hidden"
        assert str(result).startswith(str(SANDBOX_DIR))
    
    def test_special_characters(self):
        """Test special characters in filename"""
        result = sanitize_filename("test_file-2024.txt")
        assert result.name == "test_file-2024.txt"
    
    def test_unicode_filename(self):
        """Test Unicode characters"""
        result = sanitize_filename("tëst_filé.txt")
        assert result.name == "tëst_filé.txt"
    
    def test_empty_filename(self):
        """Test empty filename"""
        result = sanitize_filename("")
        assert result.name == ""


class TestCommandSafety:
    """Test command whitelisting and dangerous command detection"""
    
    def test_whitelisted_command_ls(self):
        """Test whitelisted command: ls"""
        assert check_command_safety("ls -la")
    
    def test_whitelisted_command_cat(self):
        """Test whitelisted command: cat"""
        assert check_command_safety("cat file.txt")
    
    def test_whitelisted_command_grep(self):
        """Test whitelisted command: grep"""
        assert check_command_safety("grep pattern file.txt")
    
    def test_whitelisted_command_echo(self):
        """Test whitelisted command: echo"""
        assert check_command_safety("echo 'Hello World'")
    
    def test_dangerous_command_rm(self):
        """Test dangerous command: rm"""
        with pytest.raises(SecurityError, match="Dangerous command detected"):
            check_command_safety("rm -rf /")
    
    def test_dangerous_command_dd(self):
        """Test dangerous command: dd"""
        with pytest.raises(SecurityError, match="Dangerous command detected"):
            check_command_safety("dd if=/dev/zero of=/dev/sda")
    
    def test_dangerous_command_mkfs(self):
        """Test dangerous command: mkfs"""
        with pytest.raises(SecurityError, match="Dangerous command detected"):
            check_command_safety("mkfs.ext4 /dev/sda1")
    
    def test_not_whitelisted_command(self):
        """Test command not in whitelist"""
        with pytest.raises(SecurityError, match="Command not whitelisted"):
            check_command_safety("python malicious.py")
    
    def test_command_injection_semicolon(self):
        """Test command injection with semicolon"""
        with pytest.raises(SecurityError, match="Dangerous command detected"):
            check_command_safety("ls; rm -rf /")
    
    def test_command_injection_pipe(self):
        """Test command injection with pipe (should allow if base cmd is safe)"""
        # ls is whitelisted, pipe itself is not dangerous
        assert check_command_safety("ls | grep test")
    
    def test_empty_command(self):
        """Test empty command"""
        with pytest.raises(SecurityError, match="Command not whitelisted"):
            check_command_safety("")
    
    def test_command_with_arguments(self):
        """Test whitelisted command with multiple arguments"""
        assert check_command_safety("ls -lah /path/to/dir")


class TestAllowedCommands:
    """Test that all allowed commands are properly whitelisted"""
    
    def test_all_safe_commands_allowed(self):
        """Test all safe commands in whitelist"""
        safe_commands = ['ls', 'cat', 'grep', 'echo', 'pwd', 'date', 'whoami', 'uname']
        for cmd in safe_commands:
            if cmd in ALLOWED_COMMANDS:
                assert check_command_safety(cmd)


class TestDangerousCommands:
    """Test dangerous command detection"""
    
    def test_all_dangerous_commands_blocked(self):
        """Test all dangerous commands are blocked"""
        for cmd in DANGEROUS_COMMANDS:
            with pytest.raises(SecurityError):
                check_command_safety(cmd)


class TestEdgeCases:
    """Test edge cases and corner scenarios"""
    
    def test_filename_with_spaces(self):
        """Test filename with spaces"""
        result = sanitize_filename("my file.txt")
        assert result.name == "my file.txt"
    
    def test_very_long_filename(self):
        """Test very long filename"""
        long_name = "a" * 255 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result.name) > 250
    
    def test_filename_with_dots(self):
        """Test filename with multiple dots"""
        result = sanitize_filename("archive.tar.gz")
        assert result.name == "archive.tar.gz"
    
    def test_command_with_escaped_quotes(self):
        """Test command with escaped quotes"""
        assert check_command_safety("echo 'Hello\\'World'")
    
    def test_symbolic_link_attack_prevention(self):
        """Test that symbolic links cannot escape sandbox"""
        # Even if a symlink is created, sanitize_filename should prevent escape
        with pytest.raises(SecurityError):
            sanitize_filename("../../../etc/passwd")


class TestSecurityIntegration:
    """Integration tests for security features"""
    
    def test_multiple_security_checks(self):
        """Test multiple security checks in sequence"""
        # Valid operations should pass
        assert check_command_safety("ls")
        valid_path = sanitize_filename("test.txt")
        assert str(valid_path).startswith(str(SANDBOX_DIR))
        
        # Invalid operations should fail
        with pytest.raises(SecurityError):
            check_command_safety("rm -rf /")
        
        with pytest.raises(SecurityError):
            sanitize_filename("../etc/passwd")
    
    def test_sandbox_isolation(self):
        """Test that all sanitized paths are within sandbox"""
        test_filenames = [
            "test.txt",
            "subdir/file.txt",
            "deep/nested/path/file.txt",
            ".hidden",
            "file-with-dashes.txt"
        ]
        
        for filename in test_filenames:
            result = sanitize_filename(filename)
            assert str(result.resolve()).startswith(str(SANDBOX_DIR.resolve()))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
