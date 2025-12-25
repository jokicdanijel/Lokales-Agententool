import json
import sqlite3

db = "/var/lib/docker/volumes/n8n_n8n_data/_data/database.sqlite"
conn = sqlite3.connect(db)
cur = conn.cursor()

nodes = [
    {
        "parameters": {"httpMethod": "POST", "path": "telegram-webhook", "responseMode": "lastNode"},
        "name": "Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 1,
        "position": [250, 300],
        "id": "376ec3f5-ab15-4640-94a4-838641cb2a4c",
    },
    {
        "parameters": {
            "values": {
                "string": [
                    {"name": "chat_id", "value": '={{$json["chat_id"]}}'},
                    {"name": "text", "value": '={{$json["message"]}}'},
                ]
            },
            "options": {},
        },
        "name": "Set",
        "type": "n8n-nodes-base.set",
        "typeVersion": 1,
        "position": [450, 300],
        "id": "cefa71c3-e276-4b0e-ab99-d324ab5923bf",
    },
    {
        "parameters": {
            "requestMethod": "POST",
            "url": "https://httpbin.org/post",
            "jsonParameters": True,
            "options": {},
            "bodyParametersJson": '={"chat_id": {{$json["chat_id"]}}, "text": "{{$json["text"]}}"}',
        },
        "name": "Telegram",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 1,
        "position": [650, 300],
        "id": "e4aff216-dc93-42a0-959d-44e3d17d8f10",
    },
]

nodes_json = json.dumps(nodes, separators=(",", ":"))

cur.execute("UPDATE workflow_entity SET nodes = ? WHERE id = ?", (nodes_json, "auto_telegram_1"))
cur.execute("UPDATE workflow_history SET nodes = ? WHERE versionId='1' AND workflowId='auto_telegram_1'", (nodes_json,))
conn.commit()
conn.close()
print("Updated nodes in DB")
