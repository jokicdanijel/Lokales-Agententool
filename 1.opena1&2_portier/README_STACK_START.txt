Start:
  chmod +x ./bin/start_all.sh ./bin/stop_all.sh
  systemctl --user daemon-reload
  ./bin/start_all.sh

Stop:
  ./bin/stop_all.sh

Zugänge:
  OpenWebUI:       http://127.0.0.1:8080
  n8n:             http://127.0.0.1:12344
  Code-Generator:  http://127.0.0.1:12347/docs

Voraussetzung:
  In .env muss OPENAI_API_KEY=... gesetzt sein.
  Unllama wird nicht verwendet. Agenten laufen über OpenAI-API.


