# OpenWebUI – Modell-Verfügbarkeit prüfen

**Befehl:** `/openwebui_models_test`  
**Zugriff:** `public`

## Eingabeaufforderung

Testen Sie die Verfügbarkeit der angegebenen Modelle über die API und bestätigen Sie, dass sie in der OpenWebUI ausgewählt werden können.

## Eingabefelder

```
{{api_base_url | url:placeholder="z.B. http://127.0.0.1:8001/v1":required}}
{{model_to_test | select:options=["tinyllama","localagent-pro","llama2:latest","llama3.1","mistral"]:required}}
{{test_type | select:options=["smoke-test","end-to-end","health-check","performance"]:default="health-check":required}}
{{description | textarea:placeholder="Optional: Kontext oder erwartetes Verhalten"}}
```

## Prompt-Template

```
🧪 **Modell-Verfügbarkeitstest**

Teste das Modell "{{model_to_test}}" mit Test-Typ: {{test_type}}

## Test-Schritte:

### 1. Modell-Listing
- GET {{api_base_url}}/models
- Suche nach "{{model_to_test}}" in der Response
- Prüfe Modell-Metadaten (created, owned_by)

### 2. Test-Typ: {{test_type}}

**Bei "smoke-test":**
- Sende minimalen Test-Prompt: "Hi"
- Erwarte: Erfolgreiche Response (< 5s)
- Validiere: Response-Format korrekt

**Bei "end-to-end":**
- Sende komplexen Prompt: "Erkläre Quantencomputing in 3 Sätzen"
- Erwarte: Vollständige, kohärente Antwort
- Validiere: Token-Count, Response-Zeit, Qualität

**Bei "health-check":**
- Prüfe nur, ob Modell verfügbar ist
- Keine tatsächliche Inferenz
- Validiere: Modell-ID, Status, Verfügbarkeit

**Bei "performance":**
- Sende Prompt mit bekannter Token-Anzahl
- Messe: Response-Zeit, Tokens/Sekunde
- Vergleiche mit erwarteten Benchmarks:
  * tinyllama: 6-10 t/s (GPU), 2-3 t/s (CPU)
  * llama3.1: 3-5 t/s (GPU)

### 3. Ergebnis-Report

Erstelle strukturierten Report:

```json
{
  "model": "{{model_to_test}}",
  "test_type": "{{test_type}}",
  "timestamp": "<ISO-8601>",
  "results": {
    "available": true/false,
    "response_time_ms": <number>,
    "tokens_per_second": <number>,
    "quality_score": <1-10>,
    "errors": []
  },
  "recommendation": "<Empfehlung basierend auf Test>"
}
```

**Kontext:**
{{description}}

**Führe alle Tests aus und gib detaillierte Ergebnisse.**
```

---

## Beispiel-Verwendung

### Schneller Smoke-Test

```
/openwebui_models_test
API Base URL: http://127.0.0.1:8001/v1
Modell: tinyllama
Test-Typ: smoke-test
```

**Erwarteter Output:**
```
🧪 Modell-Verfügbarkeitstest - tinyllama

1. ✅ Modell-Listing
   - Gefunden: tinyllama
   - Metadaten: {
       "id": "tinyllama",
       "object": "model",
       "created": 1763266237,
       "owned_by": "localagent-pro"
     }

2. ✅ Smoke-Test
   - Prompt: "Hi"
   - Response: "Hello! How can I help you today?"
   - Response-Zeit: 0.8s
   - Format: ✅ Korrekt (OpenAI-kompatibel)

📊 Test-Ergebnis:
{
  "model": "tinyllama",
  "test_type": "smoke-test",
  "timestamp": "2025-11-16T05:10:37Z",
  "results": {
    "available": true,
    "response_time_ms": 800,
    "tokens_per_second": 8.5,
    "quality_score": 9,
    "errors": []
  },
  "recommendation": "✅ Modell einsatzbereit - Optimal für schnelle Antworten"
}
```

### Performance-Test

```
/openwebui_models_test
API Base URL: http://127.0.0.1:8001/v1
Modell: tinyllama
Test-Typ: performance
Beschreibung: GPU-Beschleunigung testen (GTX 1050)
```

**Erwarteter Output:**
```
🧪 Performance-Test - tinyllama (GPU: GTX 1050)

1. ✅ Modell verfügbar

2. 🚀 Performance-Messung
   - Test-Prompt: "Erkläre Machine Learning" (50 Token Output)
   - Response-Zeit: 5.2s
   - Tokens/Sekunde: 9.6 t/s
   - GPU-Auslastung: 93%
   - VRAM: 1.2 GB / 4.0 GB

3. 📊 Benchmark-Vergleich
   - Erwartung (GPU): 6-10 t/s ✅
   - Ist-Wert: 9.6 t/s ✅
   - CPU-Vergleich: ~3x schneller
   - Status: Optimal

📋 Empfehlung:
✅ GPU-Beschleunigung funktioniert korrekt
🎯 Perfekte Performance für GTX 1050
💡 Für größere Modelle: RAM-Limit beachten (4GB)
```

---

## Modell-spezifische Hinweise

### tinyllama
- **Größe:** 637 MB
- **Optimal für:** Schnelle Antworten, Chat, Tools
- **GPU:** GTX 1050 (4GB) - Perfekt
- **Performance:** 6-10 t/s (GPU)

### llama3.1
- **Größe:** ~4.7 GB
- **Optimal für:** Komplexe Aufgaben, Reasoning
- **GPU:** GTX 1050 - Teilweise (RAM-Limit)
- **Performance:** 3-5 t/s (GPU)

### localagent-pro
- **Hybrid:** Tools + KI
- **Optimal für:** Datei-Operationen, Code-Generierung
- **GPU:** Nutzt tinyllama im Backend
- **Performance:** Wie tinyllama

---

## Troubleshooting

### "Model not available"
```bash
# Modell herunterladen
ollama pull tinyllama

# Verfügbare Modelle prüfen
ollama list
```

### "Slow response (>10s)"
```bash
# GPU-Status prüfen
nvidia-smi

# Ollama-Logs checken
journalctl -u ollama -f

# GPU-Beschleunigung aktivieren
sudo systemctl stop ollama
cd /path/to/LocalAgent-Pro
./setup_gpu_acceleration.sh
```

### "Quality score low"
- Größeres Modell wählen (llama3.1 statt tinyllama)
- Temperature anpassen (0.7 → 0.3 für präzisere Antworten)
- max_tokens erhöhen
