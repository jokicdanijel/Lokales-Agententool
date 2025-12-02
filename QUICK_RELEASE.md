# 🚀 Quick Release Guide

**Last Updated:** 2025-12-02

## Create a Release (1 Command)

```bash
bash bin/prepare_release.sh v3.0.0
```

## What You Get

- ✅ `portier-v3.0.0.tar.gz` (8MB) - Compressed archive
- ✅ `portier-v3.0.0.zip` (19MB) - Windows-friendly format
- ✅ SHA256 checksums for both files
- ✅ MANIFEST.txt with package details
- ✅ Automated setup script included

## Install from Release

```bash
# 1. Extract
tar -xzf portier-v3.0.0.tar.gz
cd portier-v3.0.0

# 2. Run setup
bash setup.sh

# 3. Configure
nano .env

# 4. Start
bash bin/start_all.sh
```

## What's Included

- 20+ AI Agent Services
- Core infrastructure scripts
- Configuration templates
- Essential documentation
- Docker Compose setup
- Systemd services

## What's Excluded

- Virtual environments
- Log files
- Python cache
- Database files
- Git history
- Development docs

## Verification

```bash
# Verify integrity
sha256sum -c portier-v3.0.0.tar.gz.sha256

# Check contents
tar -tzf portier-v3.0.0.tar.gz | head -20
```

## Full Documentation

See `docs/RELEASE_GUIDE.md` for complete instructions.

---

**Package Size:** ~8MB (tar.gz) | ~19MB (zip)  
**Unpacked Size:** ~25-30MB  
**Files:** ~3,000  
**Setup Time:** ~2-5 minutes
