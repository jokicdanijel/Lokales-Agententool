"""
Example: Send Telegram notification from workflow
=================================================
This example shows how to integrate opena4 into workflows
"""

import asyncio

import httpx


async def send_telegram_notification(chat_id: int, message: str):
    """
    Send a Telegram notification via opena4

    Args:
        chat_id: Telegram chat ID (get via /start command)
        message: Message text to send

    Returns:
        dict: Response from opena4
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:12346/send",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10.0,
        )
        return response.json()


async def workflow_with_telegram():
    """
    Example workflow that sends Telegram notifications
    """
    # Step 1: Get user's Telegram chat ID
    user_chat_id = 123456789  # Replace with real chat ID

    # Step 2: Send start notification
    result = await send_telegram_notification(user_chat_id, "🚀 *Workflow gestartet*\n\nIhr Prozess läuft...")

    if not result["success"]:
        print(f"❌ Failed to send: {result['error']}")
        return

    print(f"✓ Notification sent (message_id: {result['message_id']})")

    # Step 3: Do some work
    await asyncio.sleep(2)

    # Step 4: Send completion notification
    await send_telegram_notification(user_chat_id, "✅ *Workflow abgeschlossen*\n\nAlle Schritte erfolgreich!")

    print("✓ Workflow complete")


async def get_telegram_stats():
    """Get Telegram bot statistics"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:12346/stats")
        stats = response.json()

        print("\n📊 Telegram Stats:")
        print(f"  Total Chats: {stats['total_chats']}")
        print(f"  Total Messages: {stats['total_messages']}")
        print(f"  Messages Today: {stats['messages_today']}")


async def get_recent_messages(chat_id: int, limit: int = 10):
    """Get recent messages from a chat"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:12346/messages/{chat_id}", params={"limit": limit, "offset": 0})
        data = response.json()

        print(f"\n💬 Recent Messages (Chat {chat_id}):")
        for msg in data["messages"][:5]:  # Show first 5
            direction = "→" if msg["direction"] == "outgoing" else "←"
            print(f"  {direction} {msg['text'][:50]}...")


if __name__ == "__main__":
    # Run example workflow
    asyncio.run(workflow_with_telegram())

    # Get stats
    asyncio.run(get_telegram_stats())

    # Get messages (replace with real chat ID)
    # asyncio.run(get_recent_messages(123456789))
