"""
Unit Tests for 5.opena6_browser
Tests for main agent, browser engine, and dispatcher client
"""

import unittest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import BrowserAgent
from browser_engine import BrowserEngineWrapper
from dispatcher_client import DispatcherClient, SafepointManager


class TestBrowserAgent(unittest.TestCase):
    """Test BrowserAgent class"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = BrowserAgent()

    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.agent_name, '5.opena6_browser')
        self.assertEqual(self.agent.port, 12350)
        self.assertTrue(self.agent.is_healthy)

    def test_create_session(self):
        """Test session creation"""
        session_id = self.agent.create_session()
        self.assertIsNotNone(session_id)
        self.assertTrue(session_id.startswith('sess_'))

    def test_get_session(self):
        """Test get session"""
        session_id = self.agent.create_session()
        session = self.agent.get_session(session_id)
        self.assertIsNotNone(session)
        self.assertEqual(session['status'], 'active')

    def test_execute_command_open(self):
        """Test execute open command"""
        cmd = {
            'action': 'open',
            'url': 'https://example.com',
            'session_id': self.agent.create_session()
        }
        result = self.agent.execute_command(cmd)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['action'], 'open')
        self.assertEqual(result['url'], 'https://example.com')

    def test_execute_command_missing_action(self):
        """Test execute with missing action"""
        cmd = {'url': 'https://example.com'}
        result = self.agent.execute_command(cmd)

        self.assertEqual(result['status'], 'error')
        self.assertIn('action', result['message'].lower())

    def test_execute_command_invalid_action(self):
        """Test execute with invalid action"""
        cmd = {
            'action': 'invalid_action',
            'url': 'https://example.com'
        }
        result = self.agent.execute_command(cmd)

        self.assertEqual(result['status'], 'error')
        self.assertIn('invalid', result['message'].lower())

    def test_health_status(self):
        """Test health status endpoint"""
        status = self.agent.get_health_status()

        self.assertEqual(status['status'], 'healthy')
        self.assertEqual(status['agent'], '5.opena6_browser')
        self.assertIn('startup_time', status)
        self.assertIn('active_sessions', status)

    def test_valid_actions(self):
        """Test all valid actions"""
        valid_actions = [
            'open', 'click', 'type', 'extract_text', 'extract_html',
            'query_selector', 'screenshot', 'scroll', 'wait_for'
        ]

        for action in valid_actions:
            cmd = {
                'action': action,
                'url': 'https://example.com',
                'selector': 'div.test',
                'text': 'test text'
            }
            result = self.agent.execute_command(cmd)
            self.assertIn(result['status'], ['success', 'error'])


class TestBrowserEngine(unittest.TestCase):
    """Test BrowserEngineWrapper class"""

    def setUp(self):
        """Set up test fixtures"""
        self.engine = BrowserEngineWrapper()

    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        self.assertTrue(self.engine.headless)
        self.assertEqual(self.engine.default_wait_ms, 500)
        self.assertEqual(self.engine.timeout_ms, 15000)

    def test_open_url(self):
        """Test open URL"""
        result = self.engine.open_url('https://example.com')

        self.assertEqual(result['status'], 'success')
        self.assertIn('data', result)
        self.assertEqual(result['data']['url'], 'https://example.com')

    def test_click_element(self):
        """Test click element"""
        result = self.engine.click_element('https://example.com', 'button.submit')

        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['data']['clicked'])

    def test_type_text(self):
        """Test type text"""
        result = self.engine.type_text('https://example.com', 'input#email', 'test@example.com')

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['text_length'], 16)

    def test_extract_text(self):
        """Test extract text"""
        result = self.engine.extract_text('https://example.com', 'p.description')

        self.assertEqual(result['status'], 'success')
        self.assertIn('text', result['data'])

    def test_extract_html(self):
        """Test extract HTML"""
        result = self.engine.extract_html('https://example.com', 'div.content')

        self.assertEqual(result['status'], 'success')
        self.assertIn('html', result['data'])

    def test_query_selector(self):
        """Test query selector"""
        result = self.engine.query_selector('https://example.com', 'div.item')

        self.assertEqual(result['status'], 'success')
        self.assertIn('elements', result['data'])

    def test_screenshot(self):
        """Test screenshot"""
        result = self.engine.screenshot('https://example.com')

        self.assertEqual(result['status'], 'success')
        self.assertIn('path', result['data'])

    def test_scroll(self):
        """Test scroll"""
        result = self.engine.scroll('https://example.com')

        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['data']['scrolled'])

    def test_wait_for(self):
        """Test wait for"""
        result = self.engine.wait_for('https://example.com', 'div.loaded', 5000)

        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['data']['appeared'])


class TestDispatcherClient(unittest.TestCase):
    """Test DispatcherClient class"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = DispatcherClient(agent_name='5.opena6_browser')

    def test_client_initialization(self):
        """Test client initializes correctly"""
        self.assertEqual(self.client.agent_name, '5.opena6_browser')
        self.assertIsNotNone(self.client.dispatcher_url)
        self.assertIsNotNone(self.client.archivator_url)


class TestSafepointManager(unittest.TestCase):
    """Test SafepointManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = SafepointManager()

    def test_create_cmd_safepoint(self):
        """Test create CMD safepoint"""
        cmd = {'action': 'open', 'url': 'https://example.com'}
        sp_id = self.manager.create_cmd_safepoint(cmd)

        self.assertIsNotNone(sp_id)
        self.assertTrue(sp_id.startswith('sp_'))

    def test_create_resp_safepoint(self):
        """Test create RESP safepoint"""
        result = {'status': 'success'}
        sp_id = self.manager.create_resp_safepoint('cmd_001', result)

        self.assertIsNotNone(sp_id)
        self.assertTrue(sp_id.startswith('sp_'))

    def test_get_safepoint(self):
        """Test get safepoint"""
        cmd = {'action': 'open', 'url': 'https://example.com'}
        sp_id = self.manager.create_cmd_safepoint(cmd)

        sp = self.manager.get_safepoint(sp_id)
        self.assertIsNotNone(sp)
        self.assertEqual(sp['type'], 'CMD')

    def test_list_safepoints(self):
        """Test list safepoints"""
        cmd = {'action': 'open', 'url': 'https://example.com'}
        self.manager.create_cmd_safepoint(cmd)

        sps = self.manager.list_safepoints()
        self.assertGreater(len(sps), 0)


class TestCommandSchema(unittest.TestCase):
    """Test command schema validation"""

    def test_command_structure(self):
        """Test command has correct structure"""
        cmd = {
            'action': 'open',
            'url': 'https://example.com',
            'session_id': 'sess_000001',
            'wait_ms': 500,
            'return_format': 'json'
        }

        # Validate required fields
        self.assertIn('action', cmd)
        self.assertIn('url', cmd)

        # Validate action is in enum
        valid_actions = [
            'open', 'click', 'type', 'extract_text', 'extract_html',
            'query_selector', 'screenshot', 'scroll', 'wait_for'
        ]
        self.assertIn(cmd['action'], valid_actions)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_agent_command_flow(self):
        """Test full command flow"""
        agent = BrowserAgent()

        # Create session
        session_id = agent.create_session()
        self.assertIsNotNone(session_id)

        # Execute command
        cmd = {
            'action': 'open',
            'url': 'https://example.com',
            'session_id': session_id
        }
        result = agent.execute_command(cmd)
        self.assertEqual(result['status'], 'success')

        # Check session updated
        session = agent.get_session(session_id)
        self.assertEqual(session['command_count'], 1)


def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
