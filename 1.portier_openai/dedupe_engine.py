"""
dedupe_engine.py – Deduplication & Integrity Engine (Schritt 3)
Implements SHA-256 content deduplication, HEADS tracking, and INTEGRITY verification.
Integrates with safepoint lifecycle for append-only archival.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class DedupeRecord:
    """Represents a deduplicated safepoint entry."""
    sp_path: str              # Safepoint file path
    sha256_hash: str          # SHA-256 hash of content
    content_size: int         # Bytes
    first_seen_ts: str        # ISO-8601 Z timestamp
    occurrence_count: int     # How many times this hash appeared
    sources: list = field(default_factory=list)  # Agent sources


@dataclass
class IntegrityCheckpoint:
    """Represents a checkpoint in the integrity chain."""
    checkpoint_id: str        # Unique ID (unix_ts_nanoc)
    previous_hash: str        # HEADS[n-1] SHA-256
    current_hash: str         # HEADS[n] SHA-256
    entries_in_window: int    # How many dedupe records processed
    timestamp_utc: str        # ISO-8601 Z
    meta: dict = field(default_factory=dict)


class DedupeEngine:
    """
    Central deduplication engine with:
    - SHA-256 content hashing
    - HEADS.json tracking (append-only chain)
    - INTEGRITY.json verification (checkpoint integrity)
    - Append-only index integration
    """

    def __init__(self, archiv_root: Path = Path("archivp")):
        """
        Initialize dedupe engine.
        
        Args:
            archiv_root: Path to archivp root directory
        """
        self.archiv_root = Path(archiv_root)
        self.heads_file = self.archiv_root / "HEADS.json"
        self.integrity_file = self.archiv_root / "INTEGRITY.json"
        self.dedupe_cache: Dict[str, DedupeRecord] = {}
        self._load_heads()
        self._load_integrity()

    def _load_heads(self) -> None:
        """Load HEADS.json (append-only chain of hashes)."""
        if self.heads_file.exists():
            try:
                with open(self.heads_file, "r") as f:
                    self.heads = json.load(f)
                logger.info(f"✓ Loaded HEADS.json with {len(self.heads)} entries")
            except Exception as e:
                logger.error(f"Failed to load HEADS.json: {e}")
                self.heads = []
        else:
            self.heads = []
            logger.info("HEADS.json not found (first run)")

    def _load_integrity(self) -> None:
        """Load INTEGRITY.json (verification checkpoints)."""
        if self.integrity_file.exists():
            try:
                with open(self.integrity_file, "r") as f:
                    self.integrity = json.load(f)
                logger.info(f"✓ Loaded INTEGRITY.json with {len(self.integrity)} checkpoints")
            except Exception as e:
                logger.error(f"Failed to load INTEGRITY.json: {e}")
                self.integrity = []
        else:
            self.integrity = []
            logger.info("INTEGRITY.json not found (first run)")

    def compute_hash(self, content: dict) -> str:
        """
        Compute SHA-256 hash of JSON content.
        
        Args:
            content: Dictionary to hash
            
        Returns:
            SHA-256 hex digest
        """
        content_str = json.dumps(content, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    def register_safepoint(
        self,
        sp_path: str,
        content: dict,
        source_agent: str
    ) -> Dict[str, Any]:
        """
        Register a safepoint and check for duplicates.
        
        Args:
            sp_path: Path to safepoint file
            content: Safepoint content dict
            source_agent: Agent that created the safepoint
            
        Returns:
            Dict with {is_duplicate, hash, record}
        """
        sha256 = self.compute_hash(content)
        
        # Check if already exists in dedupe cache
        if sha256 in self.dedupe_cache:
            record = self.dedupe_cache[sha256]
            record.occurrence_count += 1
            record.sources.append(source_agent)
            logger.info(f"⚠️  Duplicate detected (hash={sha256[:16]}...): {sp_path}")
            return {
                "is_duplicate": True,
                "hash": sha256,
                "record": asdict(record),
                "occurrence_count": record.occurrence_count
            }
        
        # New content
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        record = DedupeRecord(
            sp_path=sp_path,
            sha256_hash=sha256,
            content_size=len(json.dumps(content)),
            first_seen_ts=now_utc,
            occurrence_count=1,
            sources=[source_agent]
        )
        self.dedupe_cache[sha256] = record
        logger.info(f"✓ New content registered (hash={sha256[:16]}...): {sp_path}")
        
        return {
            "is_duplicate": False,
            "hash": sha256,
            "record": asdict(record),
            "occurrence_count": 1
        }

    def append_head(self, new_hash: str, meta: Optional[Dict] = None) -> None:
        """
        Append a new hash to HEADS.json (append-only).
        
        Args:
            new_hash: SHA-256 hash to append
            meta: Optional metadata dict
        """
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        entry = {
            "hash": new_hash,
            "sequence": len(self.heads),
            "timestamp": now_utc,
            "meta": meta or {}
        }
        self.heads.append(entry)
        self._save_heads()

    def _save_heads(self) -> None:
        """Save HEADS.json to disk."""
        self.heads_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.heads_file, "w") as f:
            json.dump(self.heads, f, indent=2)
        logger.debug(f"✓ HEADS.json saved ({len(self.heads)} entries)")

    def create_checkpoint(self, window_label: str = "default") -> Optional[Dict]:
        """
        Create an integrity checkpoint (append to INTEGRITY.json).
        
        Args:
            window_label: Label for this checkpoint window
            
        Returns:
            Checkpoint dict or None on error
        """
        if len(self.heads) < 2:
            logger.warning("Insufficient HEADS entries for checkpoint")
            return None

        # Compute current HEADS hash
        current_heads_hash = self.compute_hash({"heads": self.heads})
        previous_heads_hash = self.heads[-2]["hash"] if len(self.heads) > 1 else "GENESIS"

        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        checkpoint = {
            "checkpoint_id": f"CP_{int(datetime.now(timezone.utc).timestamp())}",
            "window_label": window_label,
            "previous_head": previous_heads_hash,
            "current_head": current_heads_hash,
            "entries_in_cache": len(self.dedupe_cache),
            "timestamp_utc": now_utc,
            "heads_chain_length": len(self.heads)
        }
        
        self.integrity.append(checkpoint)
        self._save_integrity()
        logger.info(f"✓ Checkpoint created: {checkpoint['checkpoint_id']}")
        
        return checkpoint

    def _save_integrity(self) -> None:
        """Save INTEGRITY.json to disk."""
        self.integrity_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.integrity_file, "w") as f:
            json.dump(self.integrity, f, indent=2)
        logger.debug(f"✓ INTEGRITY.json saved ({len(self.integrity)} checkpoints)")

    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify HEADS and INTEGRITY consistency.
        
        Returns:
            Dict with {is_valid, errors, warnings}
        """
        errors = []
        warnings = []

        # Check HEADS sequence
        for i, head in enumerate(self.heads):
            if head.get("sequence") != i:
                errors.append(f"HEADS[{i}]: sequence mismatch (got {head.get('sequence')})")

        # Check INTEGRITY chain
        for i, cp in enumerate(self.integrity):
            if i > 0:
                prev_cp = self.integrity[i - 1]
                if prev_cp["current_head"] != cp["previous_head"]:
                    errors.append(f"INTEGRITY[{i}]: broken chain link")

        if not errors:
            logger.info("✓ Integrity verification PASSED")

        return {
            "is_valid": len(errors) == 0,
            "heads_entries": len(self.heads),
            "integrity_checkpoints": len(self.integrity),
            "dedupe_cache_size": len(self.dedupe_cache),
            "errors": errors,
            "warnings": warnings
        }

    def get_dedupe_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics."""
        total_unique = len(self.dedupe_cache)
        total_occurrences = sum(r.occurrence_count for r in self.dedupe_cache.values())
        total_size_bytes = sum(r.content_size for r in self.dedupe_cache.values())
        
        duplicates = sum(1 for r in self.dedupe_cache.values() if r.occurrence_count > 1)
        duplicate_occurrences = sum(
            r.occurrence_count - 1 for r in self.dedupe_cache.values() if r.occurrence_count > 1
        )

        return {
            "unique_contents": total_unique,
            "total_occurrences": total_occurrences,
            "duplicate_records": duplicates,
            "duplicate_occurrences": duplicate_occurrences,
            "savings_factor": f"{(total_occurrences - duplicate_occurrences) / max(1, duplicate_occurrences):.2f}x"
            if duplicate_occurrences > 0 else "N/A",
            "total_size_bytes": total_size_bytes,
            "average_size_bytes": total_size_bytes // max(1, total_unique)
        }


class SafepointManager:
    """
    Manages safepoint lifecycle with dedupe integration.
    Handles persistence, indexing, and integrity tracking.
    """

    def __init__(self, archiv_root: Path = Path("archivp"), dedupe_engine: Optional[DedupeEngine] = None):
        """
        Initialize safepoint manager.
        
        Args:
            archiv_root: Path to archivp root
            dedupe_engine: Optional DedupeEngine instance
        """
        self.archiv_root = Path(archiv_root)
        self.dedupe = dedupe_engine or DedupeEngine(archiv_root)
        self.index_file = self.archiv_root / "YYYY" / "MM" / "DD" / "index.jsonl"

    def write_safepoint(
        self,
        sp_path: str,
        content: dict,
        source_agent: str
    ) -> Dict[str, Any]:
        """
        Write a safepoint with dedupe + integrity tracking.
        
        Args:
            sp_path: Safepoint file path
            content: Safepoint content
            source_agent: Source agent ID
            
        Returns:
            Result dict with status, hash, duplicate flag
        """
        # Register with dedupe engine
        dedupe_result = self.dedupe.register_safepoint(sp_path, content, source_agent)
        
        # Write to disk
        sp_full_path = self.archiv_root / sp_path
        sp_full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(sp_full_path, "w") as f:
                json.dump(content, f, indent=2)
            logger.info(f"✓ Safepoint written: {sp_path}")
        except Exception as e:
            logger.error(f"Failed to write safepoint {sp_path}: {e}")
            return {"success": False, "error": str(e)}

        # Append head for integrity chain
        self.dedupe.append_head(dedupe_result["hash"], {"sp_path": sp_path, "source": source_agent})

        return {
            "success": True,
            "sp_path": sp_path,
            "hash": dedupe_result["hash"],
            "is_duplicate": dedupe_result["is_duplicate"],
            "occurrence_count": dedupe_result["occurrence_count"]
        }

    def read_safepoint(self, sp_path: str) -> Optional[dict]:
        """
        Read a safepoint from disk.
        
        Args:
            sp_path: Safepoint file path
            
        Returns:
            Safepoint dict or None
        """
        sp_full_path = self.archiv_root / sp_path
        if not sp_full_path.exists():
            logger.warning(f"Safepoint not found: {sp_path}")
            return None

        try:
            with open(sp_full_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read safepoint {sp_path}: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get full status report."""
        integrity_report = self.dedupe.verify_integrity()
        dedupe_stats = self.dedupe.get_dedupe_stats()

        return {
            "archiv_root": str(self.archiv_root),
            "integrity": integrity_report,
            "dedupe_stats": dedupe_stats,
            "heads_file_exists": self.dedupe.heads_file.exists(),
            "integrity_file_exists": self.dedupe.integrity_file.exists()
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

    # Initialize
    engine = DedupeEngine(Path("archivp"))
    manager = SafepointManager(Path("archivp"), engine)

    # Example safepoint
    sp = {
        "src": "opena1",
        "dst": "opena2",
        "kind": "CMD",
        "strict": True,
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "payload": {"msg": "test"}
    }

    # Write
    result = manager.write_safepoint(
        "2025/11/10/SP1731155200_opena1->opena2_CMD.json",
        sp,
        "opena1"
    )
    print(f"Write result: {json.dumps(result, indent=2)}")

    # Get status
    status = manager.get_status()
    print(f"\nStatus:\n{json.dumps(status, indent=2)}")

    # Verify integrity
    integrity = engine.verify_integrity()
    print(f"\nIntegrity:\n{json.dumps(integrity, indent=2)}")
