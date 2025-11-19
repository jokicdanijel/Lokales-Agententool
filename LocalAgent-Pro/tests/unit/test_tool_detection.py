"""Unit tests for tool detection and analyze_and_execute logic."""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestToolDetection:
    """Test analyze_and_execute() tool detection logic."""
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.write_file')
    def test_detect_write_file_german_create(self, mock_write):
        """Test: 'Erstelle Datei test.txt...' detects write_file."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_write.return_value = "Datei erstellt"
        result = analyze_and_execute("Erstelle Datei test.txt mit Inhalt Hello")
        
        assert mock_write.called
        assert "test.txt" in mock_write.call_args[0][0]
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.write_file')
    def test_detect_write_file_german_write(self, mock_write):
        """Test: 'Schreibe in Datei...' detects write_file."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_write.return_value = "Datei geschrieben"
        result = analyze_and_execute("Schreibe in Datei output.txt: Test Content")
        
        assert mock_write.called
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.read_file')
    def test_detect_read_file_german(self, mock_read):
        """Test: 'Lies Datei...' detects read_file."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_read.return_value = "File content"
        result = analyze_and_execute("Lies Datei config.yaml")
        
        assert mock_read.called
        assert "config.yaml" in mock_read.call_args[0][0]
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.read_file')
    def test_detect_read_file_german_show(self, mock_read):
        """Test: 'Zeige Datei...' detects read_file."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_read.return_value = "File content"
        result = analyze_and_execute("Zeige mir den Inhalt von README.md")
        
        assert mock_read.called
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.delete_file')
    def test_detect_delete_file_german(self, mock_delete):
        """Test: 'Lösche Datei...' detects delete_file."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_delete.return_value = "Datei gelöscht"
        result = analyze_and_execute("Lösche Datei old_file.txt")
        
        assert mock_delete.called
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.run_shell')
    def test_detect_shell_command_explicit_trigger(self, mock_shell):
        """Test: 'SHELL: ls -la' triggers run_shell."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_shell.return_value = "total 8\ndrwxr-xr-x..."
        result = analyze_and_execute("SHELL: ls -la")
        
        assert mock_shell.called
        assert "ls -la" in mock_shell.call_args[0][0]
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.run_shell')
    def test_detect_shell_command_run_trigger(self, mock_shell):
        """Test: 'RUN: pwd' triggers run_shell."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_shell.return_value = "/home/user"
        result = analyze_and_execute("RUN: pwd")
        
        assert mock_shell.called
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.fetch_webpage')
    def test_detect_fetch_with_url(self, mock_fetch):
        """Test: 'Hole URL https://example.com' detects fetch_webpage."""
        from openwebui_agent_execute import analyze_and_execute
        
        mock_fetch.return_value = "<html>Content</html>"
        result = analyze_and_execute("Hole den Inhalt von https://example.com")
        
        assert mock_fetch.called
        assert "example.com" in mock_fetch.call_args[0][0]
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.list_files')
    def test_detect_list_files_german(self, mock_list):
        """Test: 'Liste Dateien...' detects list_files."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_list.return_value = "file1.txt\nfile2.txt"
        result = analyze_and_execute("Liste alle Dateien in /home/user")
        
        assert mock_list.called
    
    @pytest.mark.unit
    def test_no_tool_detected_simple_text(self):
        """Test: Simple text input returns 'Keine Tool-Aktion erkannt'."""
        from openwebui_agent_server import analyze_and_execute
        
        result = analyze_and_execute("Was ist die Hauptstadt von Deutschland?")
        
        assert "Keine Tool-Aktion erkannt" in result or "kein Tool" in result.lower()
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.write_file')
    def test_multiple_files_in_request(self, mock_write):
        """Test: Multiple file operations in one request."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_write.return_value = "Datei erstellt"
        prompt = "Erstelle test1.txt und test2.txt mit Inhalt A und B"
        result = analyze_and_execute(prompt)
        
        # Should detect at least one write operation
        assert mock_write.called
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.write_file')
    def test_file_path_with_spaces(self, mock_write):
        """Test: File path with spaces is handled correctly."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_write.return_value = "Datei erstellt"
        result = analyze_and_execute("Erstelle Datei 'my file.txt' mit Inhalt Test")
        
        assert mock_write.called
    
    @pytest.mark.unit
    @patch('openwebui_agent_server.read_file')
    def test_absolute_path_detection(self, mock_read):
        """Test: Absolute path is detected correctly."""
        from openwebui_agent_server import analyze_and_execute
        
        mock_read.return_value = "Content"
        result = analyze_and_execute("Lies /home/user/config.yaml")
        
        assert mock_read.called
        assert "/home/user/config.yaml" in mock_read.call_args[0][0]
