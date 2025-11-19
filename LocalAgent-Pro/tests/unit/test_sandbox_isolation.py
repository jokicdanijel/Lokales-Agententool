"""Unit tests for sandbox isolation and file operations."""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestSandboxIsolation:
    """Test sandbox file path resolution and isolation."""
    
    def setup_method(self):
        """Setup temporary sandbox directory."""
        self.temp_sandbox = tempfile.mkdtemp(prefix="test_sandbox_")
        self.original_sandbox = None
    
    def teardown_method(self):
        """Cleanup temporary sandbox."""
        if Path(self.temp_sandbox).exists():
            shutil.rmtree(self.temp_sandbox, ignore_errors=True)
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.SANDBOX', True)
    @patch('openwebui_agent_server.SANDBOX_PATH')
    def test_sandbox_path_resolution(self, mock_sandbox_path):
        """Test: Relative paths are resolved to sandbox."""
        from openwebui_agent_server import resolve_path
        
        mock_sandbox_path.__str__ = lambda self: self.temp_sandbox
        mock_sandbox_path.__truediv__ = lambda self, other: Path(self.temp_sandbox) / other
        
        result = resolve_path("test.txt")
        
        assert str(self.temp_sandbox) in str(result)
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.SANDBOX', True)
    @patch('openwebui_agent_server.SANDBOX_PATH')
    def test_sandbox_prevents_absolute_path_escape(self, mock_sandbox_path):
        """Test: Absolute paths outside sandbox are blocked."""
        from openwebui_agent_server import resolve_path
        
        mock_sandbox_path.__str__ = lambda self: self.temp_sandbox
        
        # Try to access /etc/passwd (outside sandbox)
        result = resolve_path("/etc/passwd")
        
        # Should still resolve to sandbox
        assert str(self.temp_sandbox) in str(result)
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.SANDBOX', True)
    @patch('openwebui_agent_server.SANDBOX_PATH')
    def test_sandbox_prevents_parent_directory_escape(self, mock_sandbox_path):
        """Test: Parent directory traversal ../../ is blocked."""
        from openwebui_agent_server import resolve_path
        
        mock_sandbox_path.__str__ = lambda self: self.temp_sandbox
        
        result = resolve_path("../../etc/passwd")
        
        # Should resolve to sandbox
        assert str(self.temp_sandbox) in str(result)
    
    @pytest.mark.unit
    def test_write_file_creates_in_sandbox(self, temp_sandbox):
        """Test: write_file creates files in sandbox directory."""
        from openwebui_agent_server import write_file
        import openwebui_agent_server
        
        # Temporarily override sandbox path
        original_sandbox_path = openwebui_agent_server.SANDBOX_PATH
        original_sandbox = openwebui_agent_server.SANDBOX
        
        try:
            openwebui_agent_server.SANDBOX = True
            openwebui_agent_server.SANDBOX_PATH = temp_sandbox
            
            result = write_file("test_file.txt", "Hello World")
            
            # Check file exists in sandbox
            created_file = temp_sandbox / "test_file.txt"
            assert created_file.exists()
            assert created_file.read_text() == "Hello World"
        finally:
            openwebui_agent_server.SANDBOX_PATH = original_sandbox_path
            openwebui_agent_server.SANDBOX = original_sandbox
    
    @pytest.mark.unit
    def test_read_file_reads_from_sandbox(self, temp_sandbox):
        """Test: read_file reads files from sandbox directory."""
        from openwebui_agent_server import read_file
        import openwebui_agent_server
        
        # Create test file
        test_file = temp_sandbox / "read_test.txt"
        test_file.write_text("Test Content")
        
        original_sandbox_path = openwebui_agent_server.SANDBOX_PATH
        original_sandbox = openwebui_agent_server.SANDBOX
        
        try:
            openwebui_agent_server.SANDBOX = True
            openwebui_agent_server.SANDBOX_PATH = temp_sandbox
            
            result = read_file("read_test.txt")
            
            assert "Test Content" in result
        finally:
            openwebui_agent_server.SANDBOX_PATH = original_sandbox_path
            openwebui_agent_server.SANDBOX = original_sandbox
    
    @pytest.mark.unit
    def test_delete_file_deletes_from_sandbox(self, temp_sandbox):
        """Test: delete_file removes files from sandbox directory."""
        from openwebui_agent_server import delete_file
        import openwebui_agent_server
        
        # Create test file
        test_file = temp_sandbox / "delete_test.txt"
        test_file.write_text("To be deleted")
        
        original_sandbox_path = openwebui_agent_server.SANDBOX_PATH
        original_sandbox = openwebui_agent_server.SANDBOX
        
        try:
            openwebui_agent_server.SANDBOX = True
            openwebui_agent_server.SANDBOX_PATH = temp_sandbox
            
            result = delete_file("delete_test.txt")
            
            assert not test_file.exists()
            assert "gelöscht" in result.lower() or "deleted" in result.lower()
        finally:
            openwebui_agent_server.SANDBOX_PATH = original_sandbox_path
            openwebui_agent_server.SANDBOX = original_sandbox
    
    @pytest.mark.unit
    def test_list_files_lists_sandbox_files(self, temp_sandbox):
        """Test: list_files lists files in sandbox directory."""
        from openwebui_agent_server import list_files
        import openwebui_agent_server
        
        # Create test files
        (temp_sandbox / "file1.txt").write_text("A")
        (temp_sandbox / "file2.txt").write_text("B")
        (temp_sandbox / "file3.log").write_text("C")
        
        original_sandbox_path = openwebui_agent_server.SANDBOX_PATH
        original_sandbox = openwebui_agent_server.SANDBOX
        
        try:
            openwebui_agent_server.SANDBOX = True
            openwebui_agent_server.SANDBOX_PATH = temp_sandbox
            
            result = list_files(str(temp_sandbox))
            
            assert "file1.txt" in result
            assert "file2.txt" in result
            assert "file3.log" in result
        finally:
            openwebui_agent_server.SANDBOX_PATH = original_sandbox_path
            openwebui_agent_server.SANDBOX = original_sandbox
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_sandbox_prevents_symlink_escape(self, temp_sandbox):
        """Test: Symlinks cannot escape sandbox."""
        import openwebui_agent_server
        
        # Create symlink to /etc
        symlink_path = temp_sandbox / "etc_link"
        try:
            symlink_path.symlink_to("/etc")
        except OSError:
            pytest.skip("Cannot create symlinks (permission issue)")
        
        original_sandbox_path = openwebui_agent_server.SANDBOX_PATH
        original_sandbox = openwebui_agent_server.SANDBOX
        
        try:
            openwebui_agent_server.SANDBOX = True
            openwebui_agent_server.SANDBOX_PATH = temp_sandbox
            
            # Try to read through symlink
            from openwebui_agent_server import read_file
            result = read_file("etc_link/passwd")
            
            # Should fail or return empty/error
            assert "passwd" not in result or "Fehler" in result
        finally:
            openwebui_agent_server.SANDBOX_PATH = original_sandbox_path
            openwebui_agent_server.SANDBOX = original_sandbox
    
    @pytest.mark.unit
    def test_sandbox_creates_directory_if_missing(self):
        """Test: Sandbox directory is created if it doesn't exist."""
        from openwebui_agent_server import write_file
        import openwebui_agent_server
        
        # Create non-existent sandbox path
        new_sandbox = Path(tempfile.gettempdir()) / f"test_sandbox_{id(self)}"
        
        original_sandbox_path = openwebui_agent_server.SANDBOX_PATH
        original_sandbox = openwebui_agent_server.SANDBOX
        
        try:
            openwebui_agent_server.SANDBOX = True
            openwebui_agent_server.SANDBOX_PATH = new_sandbox
            
            # This should create the sandbox directory
            result = write_file("test.txt", "Content")
            
            assert new_sandbox.exists()
            assert (new_sandbox / "test.txt").exists()
        finally:
            openwebui_agent_server.SANDBOX_PATH = original_sandbox_path
            openwebui_agent_server.SANDBOX = original_sandbox
            if new_sandbox.exists():
                shutil.rmtree(new_sandbox, ignore_errors=True)
