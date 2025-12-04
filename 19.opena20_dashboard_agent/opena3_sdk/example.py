#!/usr/bin/env python3
"""
OpenA3 SDK Usage Examples
PORTIER 3.0 Enterprise Python Client
"""

import asyncio
from opena3_sdk import OpenA3Client, CMDRequest, ChatRequest

async def main():
    """Demonstrate OpenA3 SDK usage"""
    
    # Initialize client (add Bearer token for production)
    async with OpenA3Client(
        base_url="http://127.0.0.1:12347",
        token=None,  # Add your Bearer token here
        timeout=30.0
    ) as client:
        
        print("🚀 OpenA3 SDK Demo - PORTIER 3.0")
        print("=" * 50)
        
        # 1. Health Check
        print("\n1. Health Check:")
        try:
            health = await client.health()
            print(f"   Status: {health.status}")
            print(f"   Version: {health.version}")
            print(f"   Timestamp: {health.timestamp}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 2. Native Chat (simplified)
        print("\n2. Native Chat:")
        try:
            response = await client.chat(
                prompt="Hello from SDK!",
                model="gpt-4",
                temperature=0.7
            )
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 3. CMD Dispatch (Option-2-Flow)
        print("\n3. CMD Dispatch:")
        try:
            cmd = client.create_cmd_request(
                command="chat",
                payload={"prompt": "SDK CMD test"}
            )
            result = await client.cmd_dispatch(cmd)
            print(f"   CMD ID: {cmd.request_id}")
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 4. Dispatch Ready Check
        print("\n4. Dispatch Ready:")
        try:
            status = await client.dispatch_ready()
            print(f"   Ready: {status.ready}")
            print(f"   kordp Available: {status.kordp_available}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 5. Self Test
        print("\n5. Self Test:")
        try:
            selftest = await client.selftest()
            print(f"   Overall Status: {selftest.overall_status}")
            print(f"   Tests: {len(selftest.tests)}")
            print(f"   Duration: {selftest.duration_ms}ms")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n✅ SDK Demo completed!")

if __name__ == "__main__":
    asyncio.run(main())