# PORTIER 3.0 - Release Guide

**Document Version:** 1.0
**Last Updated:** 2025-12-02
**Maintainer:** Danijel Jokic

---

## 📋 Overview

This guide describes how to create a compressed, runnable release package for the PORTIER 3.0 Multi-Agent Intelligence Platform for deployment on new repositories or systems.

## 🎯 Purpose

The release package is designed to:

- **Minimize Size** - Exclude development artifacts, logs, caches, and large files
- **Maximize Portability** - Include all essential components for a complete deployment
- **Simplify Setup** - Automated setup script for new installations
- **Ensure Integrity** - SHA256 checksums for verification
- **Support Distribution** - Both tar.gz and zip formats

## 📦 What's Included

### Essential Components

- ✅ **20+ Agent Services** (opena1-opena21)
- ✅ **Core Infrastructure** (bin/, scripts/, configs/)
- ✅ **Essential Documentation** (system architecture, operations guide)
- ✅ **Configuration Templates** (.env.example, docker-compose)
- ✅ **Setup Scripts** (automated installation)
- ✅ **Source Code** (src/, tools/)
- ✅ **Systemd Services** (for daemon deployment)

### Excluded from Release

- ❌ Virtual environments (.venv, venv)
- ❌ Python cache (\_\_pycache\_\_, \*.pyc)
- ❌ Log files (\*.log, logs/)
- ❌ Database files (_.db,_.sqlite)
- ❌ Git history (.git/)
- ❌ Backup files
- ❌ Broken/deprecated components
- ❌ Development documentation (only essential docs included)

## 🚀 Creating a Release

### Quick Start

```bash
# Create a versioned release
bash bin/prepare_release.sh v1.0.0

# Create a timestamped release (default)
bash bin/prepare_release.sh
```

### Step-by-Step Process

#### 1. Prepare Your Repository

Ensure your repository is in a clean state:

```bash
# Check git status
git status

# Ensure all changes are committed
git add .
git commit -m "Prepare for release v1.0.0"

# Optional: Create a git tag
git tag -a v1.0.0 -m "Release version 1.0.0"
```

#### 2. Run the Release Script

```bash
cd /path/to/Gesamtprojekt-start
bash bin/prepare_release.sh v1.0.0
```

The script will:

1. Clean up any previous release directory
2. Copy all essential service directories
3. Copy core infrastructure (bin, scripts, configs)
4. Copy configuration files
5. Copy essential documentation
6. Create automated setup script
7. Generate release README
8. Create tar.gz and zip archives
9. Generate SHA256 checksums
10. Create manifest file

#### 3. Verify the Release

```bash
# Navigate to release directory
cd release

# Verify checksums
sha256sum -c portier-v1.0.0.tar.gz.sha256
sha256sum -c portier-v1.0.0.zip.sha256

# Check manifest
cat MANIFEST.txt
```

#### 4. Test the Release

Extract and test in a clean environment:

```bash
# Extract to temporary location
tar -xzf portier-v1.0.0.tar.gz -C /tmp
cd /tmp/portier-v1.0.0

# Run setup script (in dry-run mode if available)
bash setup.sh
```

#### 5. Distribute the Release

##### Option A: GitHub Release

```bash
# Create GitHub release using gh CLI
gh release create v1.0.0 \
  release/portier-v1.0.0.tar.gz \
  release/portier-v1.0.0.tar.gz.sha256 \
  release/portier-v1.0.0.zip \
  release/portier-v1.0.0.zip.sha256 \
  release/MANIFEST.txt \
  --title "PORTIER 3.0 v1.0.0" \
  --notes-file release/RELEASE_NOTES.md
```

##### Option B: Manual Upload

1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Upload the following files:
   - `portier-v1.0.0.tar.gz`
   - `portier-v1.0.0.tar.gz.sha256`
   - `portier-v1.0.0.zip`
   - `portier-v1.0.0.zip.sha256`
   - `MANIFEST.txt`

##### Option C: Direct Distribution

Copy the archive to your target location:

```bash
# Via SCP
scp release/portier-v1.0.0.tar.gz user@server:/path/to/destination/

# Via rsync
rsync -avz release/portier-v1.0.0.tar.gz user@server:/path/to/destination/
```

## 🔧 Installing from Release Package

### For End Users

#### 1. Download the Release

```bash
# Download from GitHub releases
wget https://github.com/jokicdanijel/Gesamtprojekt-start/releases/download/v1.0.0/portier-v1.0.0.tar.gz
wget https://github.com/jokicdanijel/Gesamtprojekt-start/releases/download/v1.0.0/portier-v1.0.0.tar.gz.sha256
```

#### 2. Verify Integrity

```bash
# Verify checksum
sha256sum -c portier-v1.0.0.tar.gz.sha256
```

#### 3. Extract

```bash
# Extract the archive
tar -xzf portier-v1.0.0.tar.gz
cd portier-v1.0.0
```

#### 4. Run Setup

```bash
# Execute automated setup
bash setup.sh
```

The setup script will:

- Create Python virtual environment
- Install all dependencies
- Set up directory structure
- Bootstrap environment variables
- Run initial health checks

#### 5. Configure

```bash
# Edit environment variables
nano .env

# Required variables:
# - OPENAI_API_KEY_OPENA1
# - BEARER_TOKEN_MASTER
# - Other agent-specific keys
```

#### 6. Start Services

```bash
# Start all services
bash bin/start_all.sh

# Check status
bash bin/ops.sh status

# View dashboard
# Open browser to http://127.0.0.1:12349
```

## 📊 Release Statistics

A typical release package contains:

- **Files:** ~3,000
- **Directories:** ~330
- **Python Files:** ~500
- **Shell Scripts:** ~190
- **Size (tar.gz):** ~8-10 MB
- **Size (zip):** ~15-20 MB
- **Size (unpacked):** ~25-30 MB

## 🔍 Manifest File

Each release includes a `MANIFEST.txt` file containing:

- Release version and timestamp
- List of included files
- Package statistics (file counts, sizes)
- Verification instructions
- Extraction instructions

Example manifest structure:

```
PORTIER 3.0 - Release Manifest
==============================

Release Version: v1.0.0
Generated: 2025-12-02 12:00:00 UTC

Files in This Release
---------------------
1. portier-v1.0.0.tar.gz
2. portier-v1.0.0.zip
3. MANIFEST.txt

Package Contents
----------------
[List of directories]

Total Size
----------
25M (unpacked)
8.1M (tar.gz)
15M (zip)

Verification
------------
sha256sum -c portier-v1.0.0.tar.gz.sha256
```

## 🛠️ Troubleshooting

### Issue: Checksum Verification Fails

**Solution:**

```bash
# Re-download the file
# Ensure no corruption during download
# Compare checksums manually
sha256sum portier-v1.0.0.tar.gz
cat portier-v1.0.0.tar.gz.sha256
```

### Issue: Setup Script Fails

**Solution:**

```bash
# Check Python version (requires 3.11+)
python3 --version

# Ensure pip is available
python3 -m pip --version

# Run setup with verbose output
bash -x setup.sh
```

### Issue: Missing Dependencies

**Solution:**

```bash
# Activate virtual environment
source .venv/bin/activate

# Manually install requirements
pip install -r requirements.txt
```

### Issue: Port Conflicts

**Solution:**

```bash
# Check which ports are in use
bash bin/check_ports.sh

# Kill conflicting processes or reconfigure ports in .env
```

## 📝 Customizing the Release Process

### Modify Included Files

Edit `bin/prepare_release.sh` and modify these functions:

- `copy_essential_directories()` - Change which agent dirs to include
- `copy_core_infrastructure()` - Modify infrastructure directories
- `copy_essential_documentation()` - Select which docs to include

### Add Custom Setup Steps

Edit the generated `setup.sh` by modifying the `create_setup_script()` function in `bin/prepare_release.sh`.

### Change Package Format

The script generates both tar.gz and zip by default. To add other formats:

```bash
# Add to generate_checksums() function
# Create .tar.xz for better compression
tar -cJf "$ARCHIVE_NAME.tar.xz" "$PACKAGE_NAME"
sha256sum "$ARCHIVE_NAME.tar.xz" > "$ARCHIVE_NAME.tar.xz.sha256"
```

## 🔐 Security Considerations

### Before Release

- ✅ Ensure no secrets in `.env` files
- ✅ Review all configuration files for sensitive data
- ✅ Verify `.gitignore` patterns are respected
- ✅ Remove any development API keys or tokens
- ✅ Check that `.env.example` contains only placeholders

### Distribution

- ✅ Use HTTPS for distribution
- ✅ Provide checksums for verification
- ✅ Sign releases with GPG (optional)
- ✅ Document required environment variables
- ✅ Include security documentation

### After Installation

- ✅ Users should rotate all API keys
- ✅ Generate new bearer tokens
- ✅ Review and update `.env` file
- ✅ Enable appropriate firewall rules
- ✅ Configure HTTPS if exposing services

## 📚 Additional Resources

- **System Architecture:** `docs/PORTIER_3.0_SYSTEM_ARCHITECTURE.md`
- **Operations Guide:** `OPERATIONS_COMPLETE.md`
- **Security Guide:** `SECURITY.md`
- **GitHub Repository:** <https://github.com/jokicdanijel/Gesamtprojekt-start>

## 📞 Support

For issues with the release package:

- **GitHub Issues:** <https://github.com/jokicdanijel/Gesamtprojekt-start/issues>
- **Email:** <jokicdanijel@gmail.com>

---

**Document Version:** 1.0
**Last Updated:** 2025-12-02
**Next Review:** 2026-01-02
