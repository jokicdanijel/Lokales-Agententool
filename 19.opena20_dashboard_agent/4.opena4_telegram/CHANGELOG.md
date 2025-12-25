# Changelog - opena4 (Telegram Agent)

All notable changes to this agent will be documented in this file.

## [1.0.0] - 2025-12-23

### Added

- ✅ Initial release of opena4 (Telegram Agent)
- ✅ Telegram Bot API integration
- ✅ Send/receive messages
- ✅ Chat management
- ✅ Message history (PostgreSQL)
- ✅ Redis caching for sessions
- ✅ Health check endpoint
- ✅ Capabilities endpoint for opena20 discovery
- ✅ Bot commands: /start, /help, /status
- ✅ REST API endpoints:
  - POST /send - Send message
  - GET /chats - List chats
  - GET /messages/{chat_id} - Get message history
  - GET /stats - Get statistics
  - GET /capabilities - Agent capabilities
- ✅ Plan gates (Basic plan features)
- ✅ Workflow integration examples
- ✅ Webhook mode support
- ✅ Docker deployment ready
- ✅ Unit tests
- ✅ Documentation (README.md)

### Plan Gates

- **Basic Plan:**
  - Send/receive messages ✅
  - Read-only message history ✅
  - 4 workflows per agent ✅
  - Basic bot commands ✅
- **Pro Plan (future):**
  - Delete messages
  - Edit messages
  - 10 workflows per agent
  - Advanced automation

### Database Schema

- `telegram_messages` table for message storage
- `telegram_chats` table for chat tracking

### Security

- ✅ Environment variables for secrets
- ✅ Input validation via Pydantic
- ✅ SQL injection protection (asyncpg)
- ✅ Rate limiting (Telegram API native)

### Technical Details

- **Port:** 12346 (canonical)
- **Plan:** Basic
- **Dependencies:**
  - FastAPI 0.109.0
  - python-telegram-bot 21.0.1
  - asyncpg 0.29.0
  - redis 5.0.1

---

## Future Roadmap

### [1.1.0] - Planned

- [ ] Media support (photos, documents, voice)
- [ ] Inline keyboards
- [ ] Message templates
- [ ] Scheduled messages
- [ ] Message editing (Pro+ feature)
- [ ] Message deletion (Pro+ feature)

### [1.2.0] - Planned

- [ ] Group management features
- [ ] Channel posting
- [ ] Bulk operations
- [ ] Advanced analytics
- [ ] Export chat history

### [2.0.0] - Future

- [ ] Multi-bot support
- [ ] Telegram Mini Apps integration
- [ ] Payment processing
- [ ] Advanced workflow triggers
