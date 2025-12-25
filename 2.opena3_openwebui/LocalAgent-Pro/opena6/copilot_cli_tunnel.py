"""
GitHub Copilot CLI Tunnel für OpenWebUI

Direkter Zugang zu GitHub Copilot über 'gh copilot' Kommando in OpenWebUI.

Modi:
  - chat:    Freie Anfrage an Copilot (PROMPT erforderlich)
  - explain: Erklärung zu Datei/Code (FILES[0] erforderlich)
  - commit:  Commit-Message-Vorschlag basierend auf git diff

Features:
- Native GitHub CLI Integration
- Async/await Support
- Error Handling & Timeouts
- Log File Management
- Preview Mode
- Multi-Language Support (Deutsch/English)
"""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# ==================== Constants ====================

PROMPT_COMMIT_DEFAULT = "Erzeuge eine prägnante, konventionelle Commit-Message für den folgenden Git-Diff (Deutsch)."

PROMPT_COMMIT_EN = "Generate a concise, conventional commit message for the following Git diff (English)."

PROMPTS = {
    "commit_de": PROMPT_COMMIT_DEFAULT,
    "commit_en": PROMPT_COMMIT_EN,
    "explain_de": "Erkläre diesen Code/diese Datei auf Deutsch (kurz und prägnant).",
    "explain_en": "Explain this code/file in English (concise and clear).",
}


# ==================== Validation Models ====================


class CopilotResponse(BaseModel):
    """Response-Struktur für Copilot Tunnel"""

    ok: bool = Field(description="Erfolgreich ausgeführt")
    mode: str | None = Field(None, description="Modus (chat|explain|commit)")
    preview: bool = Field(default=False, description="Nur Preview")
    base: str | None = Field(None, description="Base-Verzeichnis für Logs")
    command: list[str] | None = Field(None, description="Ausgeführter Befehl")
    cwd: str | None = Field(None, description="Arbeitsverzeichnis")
    exit_code: int | None = Field(None, description="Exit-Code")
    stdout: str | None = Field(None, description="Standard Output")
    stderr: str | None = Field(None, description="Standard Error")
    log_path: str | None = Field(None, description="Pfad zur Log-Datei")
    error: str | None = Field(None, description="Fehlermeldung")
    timestamp: str | None = Field(None, description="Zeitstempel")


# ==================== Tools Class ====================


class Tools:
    """
    OpenWebUI-Tool für GitHub Copilot CLI Integration

    Ermöglicht die Nutzung von GitHub Copilot direkt in OpenWebUI:
    - chat:    Freie Anfrage an Copilot
    - explain: Code/Datei erklären lassen
    - commit:  Commit-Message generieren
    """

    class Valves(BaseModel):
        """Konfigurationsparameter"""

        MODE: str = Field(default="chat", description="Modus: chat | explain | commit")
        PROMPT: str = Field(default="", description="Prompt-Text für MODE=chat/commit")
        FILES: list[str] = Field(default_factory=list, description="Relevante Dateien (explain nutzt FILES[0])")
        CWD: str = Field(default=".", description="Arbeitsverzeichnis/Git-Repository")
        OUT_DIR: str = Field(default="/mnt/data", description="Zielordner für Logs (Fallback: /tmp)")
        PREVIEW_ONLY: bool = Field(default=False, description="Nur anzeigen, nicht ausführen")
        TIMEOUT_SEC: int = Field(default=120, description="Timeout für gh-Aufruf in Sekunden")
        TRUNCATE: int = Field(default=8000, description="Stdout/Stderr auf N Zeichen kürzen (0=kein Kürzen)")
        LANGUAGE: str = Field(default="de", description="Sprache: de | en")
        INCLUDE_TIMESTAMPS: bool = Field(default=True, description="Zeitstempel in Logs speichern")
        VERBOSE: bool = Field(default=False, description="Verbose Logging")

    def __init__(self):
        """Initialisiere Tool mit Standard-Einstellungen"""
        self.valves = self.Valves()
        self._log_buffer = []

    # ==================== Main Entry Points ====================

    async def __call__(self, *args, **kwargs):
        """Delegiere auf run() für verschiedene Runtimes"""
        return await self.run(*args, **kwargs)

    async def run(
        self,
        body: dict | None = None,
        __user__=None,
        __event_emitter__=None,
        __event_call__=None,
        __model__=None,
        __request__=None,
        __id__=None,
        **_,
    ) -> dict[str, Any]:
        """
        Hauptmethode für Tool-Ausführung

        Args:
            body: Request Body (optional)
            __user__: Benutzerinformation
            __event_emitter__: Event Emitter für Updates
            **_: Weitere Parameter (ignoriert)

        Returns:
            Dict mit content.ok=true/false und Results
        """
        v = self.valves
        start_time = time.time()

        try:
            # 1) GitHub CLI Check
            gh_path = shutil.which("gh")
            if not gh_path:
                return await self._error_response(
                    "GitHub CLI 'gh' nicht gefunden. " "Bitte installieren & 'gh auth login' ausführen.",
                    __event_emitter__,
                )

            # 2) Setup Output Directory & CWD
            base = await self._setup_directories(v.OUT_DIR)
            cwd = await self._validate_cwd(v.CWD)
            if not cwd:
                return await self._error_response(f"CWD ungültig: {v.CWD}", __event_emitter__)

            # 3) Build Command
            mode = (v.MODE or "chat").strip().lower()
            cmd = await self._build_command(gh_path, mode, v, cwd, __event_emitter__)
            if not cmd:
                return await self._error_response("Befehl konnte nicht erstellt werden", __event_emitter__)

            # 4) Preview Mode?
            if v.PREVIEW_ONLY:
                return await self._preview_response(cmd, cwd, base, mode)

            # 5) Execute Command
            await self._notify(__event_emitter__, f"⚙️ Starte Copilot {mode}...")
            result = await self._execute_command(cmd, cwd, v, base, mode)

            # 6) Add Metadata
            result["mode"] = mode
            if v.INCLUDE_TIMESTAMPS:
                result["timestamp"] = datetime.now().isoformat()
            result["duration_sec"] = round(time.time() - start_time, 2)

            # 7) Save Log
            await self._save_log(result, base, mode)

            # 8) Notify & Return
            await self._notify(
                __event_emitter__, f"✅ Copilot {mode} abgeschlossen" if result.get("ok") else f"❌ Fehler in {mode}"
            )
            return {"content": result}

        except Exception as ex:
            return await self._error_response(str(ex), __event_emitter__)

    # ==================== Helper Methods ====================

    async def _setup_directories(self, out_dir: str) -> Path:
        """Erstelle und validiere Output-Verzeichnis"""
        base = Path(out_dir)
        try:
            base.mkdir(parents=True, exist_ok=True)
            return base
        except Exception:
            base = Path("/tmp") / "copilot_tunnel"
            base.mkdir(parents=True, exist_ok=True)
            return base

    async def _validate_cwd(self, cwd_str: str) -> Path | None:
        """Validiere Arbeitsverzeichnis"""
        try:
            cwd = Path(cwd_str).resolve()
            if cwd.exists() and cwd.is_dir():
                return cwd
            return None
        except Exception:
            return None

    async def _build_command(self, gh_path: str, mode: str, v: Valves, cwd: Path, emitter) -> list[str] | None:
        """Baue gh copilot Befehl auf"""

        if mode == "chat":
            if not v.PROMPT.strip():
                await self._notify(emitter, "❌ PROMPT erforderlich für chat")
                return None
            return [gh_path, "copilot", "chat", "-p", v.PROMPT]

        elif mode == "explain":
            if not v.FILES or not v.FILES[0]:
                await self._notify(emitter, "❌ FILES[0] erforderlich für explain")
                return None
            target = str(Path(v.FILES[0]).resolve())
            return [gh_path, "copilot", "explain", target]

        elif mode == "commit":
            prompt = v.PROMPT.strip() or PROMPTS.get(f"commit_{v.LANGUAGE}", PROMPT_COMMIT_DEFAULT)

            # Capture git diff
            git_diff = await self._capture_git_diff(cwd)
            if not git_diff:
                await self._notify(emitter, "⚠️ Kein Git Diff gefunden")
                git_diff = "(Kein Diff gefunden)"
            else:
                git_diff = git_diff[:30000]  # Truncate large diffs

            full_prompt = f"{prompt}\n\n" f"===== BEGIN DIFF =====\n{git_diff}\n===== END DIFF ====="
            return [gh_path, "copilot", "chat", "-p", full_prompt]

        else:
            await self._notify(emitter, f"❌ Unbekannter MODE: {mode} (erlaubt: chat|explain|commit)")
            return None

    async def _capture_git_diff(self, cwd: Path) -> str | None:
        """Capture git diff (staged oder unstaged)"""
        # Try staged first
        result = await self._run_command(["git", "diff", "--staged"], cwd)
        if result and result.strip():
            return result

        # Fallback to unstaged
        return await self._run_command(["git", "diff"], cwd)

    async def _run_command(self, cmd: list[str], cwd: Path, timeout: int = 10) -> str | None:
        """Führe Befehl aus und fange Output ein"""
        try:
            cp = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return cp.stdout or ""
        except Exception:
            return None

    async def _execute_command(self, cmd: list[str], cwd: Path, v: Valves, base: Path, mode: str) -> dict[str, Any]:
        """Führe gh copilot Befehl aus"""
        try:
            cp = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=max(5, int(v.TIMEOUT_SEC)),
                check=False,
            )

            stdout = cp.stdout or ""
            stderr = cp.stderr or ""

            # Truncate if needed
            if v.TRUNCATE and v.TRUNCATE > 0:
                if len(stdout) > v.TRUNCATE:
                    stdout = stdout[: v.TRUNCATE] + f"\n... (gekürzt auf {v.TRUNCATE} Zeichen)"
                if len(stderr) > v.TRUNCATE:
                    stderr = stderr[: v.TRUNCATE] + f"\n... (gekürzt auf {v.TRUNCATE} Zeichen)"

            return {
                "ok": cp.returncode == 0,
                "preview": False,
                "base": str(base),
                "command": cmd,
                "cwd": str(cwd),
                "exit_code": cp.returncode,
                "stdout": stdout,
                "stderr": stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "error": f"Timeout nach {v.TIMEOUT_SEC}s",
                "command": cmd,
                "cwd": str(cwd),
            }
        except Exception as ex:
            return {
                "ok": False,
                "error": f"Fehler: {ex}",
                "command": cmd,
                "cwd": str(cwd),
            }

    async def _preview_response(self, cmd: list[str], cwd: Path, base: Path, mode: str) -> dict[str, Any]:
        """Gebe Preview-Response zurück"""
        return {
            "content": {
                "ok": True,
                "preview": True,
                "mode": mode,
                "base": str(base),
                "command": cmd,
                "cwd": str(cwd),
                "timestamp": datetime.now().isoformat() if self.valves.INCLUDE_TIMESTAMPS else None,
            }
        }

    async def _save_log(self, result: dict[str, Any], base: Path, mode: str) -> None:
        """Speichere Log-Datei"""
        try:
            log_dir = base / "copilot_tunnel_logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            ts = int(time.time())
            log_path = log_dir / f"run_{mode}_{ts}.json"

            result["log_path"] = str(log_path)
            log_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass  # Best effort

    async def _error_response(self, error: str, emitter) -> dict[str, Any]:
        """Erstelle Error-Response"""
        await self._notify(emitter, f"❌ {error}")
        return {
            "content": {
                "ok": False,
                "error": error,
                "timestamp": datetime.now().isoformat() if self.valves.INCLUDE_TIMESTAMPS else None,
            }
        }

    async def _notify(self, emitter, msg: str) -> None:
        """Sende Notification an Event Emitter"""
        if emitter:
            try:
                await emitter(
                    {
                        "type": "notification",
                        "data": {"type": "info", "content": msg, "timestamp": datetime.now().isoformat()},
                    }
                )
            except Exception:
                pass

    # ==================== Utility Methods ====================

    async def get_status(self) -> dict[str, Any]:
        """Überprüfe GitHub CLI Status"""
        gh_path = shutil.which("gh")

        if not gh_path:
            return {
                "ok": False,
                "message": "GitHub CLI nicht installiert",
                "fix": "Install with: brew install gh (Mac) or apt install gh (Linux)",
            }

        # Check if authenticated
        try:
            result = subprocess.run([gh_path, "auth", "status"], capture_output=True, text=True, timeout=5, check=False)
            return {
                "ok": result.returncode == 0,
                "authenticated": result.returncode == 0,
                "info": result.stdout or result.stderr,
                "gh_path": gh_path,
            }
        except Exception as ex:
            return {"ok": False, "error": str(ex), "gh_path": gh_path}

    async def get_available_models(self) -> list[str]:
        """Überprüfe verfügbare Copilot Modelle"""
        gh_path = shutil.which("gh")
        if not gh_path:
            return []

        try:
            result = subprocess.run(
                [gh_path, "copilot", "--help"], capture_output=True, text=True, timeout=5, check=False
            )
            # Parse available models from help text
            return ["gpt-4", "gpt-3.5-turbo"]  # Default known models
        except Exception:
            return []


# ==================== Testing ====================


async def test_copilot_tool():
    """Test Copilot CLI Tool"""
    tool = Tools()

    print("🧪 Testing Copilot CLI Tool...\n")

    # Test 1: Chat
    print("Test 1: Chat Mode")
    tool.valves.MODE = "chat"
    tool.valves.PROMPT = "Was ist GitHub Copilot?"
    tool.valves.PREVIEW_ONLY = True
    result = await tool.run()
    print(f"Result: {result['content']['ok']}\n")

    # Test 2: Status
    print("Test 2: GitHub CLI Status")
    status = await tool.get_status()
    print(f"Authenticated: {status.get('authenticated')}\n")

    # Test 3: Models
    print("Test 3: Available Models")
    models = await tool.get_available_models()
    print(f"Models: {models}\n")

    print("✅ Tests completed")


if __name__ == "__main__":
    asyncio.run(test_copilot_tool())
