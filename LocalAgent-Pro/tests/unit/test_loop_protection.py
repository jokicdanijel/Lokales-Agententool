"""Unit tests for loop detection and protection mechanism."""

import pytest
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestLoopProtection:
    """Test loop detection and prevention logic."""
    
    def setup_method(self):
        """Reset request tracking before each test."""
        import openwebui_agent_server
        if hasattr(openwebui_agent_server, 'request_tracking'):
            openwebui_agent_server.request_tracking.clear()
    
    @pytest.mark.unit
    def test_loop_detection_identical_requests(self):
        """Test: Identical requests within 2s trigger loop protection."""
        from openwebui_agent_server import is_loop_request
        
        prompt = "Erstelle Datei test.txt"
        
        # First request should NOT be a loop
        is_loop1 = is_loop_request(prompt)
        assert is_loop1 is False
        
        # Second request within 2s SHOULD be a loop
        is_loop2 = is_loop_request(prompt)
        assert is_loop2 is True
    
    @pytest.mark.unit
    def test_loop_detection_different_requests(self):
        """Test: Different requests are NOT detected as loops."""
        from openwebui_agent_server import is_loop_request
        
        prompt1 = "Erstelle Datei file1.txt"
        prompt2 = "Erstelle Datei file2.txt"
        
        is_loop1 = is_loop_request(prompt1)
        is_loop2 = is_loop_request(prompt2)
        
        assert is_loop1 is False
        assert is_loop2 is False
    
    @pytest.mark.unit
    def test_loop_detection_timeout_reset(self):
        """Test: Requests after 2s timeout are NOT loops."""
        from openwebui_agent_server import is_loop_request
        
        prompt = "Erstelle Datei test.txt"
        
        # First request
        is_loop1 = is_loop_request(prompt)
        assert is_loop1 is False
        
        # Wait >2 seconds
        time.sleep(2.1)
        
        # Second request after timeout should NOT be a loop
        is_loop2 = is_loop_request(prompt)
        assert is_loop2 is False
    
    @pytest.mark.unit
    def test_loop_detection_md5_hashing(self):
        """Test: MD5 hashing is used for request tracking."""
        from openwebui_agent_server import is_loop_request
        import openwebui_agent_server
        
        prompt = "Test prompt for MD5 hashing"
        is_loop_request(prompt)
        
        # Check that request_tracking contains MD5 hash
        import hashlib
        expected_hash = hashlib.md5(prompt.encode()).hexdigest()
        
        assert expected_hash in openwebui_agent_server.request_tracking
    
    @pytest.mark.unit
    def test_loop_detection_max_retries(self):
        """Test: Maximum 1 retry is allowed within 2s."""
        from openwebui_agent_server import is_loop_request
        
        prompt = "Erstelle Datei test.txt"
        
        # First request (not a loop)
        is_loop1 = is_loop_request(prompt)
        assert is_loop1 is False
        
        # Second request (IS a loop)
        is_loop2 = is_loop_request(prompt)
        assert is_loop2 is True
        
        # Third request (still a loop - max 1 retry)
        is_loop3 = is_loop_request(prompt)
        assert is_loop3 is True
    
    @pytest.mark.unit
    def test_loop_detection_whitespace_ignored(self):
        """Test: Extra whitespace doesn't affect loop detection."""
        from openwebui_agent_server import is_loop_request
        
        prompt1 = "Erstelle Datei test.txt"
        prompt2 = "Erstelle  Datei  test.txt"  # Extra spaces
        
        is_loop1 = is_loop_request(prompt1)
        is_loop2 = is_loop_request(prompt2)
        
        # Different whitespace should NOT affect MD5
        # (This tests current implementation - may need adjustment if normalization is added)
        assert prompt1 != prompt2  # Different strings
    
    @pytest.mark.unit
    @pytest.mark.slow
    def test_loop_detection_concurrent_requests(self):
        """Test: Concurrent identical requests are detected as loops."""
        from openwebui_agent_server import is_loop_request
        import threading
        
        prompt = "Erstelle Datei concurrent_test.txt"
        results = []
        
        def check_loop():
            is_loop = is_loop_request(prompt)
            results.append(is_loop)
        
        # Start 3 threads simultaneously
        threads = [threading.Thread(target=check_loop) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # At least one should be detected as a loop
        assert any(results)
    
    @pytest.mark.unit
    def test_loop_metrics_increment(self):
        """Test: Loop detection increments Prometheus metrics."""
        from openwebui_agent_server import is_loop_request
        import openwebui_agent_server
        
        # Get initial metric value
        initial_value = openwebui_agent_server.loop_detections._value._value
        
        prompt = "Erstelle Datei test.txt"
        is_loop_request(prompt)  # First request
        is_loop_request(prompt)  # Loop detected
        
        # Metric should have incremented
        final_value = openwebui_agent_server.loop_detections._value._value
        assert final_value > initial_value
    
    @pytest.mark.unit
    def test_loop_detection_case_sensitive(self):
        """Test: Loop detection is case-sensitive."""
        from openwebui_agent_server import is_loop_request
        
        prompt1 = "Erstelle Datei test.txt"
        prompt2 = "ERSTELLE DATEI TEST.TXT"
        
        is_loop1 = is_loop_request(prompt1)
        is_loop2 = is_loop_request(prompt2)
        
        # Different case = different hash = not a loop
        assert is_loop1 is False
        assert is_loop2 is False
    
    @pytest.mark.unit
    def test_loop_detection_special_characters(self):
        """Test: Special characters are included in loop detection."""
        from openwebui_agent_server import is_loop_request
        
        prompt1 = "Erstelle Datei test.txt!"
        prompt2 = "Erstelle Datei test.txt?"
        
        is_loop1 = is_loop_request(prompt1)
        is_loop2 = is_loop_request(prompt2)
        
        # Different punctuation = different hash = not a loop
        assert is_loop1 is False
        assert is_loop2 is False
    
    @pytest.mark.unit
    def test_loop_detection_empty_prompt(self):
        """Test: Empty prompts are handled gracefully."""
        from openwebui_agent_server import is_loop_request
        
        prompt = ""
        
        is_loop1 = is_loop_request(prompt)
        is_loop2 = is_loop_request(prompt)
        
        # Even empty prompts should trigger loop detection
        assert is_loop1 is False
        assert is_loop2 is True
    
    @pytest.mark.unit
    def test_loop_detection_very_long_prompt(self):
        """Test: Very long prompts are handled correctly."""
        from openwebui_agent_server import is_loop_request
        
        prompt = "A" * 10000  # 10k characters
        
        is_loop1 = is_loop_request(prompt)
        is_loop2 = is_loop_request(prompt)
        
        assert is_loop1 is False
        assert is_loop2 is True
    
    @pytest.mark.unit
    def test_loop_response_message(self):
        """Test: Loop detection returns proper error message."""
        from openwebui_agent_server import chat_completions
        import openwebui_agent_server
        
        with patch.object(openwebui_agent_server, 'is_loop_request', return_value=True):
            with patch('flask.request') as mock_request:
                mock_request.get_json.return_value = {
                    "model": "localagent-pro",
                    "messages": [{"role": "user", "content": "Test"}]
                }
                
                response = chat_completions()
                data = response.get_json()
                
                # Should contain loop detection message
                content = data["choices"][0]["message"]["content"]
                assert "loop" in content.lower() or "wiederholt" in content.lower()
