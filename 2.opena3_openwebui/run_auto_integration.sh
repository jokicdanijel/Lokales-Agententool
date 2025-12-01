#!/bin/bash
# ELION Auto-Integration Orchestrator
# Automatische Ausführung: Indexierung → Feeding → Validierung

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_ROOT="${BASE_ROOT:-/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 ELION Auto-Integration Orchestrator"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ──────────────────────────────────────────────────────────────────────────────
# Phase 1: Auto-Indexierung
# ──────────────────────────────────────────────────────────────────────────────

echo "[1/3] 📊 Auto-Indexierung..."
echo ""

if [ -f "$SCRIPT_DIR/elion_auto_indexer.py" ]; then
    python3 "$SCRIPT_DIR/elion_auto_indexer.py" --verbose
    INDEX_STATUS=$?
    
    if [ $INDEX_STATUS -eq 0 ]; then
        echo ""
        echo "✓ Auto-Indexierung erfolgreich"
    else
        echo ""
        echo "✗ Auto-Indexierung fehlgeschlagen (Exit Code: $INDEX_STATUS)"
        exit 1
    fi
else
    echo "✗ elion_auto_indexer.py nicht gefunden"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ──────────────────────────────────────────────────────────────────────────────
# Phase 2: Knowledgebase-Feeding
# ──────────────────────────────────────────────────────────────────────────────

echo "[2/3] 🧠 Knowledgebase-Feeding..."
echo ""

if [ -f "$SCRIPT_DIR/knowledge_feeder.py" ]; then
    python3 "$SCRIPT_DIR/knowledge_feeder.py" --verbose
    FEED_STATUS=$?
    
    if [ $FEED_STATUS -eq 0 ]; then
        echo ""
        echo "✓ Knowledgebase-Feeding erfolgreich"
    else
        echo ""
        echo "✗ Knowledgebase-Feeding fehlgeschlagen (Exit Code: $FEED_STATUS)"
        exit 1
    fi
else
    echo "✗ knowledge_feeder.py nicht gefunden"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ──────────────────────────────────────────────────────────────────────────────
# Phase 3: Validierung
# ──────────────────────────────────────────────────────────────────────────────

echo "[3/3] ✓ Validierung..."
echo ""

# Prüfe ob Verzeichnisse existieren
AUTO_INDEX_DIR="$SCRIPT_DIR/auto_indexed"
KB_DIR="$BASE_ROOT/1.opena1&2_portier/knowledgebase"

if [ -d "$AUTO_INDEX_DIR" ]; then
    INDEXED_FILES=$(find "$AUTO_INDEX_DIR" -type f | wc -l)
    echo "  ✓ Auto-Index Verzeichnis: $INDEXED_FILES Dateien"
else
    echo "  ✗ Auto-Index Verzeichnis nicht gefunden"
fi

if [ -f "$AUTO_INDEX_DIR/index_metadata.jsonl" ]; then
    METADATA_ENTRIES=$(wc -l < "$AUTO_INDEX_DIR/index_metadata.jsonl")
    echo "  ✓ Metadata-Einträge: $METADATA_ENTRIES"
else
    echo "  ℹ Metadata-Datei noch nicht erstellt"
fi

if [ -f "$KB_DIR/kb_index.jsonl" ]; then
    KB_ENTRIES=$(wc -l < "$KB_DIR/kb_index.jsonl")
    echo "  ✓ Knowledgebase-Einträge: $KB_ENTRIES"
else
    echo "  ℹ KB-Index noch nicht erstellt"
fi

# Prüfe Ordnerstruktur-Integrität
echo ""
echo "  Ordnerstruktur-Integrität:"

EXPECTED_DIRS=(
    "1.opena1&2_portier"
    "2.opena3_openwebui"
    "3.opena4_telegram"
)

for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$BASE_ROOT/$dir" ]; then
        echo "    ✓ $dir"
    else
        echo "    ✗ $dir (fehlt)"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ ELION Auto-Integration abgeschlossen"
echo ""
echo "📂 Ausgabeverzeichnisse:"
echo "   Auto-Index:    $AUTO_INDEX_DIR"
echo "   Knowledgebase: $KB_DIR"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
