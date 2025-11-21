# ELION Hyper-Dashboard Setup Guide

## Quick Start

This guide shows you how to set up and start the ELION Hyper-Dashboard system with proper environment configuration and agent registration.

## Prerequisites

- Python 3.12+
- Bash shell
- Access to OpenAI API (for OPENAI_API_KEY)
- Dashboard admin token

## Setup Workflow

### 1. Set OPENAI_API_KEY

The OPENAI_API_KEY is required for AI-powered features in the dashboard.

**Check if it exists:**
```bash
grep "^OPENAI_API_KEY=" .env
```

**Add it if missing:**
```bash
echo "OPENAI_API_KEY=your_key_here" >> .env
```

**Alternative:** Copy from template
```bash
# If .env doesn't exist, create from template
cp .env.example .env
# Then edit .env and add your keys
```

### 2. Start Services

Use the `bin/ops.sh` script to start all services:

```bash
bin/ops.sh start
```

This command will:
- ✅ Check for OPENAI_API_KEY in .env
- ✅ Start the Dashboard (Port 12349)
- ✅ Start Portier/Coordinator (Port 12344)
- ✅ Start Archivator (Port 12345)
- ✅ Start other agent services

### 3. Register Agents

After services are running, register the agents with the dashboard:

```bash
python3 scripts/register_agents.py
```

**Alternative:** Use the ops.sh shortcut:
```bash
bin/ops.sh agents:register
```

This will register:
- **opena1** (Portier/Coordinator) → http://127.0.0.1:12344
- **opena2** (Archivator) → http://127.0.0.1:12345

## Verification

### Check Service Health

```bash
bin/ops.sh health
```

Expected output:
```json
{
  "status": "ok",
  "service": "dashboard",
  "timestamp": "2025-11-21T05:28:35Z"
}
```

### Check Agent Status

```bash
bin/ops.sh status
```

Expected output:
```json
{
  "agents": {
    "opena1": {
      "status": "up",
      "endpoint": "http://127.0.0.1:12344"
    },
    "opena2": {
      "status": "up",
      "endpoint": "http://127.0.0.1:12345"
    }
  }
}
```

## Available Commands

The `bin/ops.sh` script provides the following commands:

| Command | Description |
|---------|-------------|
| `start` | Start all services |
| `stop` | Stop all services |
| `health` | Check Dashboard health (no token required) |
| `status` | Check all agents status (requires token) |
| `agents:register` | Register agents with dashboard |
| `verify` | Run integration verification |
| `logs` | Show service logs |
| `help` | Show help message |

## Configuration Files

### .env File Structure

```bash
# Required: Admin token for dashboard API
DASHBOARD_ADMIN_TOKEN=your_secure_token_here

# Required: OpenAI API key for AI features
OPENAI_API_KEY=sk-proj-...

# Optional: Telegram configuration
TELEGRAM_BOT_TOKEN=123456:ABCDEF...
TELEGRAM_WEBHOOK_SECRET=webhook_secret...
TELEGRAM_ALLOWED_USERS=123456789,987654321

# Optional: OpenAI organization
OPENAI_ORG=org-...
```

### Important Notes

1. **Never commit .env to git** - It contains sensitive credentials
2. **Use .env.example as template** - Copy and modify for your setup
3. **DASHBOARD_ADMIN_TOKEN is required** - Used for agent registration
4. **OPENAI_API_KEY is required** - Used for AI-powered features

## Troubleshooting

### "DASHBOARD_ADMIN_TOKEN not found in .env"

**Solution:** Add the token to your .env file:
```bash
echo "DASHBOARD_ADMIN_TOKEN=your_token_here" >> .env
```

### "OPENAI_API_KEY not found in .env"

**Solution:** Add your OpenAI API key:
```bash
echo "OPENAI_API_KEY=sk-proj-your_key_here" >> .env
```

### Services fail to start

**Check ports:**
```bash
# Ensure ports 12344, 12345, 12349 are available
netstat -tuln | grep -E "12344|12345|12349"
```

**Check logs:**
```bash
bin/ops.sh logs
```

### Agent registration fails

**Ensure services are running:**
```bash
bin/ops.sh health
```

**Check dashboard is accessible:**
```bash
curl -s http://127.0.0.1:12349/health
```

**Verify token is correct:**
```bash
grep "^DASHBOARD_ADMIN_TOKEN=" .env
```

## Demo Workflow

To see a demonstration of the complete workflow:

```bash
./scripts/demo_workflow.sh
```

This will show you each step of the setup process without actually starting services.

## Advanced Usage

### Custom Port Configuration

If you need to use a custom dashboard port, create `.runtime/port`:

```bash
mkdir -p .runtime
echo "8000" > .runtime/port
```

The scripts will automatically use this port instead of the default 12349.

### Manual Agent Registration

If you prefer to register agents manually:

```bash
curl -X POST http://127.0.0.1:12349/api/agent/register \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"opena1","endpoint":"http://127.0.0.1:12344"}'
```

## Testing

Run the automated tests to verify your setup:

```bash
python3 -m pytest tests/test_ops_and_register.py -v -o addopts=""
```

Expected: 19 tests passing ✅

## Security Best Practices

1. **Protect your .env file**
   - Never commit it to version control
   - Set appropriate file permissions: `chmod 600 .env`

2. **Use strong tokens**
   - DASHBOARD_ADMIN_TOKEN should be at least 16 characters
   - Use a password manager to generate secure tokens

3. **Rotate credentials regularly**
   - Change DASHBOARD_ADMIN_TOKEN periodically
   - Rotate OPENAI_API_KEY if compromised

4. **Monitor access**
   - Check logs regularly: `bin/ops.sh logs`
   - Monitor for unauthorized access attempts

## Support

For issues or questions:
1. Check this README
2. Run the demo: `./scripts/demo_workflow.sh`
3. Review the logs: `bin/ops.sh logs`
4. Check the test suite: `pytest tests/test_ops_and_register.py`

## License

MIT License - See LICENSE file for details
