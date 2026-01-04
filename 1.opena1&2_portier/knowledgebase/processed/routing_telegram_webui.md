# Routing - Telegram <-> OpenWebUI - Processed Core Version

## 1. Eingangspfad (Telegram → System)

### Sequenz

```
opena4 → opena2 → opena1 → opena2 → opena3/opena5/opena20
```

### Details

- **opena4** empfaengt Telegram-Message
- **opena2** erzeugt CMD-Safepoint
- **opena1** routet zu Ziel-Agent
- **opena2** erzeugt RESP-Safepoint
- **opena3/opena5/opena20** verarbeitet

## 2. Ereignisse

### Message-Types

- MSG_IN - Eingehende Nachricht
- BOT_CMD - Bot-Command
- DELIVER_IN - Zustellung
- CMD - Command-Envelope
- RESP - Response-Envelope
- UI_CMD - UI-Command
- ALERT - System-Alert
- SEND_OUT - Ausgehende Nachricht

## 3. Dedup-Mechanismus

### Key-Generation

```
key = SHA256(chat_id + message_id)
```

### Komponenten

- chat_id (Telegram Chat-ID)
- message_id (Telegram Message-ID)
- SHA-256 Hashing
- Dedupe-Index: archivp/.../DEDUP_INDEX.json

### Ablauf

1. Message empfangen
2. Key generieren
3. Index pruefen
4. Bei Treffer: No-Op
5. Bei Miss: Verarbeiten + Index aktualisieren

### Keine Doppelblobs

- Verhindert Duplikate
- Reduziert Speicher
- Beschleunigt Suche

## 4. Persistenz

### Telegram-Blobs

```
archivp/.../blobs/tg/in/...   # Eingehend
archivp/.../blobs/tg/out/...  # Ausgehend
```

### UI-Blobs

```
archivp/.../blobs/ui/...
```

### Metrics-Blobs

```
archivp/.../blobs/metrics/...
```

### Index

```
archivp/index.jsonl
```

## 5. Fehlerbehandlung

### 429 Rate-Limit

- Exponential Backoff
- Retry nach 1s, 2s, 4s, 8s
- Max 5 Retries

### Port-Lease-Wechsel

- Bei Port-Konflikt
- Automatischer Fallback
- Registry-Update

### Dedupe-Treffer

- No-Op (keine Verarbeitung)
- Log-Eintrag
- Metrics-Update

## 6. Routing-Regeln

### Telegram → OpenWebUI

```
Telegram → opena4 → opena2 → opena1 → opena2 → opena3 → OpenWebUI
```

### OpenWebUI → Telegram

```
OpenWebUI → opena3 → opena2 → opena1 → opena2 → opena4 → Telegram
```

### Keine Shortcuts

- Immer ueber opena2
- Immer Safepoints
- Immer Option-2-Flow

## 7. Port-Mapping

### Agents

- opena4 (Telegram): 12346
- opena3 (OpenWebUI): 12347
- opena1 (Koordinator): 12344
- opena2 (Archivator): 12345

### UI

- OpenWebUI: 8080 (UI-only)
