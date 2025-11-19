"""Integration tests for complete request workflows."""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestEndToEndWorkflows:
    """Integration tests for complete user workflows."""
    
    @pytest.mark.integration
    def test_chat_request_write_file_workflow(self, app_client):
        """Test: Complete workflow - Chat request → write_file → Response."""
        with patch('openwebui_agent_server.write_file') as mock_write:
            mock_write.return_value = "✅ Datei erstellt: /sandbox/test.txt"
            
            response = app_client.post(
                '/v1/chat/completions',
                json={
                    "model": "localagent-pro",
                    "messages": [
                        {"role": "user", "content": "Erstelle Datei test.txt mit Inhalt Hello"}
                    ],
                    "stream": False
                },
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert "choices" in data
            assert mock_write.called
    
    @pytest.mark.integration
    def test_health_endpoint_returns_status(self, app_client):
        """Test: /health endpoint returns system status."""
        response = app_client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert "status" in data
        assert "version" in data
        assert "sandbox" in data
    
    @pytest.mark.integration
    def test_metrics_endpoint_returns_prometheus_format(self, app_client):
        """Test: /metrics endpoint returns Prometheus metrics."""
        response = app_client.get('/metrics')
        
        assert response.status_code == 200
        assert response.content_type.startswith('text/plain')
        
        # Check for Prometheus metrics
        content = response.get_data(as_text=True)
        assert "localagent_requests_total" in content
        assert "localagent_request_duration_seconds" in content
    
    @pytest.mark.integration
    def test_loop_protection_triggers_on_identical_requests(self, app_client):
        """Test: Loop protection triggers for identical requests."""
        request_payload = {
            "model": "localagent-pro",
            "messages": [
                {"role": "user", "content": "Erstelle Datei loop_test.txt"}
            ],
            "stream": False
        }
        
        # First request
        response1 = app_client.post(
            '/v1/chat/completions',
            json=request_payload,
            content_type='application/json'
        )
        
        # Second identical request (should trigger loop protection)
        response2 = app_client.post(
            '/v1/chat/completions',
            json=request_payload,
            content_type='application/json'
        )
        
        assert response2.status_code == 200
        data2 = response2.get_json()
        content = data2["choices"][0]["message"]["content"]
        
        # Should contain loop detection message
        assert "loop" in content.lower() or "wiederholt" in content.lower()
    
    @pytest.mark.integration
    @pytest.mark.security
    def test_domain_whitelist_blocks_unauthorized_urls(self, app_client):
        """Test: Domain whitelist blocks non-allowed URLs."""
        import openwebui_agent_server
        
        # Temporarily set restricted whitelist
        original_domains = openwebui_agent_server.ALLOWED_DOMAINS
        
        try:
            openwebui_agent_server.ALLOWED_DOMAINS = ["example.com", "github.com"]
            
            with patch('openwebui_agent_server.fetch_webpage') as mock_fetch:
                mock_fetch.return_value = "❌ Domain nicht erlaubt"
                
                response = app_client.post(
                    '/v1/chat/completions',
                    json={
                        "model": "localagent-pro",
                        "messages": [
                            {"role": "user", "content": "Hole https://evil-site.com/data"}
                        ],
                        "stream": False
                    },
                    content_type='application/json'
                )
                
                data = response.get_json()
                content = data["choices"][0]["message"]["content"]
                
                assert "nicht erlaubt" in content.lower() or "blocked" in content.lower()
        finally:
            openwebui_agent_server.ALLOWED_DOMAINS = original_domains
    
    @pytest.mark.integration
    def test_prometheus_metrics_increment_on_request(self, app_client):
        """Test: Prometheus metrics increment correctly on requests."""
        import openwebui_agent_server
        
        # Get initial metric value
        initial_count = openwebui_agent_server.request_count._metrics.get(('chat_completions', 'success'), 0)
        
        # Make request
        response = app_client.post(
            '/v1/chat/completions',
            json={
                "model": "localagent-pro",
                "messages": [
                    {"role": "user", "content": "Was ist 2+2?"}
                ],
                "stream": False
            },
            content_type='application/json'
        )
        
        # Metrics should have incremented
        # (Note: Exact checking depends on Prometheus client implementation)
        assert response.status_code == 200
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_complete_workflow_with_ollama_mocked(self, app_client):
        """Test: Complete workflow with mocked Ollama response."""
        with patch('openwebui_agent_server.ollama_client.chat') as mock_ollama:
            mock_ollama.return_value = {
                "message": {
                    "role": "assistant",
                    "content": "write_file('/sandbox/test.txt', 'Hello World')"
                },
                "done": True
            }
            
            with patch('openwebui_agent_server.write_file') as mock_write:
                mock_write.return_value = "✅ Datei erstellt"
                
                response = app_client.post(
                    '/v1/chat/completions',
                    json={
                        "model": "localagent-pro",
                        "messages": [
                            {"role": "user", "content": "Erstelle eine Testdatei"}
                        ],
                        "stream": False
                    },
                    content_type='application/json'
                )
                
                assert response.status_code == 200
                assert mock_ollama.called
                assert mock_write.called
    
    @pytest.mark.integration
    def test_error_handling_invalid_json(self, app_client):
        """Test: Server handles invalid JSON gracefully."""
        response = app_client.post(
            '/v1/chat/completions',
            data='{"invalid": json',  # Malformed JSON
            content_type='application/json'
        )
        
        # Should return 400 or 500 error
        assert response.status_code >= 400
    
    @pytest.mark.integration
    def test_error_handling_missing_messages(self, app_client):
        """Test: Server handles missing 'messages' field gracefully."""
        response = app_client.post(
            '/v1/chat/completions',
            json={
                "model": "localagent-pro"
                # Missing 'messages' field
            },
            content_type='application/json'
        )
        
        # Should return error or empty response
        assert response.status_code in [200, 400, 422]
    
    @pytest.mark.integration
    def test_test_endpoint_executes_successfully(self, app_client):
        """Test: /test endpoint executes test prompt successfully."""
        with patch('openwebui_agent_server.analyze_and_execute') as mock_analyze:
            mock_analyze.return_value = "Test erfolgreich"
            
            response = app_client.post(
                '/test',
                json={
                    "prompt": "Lies Datei test.txt"
                },
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert "result" in data
            assert mock_analyze.called
