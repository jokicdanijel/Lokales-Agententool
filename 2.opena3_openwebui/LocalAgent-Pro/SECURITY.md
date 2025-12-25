# 🔒 Security Guide - LocalAgent-Pro

Sicherheitsarchitektur und Best Practices.

---

## 🎯 Sicherheitsziele

LocalAgent-Pro implementiert mehrere Sicherheitsebenen:

1. **Sandbox-Isolation:** Dateioperationen in isoliertem Verzeichnis
2. **Command-Whitelisting:** Nur sichere Shell-Befehle
3. **Domain-Whitelisting:** Nur vertrauenswürdige Domains
4. **Path-Traversal-Prevention:** Blockiert `../` in Pfaden
5. **Loop-Protection:** MD5-basierte Request-Deduplizierung
6. **Rate-Limiting:** Schutz vor Missbrauch

---

## 🛡️ Sicherheitsmechanismen

### 1. Sandbox-Isolation

Alle Dateioperationen erfolgen in einem isolierten Verzeichnis:

```python
SANDBOX_DIR = os.path.expanduser("~/localagent_sandbox")
```

**Verhindert:**

- ✅ Zugriff auf System-Dateien
- ✅ Manipulation kritischer Konfigurationen
- ✅ Unberechtigtes Lesen sensibler Daten

**Beispiel:**

```bash
# Erlaubt:
/home/user/localagent_sandbox/config.yaml

# Blockiert:
/etc/passwd
/home/user/.ssh/id_rsa
```

---

### 2. Command-Whitelisting

Nur sichere Befehle sind erlaubt:

```python
ALLOWED_COMMANDS = [
    "ls", "cat", "grep", "echo", "pwd",
    "date", "whoami", "uname", "df", "du"
]
```

**Blockierte Befehle:**

- ❌ `rm -rf` (Löschen)
- ❌ `sudo` (Privilege-Escalation)
- ❌ `dd` (Low-Level-Disk-Operations)
- ❌ `mkfs` (Filesystem-Formatierung)
- ❌ `chmod 777` (Unsichere Berechtigungen)

**Beispiel:**

```bash
# Erlaubt:
ls -la /home/user/localagent_sandbox

# Blockiert:
sudo rm -rf /
```

---

### 3. Domain-Whitelisting

Nur vertrauenswürdige Domains für Web-Requests:

```yaml
# config/domain_whitelist.yaml
allowed_domains:
  - example.com
  - api.github.com
  - httpbin.org
```

**Beispiel:**

```bash
# Erlaubt:
https://api.github.com/repos/jokicdanijel

# Blockiert:
https://malicious-site.com
```

---

### 4. Path-Traversal-Prevention

Blockiert `../` in Dateinamen:

```python
def sanitize_path(filename):
    if ".." in filename or filename.startswith("/"):
        raise SecurityError("Path traversal detected")
    return os.path.join(SANDBOX_DIR, filename)
```

**Beispiel:**

```bash
# Erlaubt:
config.yaml
data/users.json

# Blockiert:
../../../etc/passwd
/etc/shadow
```

---

### 5. Loop-Protection

MD5-basierte Deduplizierung verhindert Endlosschleifen:

```python
import hashlib

def check_duplicate_request(request_data):
    request_hash = hashlib.md5(str(request_data).encode()).hexdigest()
    if request_hash in recent_requests:
        raise DuplicateRequestError("Duplicate request detected")
    recent_requests.add(request_hash)
```

---

### 6. Rate-Limiting

Schutz vor Missbrauch:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/chat/completions")
@limiter.limit("100/minute")
def chat_completions():
    # ...
```

---

## 🔐 Best Practices

### 1. Sichere Konfiguration

```yaml
# config/config.yaml
security:
  sandbox_enabled: true
  command_whitelist_enabled: true
  domain_whitelist_enabled: true
  max_file_size: 10485760 # 10 MB
  max_request_size: 1048576 # 1 MB
```

### 2. Logging & Monitoring

```python
import logging

# Sicherheitsrelevante Events loggen
logging.warning(f"Blocked command: {command}")
logging.error(f"Path traversal attempt: {filename}")
logging.info(f"Duplicate request detected: {request_hash}")
```

### 3. Regelmäßige Updates

```bash
# Dependencies aktualisieren
pip install --upgrade -r requirements.txt

# Security-Patches prüfen
pip-audit

# Ollama aktualisieren
ollama pull llama3.1:8b-instruct-q4_K_M
```

### 4. Firewall-Konfiguration

```bash
# Nur lokalen Zugriff erlauben
sudo ufw allow from 127.0.0.1 to any port 8001

# Externe Zugriffe blockieren
sudo ufw deny 8001
```

---

## 🚨 Sicherheitswarnungen

### ⚠️ Production-Deployment

Für Production-Umgebungen:

1. **HTTPS verwenden:** Reverse-Proxy mit TLS
2. **Authentication:** API-Keys oder JWT
3. **Network-Isolation:** VPN oder Private Network
4. **Monitoring:** Prometheus + Grafana
5. **Backups:** Regelmäßige Sandbox-Backups

### ⚠️ Bekannte Einschränkungen

- **Single-User:** Keine Multi-Tenancy
- **No Authentication:** Nur für lokale Nutzung
- **Limited Resources:** Keine Resource-Quotas

---

## 🔍 Security-Audit

### Checkliste

- [ ] Sandbox-Verzeichnis hat korrekte Berechtigungen
- [ ] Command-Whitelist ist restriktiv
- [ ] Domain-Whitelist ist aktuell
- [ ] Logging ist aktiviert
- [ ] Firewall-Regeln sind konfiguriert
- [ ] Dependencies sind aktuell
- [ ] Keine sensiblen Daten in Logs

### Automatisierte Tests

```bash
# Security-Tests ausführen
pytest tests/security/

# Vulnerability-Scan
pip-audit

# Code-Analyse
bandit -r src/
```

---

## 📚 Weitere Ressourcen

- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **Python Security Best Practices:** https://python.readthedocs.io/en/stable/library/security_warnings.html
- **Docker Security:** https://docs.docker.com/engine/security/

---

## 📧 Security-Kontakt

**Sicherheitslücken melden:**

- **Email:** jokicdanijel@protonmail.com
- **GitHub Security Advisory:** [Create Advisory](https://github.com/jokicdanijel/Lokales-Agententool/security/advisories/new)

**Verschlüsselte Kommunikation bevorzugt.**

---

**🔒 Sicherheit ist eine kontinuierliche Reise, kein Ziel!**
