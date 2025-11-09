#!/usr/bin/env bash
set -euo pipefail

# Archivator Release Script
# Erstellt GitHub Release mit Checksummen & SBOM

TIMESTAMP="${1:-$(date +%Y%m%d-%H%M%S)}"
BACKUP_DIR="backups"
TAG="vSTRUCTURE-${TIMESTAMP}"
SBOM_FILE="$BACKUP_DIR/sbom-${TIMESTAMP}.json"
RELEASE_NOTES_FILE="/tmp/release_notes_${TIMESTAMP}.md"

mkdir -p "$BACKUP_DIR"

echo "[Release] Creating artifacts for $TAG..."

# 1. Packe Quellen (tar.gz)
echo "[Release] Packing tar.gz..."
tar --exclude=.git --exclude=.venv --exclude=backups --exclude=_conflicts \
    -czf "$BACKUP_DIR/portier-$TIMESTAMP.tar.gz" \
    --exclude="*.pyc" --exclude="__pycache__" \
    . 2>/dev/null || echo "⚠ tar.gz creation skipped"

# 2. Packe als zip
echo "[Release] Packing zip..."
zip -r "$BACKUP_DIR/portier-$TIMESTAMP.zip" \
    . -x ".git/*" ".venv/*" "backups/*" "_conflicts/*" "*.pyc" "__pycache__/*" \
    2>/dev/null || echo "⚠ zip creation skipped"

# 3. Erzeuge SHA256 Checksummen
echo "[Release] Generating checksums..."
cd "$BACKUP_DIR"
sha256sum portier-$TIMESTAMP.tar.gz > portier-$TIMESTAMP.tar.gz.sha256 2>/dev/null || true
sha256sum portier-$TIMESTAMP.zip > portier-$TIMESTAMP.zip.sha256 2>/dev/null || true
cd - > /dev/null

# 4. SBOM (fallback, wenn syft nicht vorhanden)
echo "[Release] Generating SBOM..."
if command -v syft &> /dev/null; then
    syft packages . -o spdx-json > "$SBOM_FILE" 2>/dev/null || echo "⚠ SBOM via syft failed"
else
    echo "⚠ syft not available - generating minimal SBOM"
    cat > "$SBOM_FILE" << 'EOF'
{
  "spdxVersion": "SPDX-2.3",
  "creationInfo": {
    "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  },
  "name": "Portier OpenAI",
  "packages": []
}
EOF
fi

# 5. Erzeuge Release Notes
echo "[Release] Creating release notes..."
cat > "$RELEASE_NOTES_FILE" << EOF
# Portier Structure Release $TIMESTAMP

## 📦 Artifacts
- \`portier-$TIMESTAMP.tar.gz\` - Full project archive
- \`portier-$TIMESTAMP.zip\` - ZIP format
- \`sbom-$TIMESTAMP.json\` - SBOM

## ✅ Verification
Verify integrity:
\`\`\`bash
sha256sum -c backups/portier-$TIMESTAMP.tar.gz.sha256
\`\`\`

## 📊 Statistics
- Timestamp: $TIMESTAMP
- Tag: $TAG
- Backups: $(ls -1 $BACKUP_DIR/*.tar.gz 2>/dev/null | wc -l) archives
- SBOM: See sbom-$TIMESTAMP.json

## 📋 Reports
See attached:
- \`rename_map.csv\`
- \`path_index.json\`
- \`violations_report.md\`
- \`structure_checkpoint.json\`
EOF

# 6. Anhängen der Reports zu Release Notes
if [ -f rename_map.csv ]; then
    echo "" >> "$RELEASE_NOTES_FILE"
    echo "## 📝 Rename Map" >> "$RELEASE_NOTES_FILE"
    echo "\`\`\`csv" >> "$RELEASE_NOTES_FILE"
    head -20 rename_map.csv >> "$RELEASE_NOTES_FILE"
    echo "...(see artifacts)" >> "$RELEASE_NOTES_FILE"
    echo "\`\`\`" >> "$RELEASE_NOTES_FILE"
fi

# 7. GitHub Release (falls gh verfügbar)
if command -v gh &> /dev/null; then
    echo "[Release] Publishing to GitHub..."
    if gh release view "$TAG" &>/dev/null; then
        echo "⚠ Release $TAG already exists, skipping upload"
    else
        gh release create "$TAG" \
            "$BACKUP_DIR/portier-$TIMESTAMP.tar.gz" \
            "$BACKUP_DIR/portier-$TIMESTAMP.tar.gz.sha256" \
            "$BACKUP_DIR/portier-$TIMESTAMP.zip" \
            "$BACKUP_DIR/portier-$TIMESTAMP.zip.sha256" \
            "$SBOM_FILE" \
            rename_map.csv \
            path_index.json \
            violations_report.md \
            structure_checkpoint.json \
            --notes-file "$RELEASE_NOTES_FILE" \
            2>/dev/null || echo "⚠ gh release failed (check permissions)"
    fi
else
    echo "⚠ gh CLI not available - local artifacts only"
fi

echo "✅ Release artifacts ready in $BACKUP_DIR/"
echo "   - portier-$TIMESTAMP.tar.gz"
echo "   - portier-$TIMESTAMP.tar.gz.sha256"
echo "   - portier-$TIMESTAMP.zip"
echo "   - portier-$TIMESTAMP.zip.sha256"
echo "   - sbom-$TIMESTAMP.json"
echo "   - Release notes: $RELEASE_NOTES_FILE"
