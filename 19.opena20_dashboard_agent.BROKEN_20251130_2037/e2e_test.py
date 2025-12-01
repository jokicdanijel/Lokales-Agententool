#!/usr/bin/env python3
"""
E2E Test Suite für opena20 Dashboard Agent
PORTIER 3.0 Konform | Enterprise Grade Testing

Tests:
- Health Endpoints
- Authentication
- Agent Status Aggregation
- SSE Event Streaming
- HTML Workflow Engine
- Social Media Automation
- Safepoint Client Integration
- Error Handling
- Performance Benchmarks
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any
import subprocess
import signal
import os

class OpenaE2ETest:
    """Comprehensive E2E Test Suite for opena20"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:12349"
        self.token = "c899b90d-faf8-485b-afa4-078357cf5313"
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.results = []
        self.dashboard_process = None
    
    async def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": timestamp
        }
        
        self.results.append(result)
        print(f"[{timestamp}] {status} {test_name}")
        if details and not success:
            print(f"    Details: {details}")
    
    def start_dashboard_if_needed(self):
        """Start dashboard if not running"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200:
                print("📊 Dashboard already running")
                return False
        except:
            pass
        
        print("🚀 Starting dashboard for testing...")
        self.dashboard_process = subprocess.Popen([
            sys.executable, "main_dashboard_final.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for startup
        for i in range(10):
            try:
                import requests
                response = requests.get(f"{self.base_url}/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Dashboard started successfully")
                    return True
            except:
                time.sleep(1)
        
        print("❌ Failed to start dashboard")
        return False
    
    def cleanup(self):
        """Cleanup test resources"""
        if self.dashboard_process:
            print("🛑 Stopping test dashboard...")
            self.dashboard_process.terminate()
            try:
                self.dashboard_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.dashboard_process.kill()
    
    async def test_health_endpoint(self):
        """Test basic health endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        success = (
                            data.get("status") == "ok" and
                            data.get("service") == "opena20" and
                            data.get("port") == 12349
                        )
                        await self.log_result("Health Endpoint", success, 
                                            f"Status: {data.get('status')}, Port: {data.get('port')}")
                    else:
                        await self.log_result("Health Endpoint", False, f"HTTP {response.status}")
        except Exception as e:
            await self.log_result("Health Endpoint", False, str(e))
    
    async def test_authentication(self):
        """Test Bearer token authentication"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test without token
                async with session.get(f"{self.base_url}/api/agents") as response:
                    no_auth_fail = response.status == 401
                
                # Test with valid token
                async with session.get(f"{self.base_url}/api/agents", 
                                     headers=self.headers) as response:
                    auth_success = response.status == 200
                
                # Test with invalid token
                bad_headers = {"Authorization": "Bearer invalid-token"}
                async with session.get(f"{self.base_url}/api/agents",
                                     headers=bad_headers) as response:
                    bad_auth_fail = response.status == 401
                
                success = no_auth_fail and auth_success and bad_auth_fail
                await self.log_result("Authentication", success,
                                    f"No auth: {no_auth_fail}, Valid: {auth_success}, Invalid: {bad_auth_fail}")
        
        except Exception as e:
            await self.log_result("Authentication", False, str(e))
    
    async def test_agent_status_aggregation(self):
        """Test agent status aggregation"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/status/all",
                                     headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        success = (
                            "total" in data and
                            "online" in data and
                            "offline" in data and
                            "agents" in data and
                            "timestamp" in data and
                            isinstance(data["agents"], list)
                        )
                        await self.log_result("Agent Status Aggregation", success,
                                            f"Total: {data.get('total')}, Online: {data.get('online')}")
                    else:
                        await self.log_result("Agent Status Aggregation", False, f"HTTP {response.status}")
        
        except Exception as e:
            await self.log_result("Agent Status Aggregation", False, str(e))
    
    async def test_sse_events(self):
        """Test Server-Sent Events"""
        try:
            # This is a simplified test - real SSE testing would be more complex
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/sse/events") as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        success = 'text/event-stream' in content_type
                        await self.log_result("SSE Events", success, 
                                            f"Content-Type: {content_type}")
                    else:
                        await self.log_result("SSE Events", False, f"HTTP {response.status}")
        
        except Exception as e:
            await self.log_result("SSE Events", False, str(e))
    
    async def test_html_workflows(self):
        """Test HTML workflow engine"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test available workflows
                async with session.get(f"{self.base_url}/api/html/workflows/available",
                                     headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        workflows_available = "workflows" in data and len(data["workflows"]) > 0
                        
                        # Test workflow execution
                        workflow_payload = {
                            "workflow_name": "html_systems_discovery",
                            "inputs": {"test": True},
                            "mode": "async"
                        }
                        
                        async with session.post(f"{self.base_url}/api/html/workflows/execute",
                                              json=workflow_payload,
                                              headers=self.headers) as exec_response:
                            execution_success = exec_response.status == 200
                            
                            success = workflows_available and execution_success
                            await self.log_result("HTML Workflows", success,
                                                f"Available: {workflows_available}, Execute: {execution_success}")
                    else:
                        await self.log_result("HTML Workflows", False, f"HTTP {response.status}")
        
        except Exception as e:
            await self.log_result("HTML Workflows", False, str(e))
    
    async def test_social_media_automation(self):
        """Test social media automation endpoints"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test status endpoint
                async with session.get(f"{self.base_url}/api/socialmedia/status",
                                     headers=self.headers) as response:
                    status_success = response.status == 200
                
                # Test execution endpoint
                sm_payload = {
                    "workflow_name": "social_media_auto_content",
                    "platform": "test",
                    "content_type": "test"
                }
                
                async with session.post(f"{self.base_url}/api/socialmedia/execute",
                                      json=sm_payload,
                                      headers=self.headers) as exec_response:
                    exec_success = exec_response.status == 200
                
                success = status_success and exec_success
                await self.log_result("Social Media Automation", success,
                                    f"Status: {status_success}, Execute: {exec_success}")
        
        except Exception as e:
            await self.log_result("Social Media Automation", False, str(e))
    
    async def test_command_api(self):
        """Test command API (Option-2 Flow)"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test get_status command
                cmd_payload = {"action": "get_status", "params": {}}
                
                async with session.post(f"{self.base_url}/command",
                                      json=cmd_payload,
                                      headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        success = data.get("success") == True and "status" in data
                        await self.log_result("Command API", success,
                                            f"Success: {data.get('success')}")
                    else:
                        await self.log_result("Command API", False, f"HTTP {response.status}")
        
        except Exception as e:
            await self.log_result("Command API", False, str(e))
    
    async def test_performance_benchmark(self):
        """Performance benchmark test"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # Run 10 concurrent health checks
                tasks = []
                for _ in range(10):
                    task = session.get(f"{self.base_url}/health")
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Close all responses
                for resp in responses:
                    if hasattr(resp, 'close'):
                        resp.close()
                
                success = duration < 5.0  # Should complete in under 5 seconds
                await self.log_result("Performance Benchmark", success,
                                    f"10 requests in {duration:.2f}s")
        
        except Exception as e:
            await self.log_result("Performance Benchmark", False, str(e))
    
    async def run_all_tests(self):
        """Run complete E2E test suite"""
        print("🧪 Starting opena20 E2E Test Suite")
        print("=" * 50)
        
        # Start dashboard if needed
        started_dashboard = self.start_dashboard_if_needed()
        
        try:
            # Wait for startup
            if started_dashboard:
                await asyncio.sleep(3)
            
            # Run all tests
            await self.test_health_endpoint()
            await self.test_authentication() 
            await self.test_agent_status_aggregation()
            await self.test_sse_events()
            await self.test_html_workflows()
            await self.test_social_media_automation()
            await self.test_command_api()
            await self.test_performance_benchmark()
            
            # Generate report
            self.generate_report()
            
        finally:
            if started_dashboard:
                self.cleanup()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 50)
        print("📊 E2E Test Report")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Write JSON report
        with open("e2e_test_report.json", "w") as f:
            json.dump({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.results
            }, f, indent=2)
        
        print("📄 Detailed report saved to: e2e_test_report.json")
        
        # Exit with proper code
        sys.exit(0 if failed_tests == 0 else 1)

async def main():
    """Main entry point"""
    test_suite = OpenaE2ETest()
    
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\n🛑 Test interrupted")
        test_suite.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())