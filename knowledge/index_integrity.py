import hashlib
import json
import os


def canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class IndexIntegrityManager:
    """Provides append-with-checksum and startup verify+recover for append-only index files.

    Line format: <canonical_json>\t<sha256>\n
    Methods:
      - append_line(file_path, data_dict)
      - verify_and_recover(file_path) -> (recovered_lines: int)
    """

    @staticmethod
    def append_line(file_path: str, data: dict) -> None:
        line_json = canonical_json(data)
        checksum = sha256_hex(line_json)
        line = f"{line_json}\t{checksum}\n"

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Append and fsync to minimize risk of partial writes
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

    @staticmethod
    def verify_and_recover(file_path: str) -> int:
        """Verify each line; if corruption found, truncate file to last good line.

        Returns the number of truncated/corrupted lines removed.
        """
        if not os.path.exists(file_path):
            return 0

        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        last_good_index = -1
        for i, raw in enumerate(lines):
            # strip only trailing newline
            line = raw.rstrip("\n")
            if "\t" not in line:
                # malformed
                break
            payload, checksum = line.rsplit("\t", 1)
            try:
                # Validate checksum
                calc = sha256_hex(payload)
                if calc != checksum:
                    break
                # Validate JSON
                json.loads(payload)
                last_good_index = i
            except Exception:
                break

        if last_good_index == len(lines) - 1:
            # All good
            return 0

        # Truncate file to last_good_index+1 lines
        byte_offset = 0
        for j in range(last_good_index + 1):
            byte_offset += len(lines[j].encode("utf-8"))

        # Truncate and fsync
        with open(file_path, "r+b") as f:
            f.truncate(byte_offset)
            f.flush()
            os.fsync(f.fileno())

        removed = len(lines) - (last_good_index + 1)
        # metrics: record recovery
        try:
            from .metrics import inc_counter

            inc_counter("kb_index_recovery_total")
            inc_counter("kb_index_verify_fail_total")
        except Exception:
            pass
        return removed
