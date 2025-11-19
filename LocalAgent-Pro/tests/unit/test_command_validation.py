"""Unit tests for command validation logic."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestCommandValidation:
    """Test _is_valid_command() function."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Import here to avoid issues with module loading
        import openwebui_agent_server
        self._is_valid_command = openwebui_agent_server._is_valid_command
    
    # === VALID COMMANDS ===
    
    @pytest.mark.unit
    def test_valid_ls_with_args(self):
        """Test: ls -la is valid."""
        assert self._is_valid_command("ls -la") is True
    
    @pytest.mark.unit
    def test_valid_ls_no_args(self):
        """Test: ls (standalone) is valid."""
        assert self._is_valid_command("ls") is True
    
    @pytest.mark.unit
    def test_valid_pwd(self):
        """Test: pwd is valid."""
        assert self._is_valid_command("pwd") is True
    
    @pytest.mark.unit
    def test_valid_cat_with_file(self):
        """Test: cat file.txt is valid."""
        assert self._is_valid_command("cat file.txt") is True
    
    @pytest.mark.unit
    def test_valid_echo_with_text(self):
        """Test: echo 'hello' is valid."""
        assert self._is_valid_command("echo 'hello'") is True
    
    @pytest.mark.unit
    def test_valid_grep_pattern(self):
        """Test: grep 'pattern' file.txt is valid."""
        assert self._is_valid_command("grep 'pattern' file.txt") is True
    
    @pytest.mark.unit
    def test_valid_find_command(self):
        """Test: find . -name '*.txt' is valid."""
        assert self._is_valid_command("find . -name '*.txt'") is True
    
    @pytest.mark.unit
    def test_valid_pipe_command(self):
        """Test: ls | grep test is valid (pipe)."""
        assert self._is_valid_command("ls | grep test") is True
    
    @pytest.mark.unit
    def test_valid_redirect_command(self):
        """Test: echo test > file.txt is valid (redirect)."""
        assert self._is_valid_command("echo test > file.txt") is True
    
    @pytest.mark.unit
    def test_valid_chain_command(self):
        """Test: pwd && ls is valid (chain)."""
        assert self._is_valid_command("pwd && ls") is True
    
    @pytest.mark.unit
    def test_valid_date_command(self):
        """Test: date is valid."""
        assert self._is_valid_command("date") is True
    
    @pytest.mark.unit
    def test_valid_whoami_command(self):
        """Test: whoami is valid."""
        assert self._is_valid_command("whoami") is True
    
    @pytest.mark.unit
    def test_valid_df_command(self):
        """Test: df -h is valid."""
        assert self._is_valid_command("df -h") is True
    
    @pytest.mark.unit
    def test_valid_du_command(self):
        """Test: du -sh is valid."""
        assert self._is_valid_command("du -sh") is True
    
    @pytest.mark.unit
    def test_valid_free_command(self):
        """Test: free -m is valid."""
        assert self._is_valid_command("free -m") is True
    
    @pytest.mark.unit
    def test_valid_top_command(self):
        """Test: top -n 1 is valid."""
        assert self._is_valid_command("top -n 1") is True
    
    @pytest.mark.unit
    def test_valid_ps_command(self):
        """Test: ps aux is valid."""
        assert self._is_valid_command("ps aux") is True
    
    # === INVALID COMMANDS (nur Pfade/Dateinamen) ===
    
    @pytest.mark.unit
    def test_invalid_absolute_path(self):
        """Test: /home/user/file.txt (nur Pfad) is invalid."""
        assert self._is_valid_command("/home/user/file.txt") is False
    
    @pytest.mark.unit
    def test_invalid_absolute_path_no_extension(self):
        """Test: /usr/bin/python (nur Pfad ohne Extension) is invalid."""
        assert self._is_valid_command("/usr/bin/python") is False
    
    @pytest.mark.unit
    def test_invalid_simple_filename(self):
        """Test: test.txt (nur Dateiname) is invalid."""
        assert self._is_valid_command("test.txt") is False
    
    @pytest.mark.unit
    def test_invalid_filename_with_extension(self):
        """Test: document.pdf (nur Dateiname) is invalid."""
        assert self._is_valid_command("document.pdf") is False
    
    @pytest.mark.unit
    def test_invalid_python_script(self):
        """Test: script.py (nur Dateiname) is invalid."""
        assert self._is_valid_command("script.py") is False
    
    @pytest.mark.unit
    def test_invalid_config_file(self):
        """Test: config.yaml (nur Dateiname) is invalid."""
        assert self._is_valid_command("config.yaml") is False
    
    @pytest.mark.unit
    def test_invalid_log_file(self):
        """Test: error.log (nur Dateiname) is invalid."""
        assert self._is_valid_command("error.log") is False
    
    # === EDGE CASES ===
    
    @pytest.mark.unit
    def test_edge_empty_string(self):
        """Test: Empty string is invalid."""
        assert self._is_valid_command("") is False
    
    @pytest.mark.unit
    def test_edge_only_spaces(self):
        """Test: Only spaces is invalid."""
        assert self._is_valid_command("   ") is False
    
    @pytest.mark.unit
    def test_edge_relative_path_with_extension(self):
        """Test: ./test.txt (relativer Pfad) is invalid."""
        assert self._is_valid_command("./test.txt") is False
    
    @pytest.mark.unit
    def test_edge_parent_directory_path(self):
        """Test: ../file.txt (Parent-Pfad) is invalid."""
        assert self._is_valid_command("../file.txt") is False
    
    @pytest.mark.unit
    def test_edge_command_with_special_chars(self):
        """Test: ls -la | grep '.txt' (mit Sonderzeichen) is valid."""
        assert self._is_valid_command("ls -la | grep '.txt'") is True
    
    @pytest.mark.unit
    def test_edge_command_with_quotes(self):
        """Test: echo \"hello world\" is valid."""
        assert self._is_valid_command('echo "hello world"') is True
    
    @pytest.mark.unit
    def test_edge_filename_no_extension(self):
        """Test: README (Dateiname ohne Extension) - should be invalid."""
        # README ist ein Dateiname ohne Extension und enthält keinen Punkt
        # ABER: _is_valid_command prüft '.' in cmd, also ist README ohne Punkt
        # Wir testen, ob es korrekt als ungültig erkannt wird
        result = self._is_valid_command("README")
        # Laut Funktion: Nur wenn '.' in cmd UND kein Space UND keine Pipes/Redirects
        # README hat KEIN '.', also wird es NICHT als Dateiname erkannt
        # Es muss also gegen die valid_patterns getestet werden
        # README passt zu keinem Pattern → sollte False sein
        assert result is False
    
    @pytest.mark.unit
    def test_edge_directory_name(self):
        """Test: /home/user/folder (nur Verzeichnis) is invalid."""
        assert self._is_valid_command("/home/user/folder") is False
    
    @pytest.mark.unit
    def test_edge_command_with_absolute_path_arg(self):
        """Test: cat /etc/passwd (Command mit absolutem Pfad) is valid."""
        assert self._is_valid_command("cat /etc/passwd") is True
    
    @pytest.mark.unit
    def test_edge_command_with_multiple_args(self):
        """Test: grep -r 'pattern' /var/log is valid."""
        assert self._is_valid_command("grep -r 'pattern' /var/log") is True
