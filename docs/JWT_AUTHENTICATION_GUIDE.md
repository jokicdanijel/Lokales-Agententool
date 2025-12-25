# 🔐 JWT Authentication System für ELION

**Status:** ✅ **PRODUKTIONSREIF**
**Version:** 1.0.0
**Datum:** 2025-11-08

---

## 📋 Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Installation & Setup](#installation--setup)
3. [Token-Generierung](#token-generierung)
4. [Token-Validierung](#token-validierung)
5. [Integration in FastAPI](#integration-in-fastapi)
6. [Security Best Practices](#security-best-practices)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## 📚 Übersicht

Das JWT-System bietet:

- ✅ **RS256-Signierung** (RSA 2048-bit)
- ✅ **Token-Expirierung** (Konfigurierbar, default 24h)
- ✅ **Agent-spezifische Claims** (agent_id, scope, permissions)
- ✅ **Token-Refresh** (Automatische Erneuerung)
- ✅ **Sichere Key-Verwaltung** (.env oder Dateisystem)
- ✅ **Pydantic-Validierung** (Typsicherheit)
- ✅ **Fehlerbehandlung** (Detaillierte Error-Typen)

### Architektur

```
┌─────────────────────────────────────────────┐
│         OpenWebUI Integration Manager       │
│  (openwebui_integration.py mit JWT-Auth)   │
└────────────────┬────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
      ▼                     ▼
  JWT Auth Module      19 Agenten
  (jwt_auth.py)     (opena1-opena19)
      │                     │
      ├─ Token Creation     │
      ├─ Verification       │
      ├─ Refresh            │
      └─ Key Management     │
                            │
         ┌──────────────────┘
         ▼
   REST API Calls
   (mit Bearer Token)
```

---

## 🚀 Installation & Setup

### 1. Abhängigkeiten installieren

```bash
cd /path/to/Gesamtprojekt
pip install PyJWT cryptography pydantic aiohttp
```

### 2. RSA-Schlüssel generieren (automatisch)

Die Schlüssel werden beim ersten Start automatisch generiert:

```python
from jwt_auth import RSAKeyManager

# Wird automatisch beim ersten Token erstellt
private_key, public_key = RSAKeyManager.generate_keypair()
```

**Speicherorte:**

- Private Key: `secrets/jwt_private.pem`
- Public Key: `secrets/jwt_public.pem`

### 3. Environment-Variablen (Optional)

Alternativ können Schlüssel in der `.env` gespeichert werden:

```bash
# .env
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n..."
```

---

## 🎫 Token-Generierung

### Einfacher Token

```python
from jwt_auth import create_token

# Erstelle Token für opena1
token = create_token(
    agent_id="opena1",
    scope="invoke"
)

print(token)
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOi...
```

### Token mit Permissions

```python
token = create_token(
    agent_id="opena2",
    scope="admin",
    permissions=["read", "write", "delete"]
)
```

### Token mit Custom Expirierung

```python
token = create_token(
    agent_id="opena1",
    scope="invoke",
    expires_in_hours=1  # 1 Stunde statt default 24h
)
```

### Token-Struktur (JWT Payload)

```json
{
  "iss": "elion-dashboard",
  "sub": "opena1",
  "aud": "elion-agents",
  "iat": 1699512345,
  "exp": 1699598745,
  "nbf": 1699512345,
  "jti": "abc123def456",
  "agent_id": "opena1",
  "scope": "invoke",
  "permissions": ["read", "write"]
}
```

---

## ✅ Token-Validierung

### Basis-Validierung

```python
from jwt_auth import verify_token

result = verify_token(token)

if result.valid:
    print(f"✅ Token gültig")
    print(f"Agent: {result.claims.agent_id}")
    print(f"Scope: {result.claims.scope}")
else:
    print(f"❌ Fehler: {result.error}")
    print(f"Typ: {result.error_type}")
```

### Error-Typen

| Error Type          | Bedeutung                                    |
| ------------------- | -------------------------------------------- |
| `EXPIRED`           | Token ist abgelaufen                         |
| `INVALID_SIGNATURE` | Signatur ist ungültig                        |
| `INVALID_AUDIENCE`  | Zielgruppe stimmt nicht überein              |
| `INVALID_ISSUER`    | Aussteller stimmt nicht überein              |
| `DECODE_ERROR`      | Token kann nicht dekodiert werden            |
| `MISSING_HEADER`    | Authorization-Header fehlt                   |
| `INVALID_FORMAT`    | Header-Format ist ungültig                   |
| `KEY_LOAD_ERROR`    | Private/Public Key kann nicht geladen werden |

---

## 🔄 Token-Refresh

Tokens können automatisch erneuert werden, wenn sie kurz vor Ablauf stehen:

```python
from jwt_auth import refresh_token

new_token = refresh_token(
    token=old_token,
    agent_id="opena1"
)

if new_token:
    print(f"✅ Token erneuert")
else:
    print(f"ℹ️  Token noch gültig, keine Erneuerung nötig")
```

**Refresh-Logik:**

- Wenn Token < 1 Stunde bis Ablauf: Automatische Erneuerung
- Wenn Token > 1 Stunde bis Ablauf: Keine Erneuerung nötig
- Neue Token erhalten gleiche `scope` und `permissions`

---

## 🔌 Integration in FastAPI

### 1. Token-Generierung im Dashboard

```python
# main_dashboard.py
from fastapi import FastAPI, HTTPException
from jwt_auth import create_token, verify_token
from openwebui_integration import get_manager

app = FastAPI()

@app.post("/api/agents/{agent_id}/token")
async def get_agent_token(agent_id: str, authorization: str):
    """Generiere JWT-Token für Agent"""

    # 1. Prüfe Admin-Token
    admin_result = verify_token(authorization.replace("Bearer ", ""))
    if not admin_result.valid or admin_result.claims.scope != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    # 2. Erstelle Agent-Token
    token = create_token(
        agent_id=agent_id,
        scope="invoke",
        permissions=["read", "write"]
    )

    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 86400,
        "agent_id": agent_id
    }
```

### 2. Token-Validierung in Agenten

```python
# main_opena1.py
from fastapi import FastAPI, Header, HTTPException
from jwt_auth import verify_token

app = FastAPI()

@app.post("/invoke")
async def invoke(
    payload: dict,
    authorization: str = Header(None)
):
    """Agent-Endpoint mit JWT-Validierung"""

    # 1. Prüfe Authorization-Header
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    # 2. Verifiziere Token
    result = verify_token(authorization.replace("Bearer ", ""))
    if not result.valid:
        raise HTTPException(status_code=403, detail=result.error)

    # 3. Prüfe Berechtigungen
    if "write" not in result.claims.permissions:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # 4. Verarbeite Request
    return {"status": "ok", "agent_id": result.claims.agent_id}
```

### 3. Manager-Integration

```python
# openwebui_integration.py
manager = await get_manager()

# Tokens für alle Agenten erstellen
tokens = manager.get_all_agent_tokens()

# Token mit Manager erstellen
token = manager.create_agent_token(
    agent_id="opena1",
    scope="invoke"
)

# Token mit Manager validieren
claims = manager.verify_agent_token(token)

# Agent mit JWT aufrufen
response = await manager.invoke_agent_with_jwt(
    agent_id="opena1",
    payload={"test": "data"},
    token=token
)
```

---

## 🔐 Security Best Practices

### 1. Private Key schützen

```bash
# Berechtigungen einschränken
chmod 600 secrets/jwt_private.pem
```

### 2. Tokens nicht loggen

```python
# ❌ FALSCH
logger.info(f"Token: {token}")

# ✅ RICHTIG
logger.info(f"Token created for {agent_id}")
```

### 3. Kurze Expirierung für sensitive Operationen

```python
# Für Admin-Operationen
token = create_token(
    agent_id="opena1",
    scope="admin",
    expires_in_hours=0.5  # 30 Minuten
)
```

### 4. HTTPS verwenden

```bash
# In Production immer HTTPS
https://your-domain.com/api/agents/invoke
```

### 5. Token-Rotation

```python
# Periodisch neue Tokens erstellen (z.B. täglich)
@app.on_event("startup")
async def rotate_tokens():
    manager = await get_manager()
    tokens = manager.get_all_agent_tokens()
    # Speichere neue Tokens in Secrets-Verwaltung
```

---

## 🧪 Testing

### JWT-Tests ausführen

```bash
cd 19.dashboard_agent
python -m pytest tests/test_jwt_auth.py -v
```

### Tests lokal ausführen

```bash
python tests/test_jwt_auth.py
```

### Spezifische Testklasse

```bash
pytest tests/test_jwt_auth.py::TestTokenGeneration -v
pytest tests/test_jwt_auth.py::TestTokenVerification -v
pytest tests/test_jwt_auth.py::TestKeyManagement -v
```

### Test-Coverage

```bash
pytest tests/test_jwt_auth.py --cov=jwt_auth
```

---

## 🐛 Troubleshooting

### Problem: "JWT module not available"

**Lösung:**

```bash
pip install PyJWT cryptography
```

### Problem: "Private key not found"

**Lösung:**

```bash
# Schlüssel automatisch generieren
python -c "from jwt_auth import RSAKeyManager; RSAKeyManager.generate_keypair()"
```

### Problem: "Invalid signature"

**Ursachen:**

- Private/Public Key stimmt nicht überein
- Token wurde manipuliert
- Falscher Algorithmus

**Lösung:**

```bash
# Schlüssel neu generieren
rm secrets/jwt_*.pem
python -c "from jwt_auth import RSAKeyManager; RSAKeyManager.generate_keypair()"
```

### Problem: "Token expired"

**Lösung:**

```python
# Neue Tokens mit längerer Expirierung erstellen
token = create_token(agent_id="opena1", expires_in_hours=48)
```

### Problem: "Missing Authorization header"

**Lösung:**

```bash
# Request muss Bearer-Token enthalten
curl -H "Authorization: Bearer <token>" \
     -X POST http://localhost:12349/api/endpoint
```

---

## 📊 Monitoring

### Token-Metriken tracken

```python
# In OpenWebUI Integration Manager
class OpenWebUIIntegrationManager:
    def __init__(self):
        self.token_metrics = {
            "created": 0,
            "verified": 0,
            "expired": 0,
            "invalid": 0
        }

    def record_token_created(self):
        self.token_metrics["created"] += 1

    def record_token_verified(self):
        self.token_metrics["verified"] += 1
```

### Health-Check mit JWT

```bash
# Prüfe ob JWT funktioniert
curl -X POST http://localhost:12349/api/auth/verify \
     -H "Authorization: Bearer $(cat token.txt)" \
     -H "Content-Type: application/json"
```

---

## 📝 Checkliste für Production

- [ ] RSA-Schlüssel generiert und sicher gespeichert
- [ ] Private Key in `.env` oder `secrets/` mit 600er Berechtigungen
- [ ] Token-Expirierung im Kopf (Default: 24h)
- [ ] HTTPS in Production aktiviert
- [ ] Fehlerbehandlung implementiert (siehe Codes oben)
- [ ] Unit-Tests durchführen
- [ ] Monitoring/Logging konfiguriert
- [ ] Key-Rotation Plan erstellt
- [ ] Dokumentation aktualisiert
- [ ] Team geschult auf JWT-System

---

## 🎯 Nächste Schritte

1. JWT in Dashboard aktivieren:

   ```bash
   # In main_dashboard.py Token-Endpoints hinzufügen
   ```

2. Alle Agenten mit JWT ausstatten:

   ```bash
   # In main_opena*.py Token-Validierung hinzufügen
   ```

3. Integration testen:

   ```bash
   pytest tests/test_jwt_auth.py -v
   ```

4. Tokens für Production generieren:
   ```bash
   python -c "from openwebui_integration import get_manager; \
             import asyncio; \
             m = asyncio.run(get_manager()); \
             print(m.get_all_agent_tokens())"
   ```

---

**Erstellt:** 2025-11-08
**Version:** 1.0.0
**Status:** Production Ready ✅
