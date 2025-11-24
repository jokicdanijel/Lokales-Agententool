# NOTICE

## Third-Party Dependencies & Acknowledgments

This project (PORTIER 3.0) uses the following open-source libraries and frameworks:

---

## 🐍 Python Dependencies

### Core Framework & APIs

| Library | Version | License | Purpose |
|---------|---------|---------|---------|
| **FastAPI** | >=0.95.0 | MIT | Web Framework for REST APIs |
| **Pydantic** | >=2.0.0 | MIT | Data Validation & Settings |
| **OpenAI** | >=1.0.0 | MIT | OpenAI API Client |
| **python-telegram-bot** | >=20.0 | LGPL-3.0 | Telegram Bot Integration |
| **requests** | >=2.31.0 | Apache 2.0 | HTTP Client |
| **SQLAlchemy** | >=2.0 | MIT | ORM Database Layer |
| **SQLite3** | Built-in | Public Domain | Local Database |

### Async & Concurrency

| Library | License | Purpose |
|---------|---------|---------|
| **asyncio** | Python Software Foundation | Async I/O |
| **aiohttp** | Apache 2.0 | Async HTTP Client |

### Data Processing

| Library | License | Purpose |
|---------|---------|---------|
| **pandas** | BSD-3-Clause | Data Analysis (Optional) |
| **numpy** | BSD-3-Clause | Numerical Computing (Optional) |
| **json** | Python Software Foundation | JSON Serialization |

### Utilities & Helpers

| Library | License | Purpose |
|---------|---------|---------|
| **python-dotenv** | BSD-3-Clause | Environment Variable Management |
| **pathlib** | Python Software Foundation | File Path Operations |
| **logging** | Python Software Foundation | Logging Framework |
| **datetime** | Python Software Foundation | Date/Time Operations |

---

## 🐳 Docker & Infrastructure

| Component | License | Purpose |
|-----------|---------|---------|
| **Docker** | Apache 2.0 | Container Runtime |
| **Docker Compose** | Apache 2.0 | Multi-Container Orchestration |
| **Python 3.12+** | Python Software Foundation | Runtime Environment |

---

## 📦 System Dependencies

### Ubuntu/Debian Linux

```
- curl (MIT)
- git (GPLv2)
- openssh-client (BSD)
- jq (MIT)
- sqlite3 (Public Domain)
```

### Optional Tools

```
- redis (BSD-3-Clause) - Caching & Message Queue
- PostgreSQL (PostgreSQL License) - Enterprise Database
```

---

## 🎨 Frontend & UI

### Dashboard (if applicable)

| Library | License | Purpose |
|---------|---------|---------|
| **Glasmorphism CSS** | MIT | Visual Design Pattern |
| **Responsive HTML5** | - | Web Standards |

---

## 📄 Special Notices

### 1. Safepoint System

- **Append-Only Archive Format** (Custom Implementation)
- Uses Unicode `→` (U+2192) arrow markers
- Compatible with JSON standards

### 2. Option-2-Flow Architecture

- **Custom Multi-Agent Pattern** (Proprietary to JD Smart Vision EU)
- Implements sequential request routing through:
  - opena1 (Koordinator)
  - opena2 (Archivator)
  - kordp (Gateway)
  - Specialized Agents (opena3-opena20+)

### 3. Data Backup Infrastructure

- **35 GB encrypted backup** (Backup Strategy)
- Non-public, internal infrastructure
- Encryption: AES-256 (or equivalent)

---

## 📋 License Compliance

All third-party libraries are used in compliance with their respective licenses:

- **MIT Licensed** → Commercial use permitted, attribution required
- **Apache 2.0** → Commercial use permitted, changes must be documented
- **BSD-3-Clause** → Commercial use permitted, clause notice required
- **LGPL-3.0** → Weak copyleft, library usage permitted
- **GPLv2** → Derivative works must be open-source (git only)
- **Public Domain** → No restrictions

---

## 🔒 Security Considerations

- No malware or suspicious code included
- All dependencies from official package repositories (PyPI, apt, etc.)
- Regular security updates recommended
- See SECURITY.md for vulnerability reporting

---

## 📞 Attribution

**PORTIER 3.0 Development Team:**

- **Erfinder & Lead Developer:** Danijel Jokic
- **Company:** JD Smart Vision EU
- **Project:** Multi-Agent Enterprise Intelligence Platform

**Repository:** <https://github.com/jokicdanijel/Gesamtprojekt-Start>

---

## 📝 Updates

This NOTICE.md is maintained as part of the PORTIER 3.0 project and updated with each major release.

**Last Updated:** 24. November 2025
**PHASE:** 13 (Production Deployment)

---

*Generated for PORTIER 3.0 Enterprise Edition - JD Smart Vision EU*
