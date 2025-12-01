#!/usr/bin/env python3
"""
commit_and_pr.py - Agent Commit & PR Helper

Erstellt automatisch einen Branch, committet Änderungen und erstellt einen PR.
Benötigt: git, gh (GitHub CLI) oder GITHUB_TOKEN

Verwendung:
    python3 tools/commit_and_pr.py "agent-generated/feature-x" "AGENT: feature-x (task123)"
"""

import subprocess
import sys
import os
from pathlib import Path
import uuid
from datetime import datetime
import json

BASE = Path(__file__).resolve().parents[1]
ARCHIV_INDEX = BASE / "archivp" / "index.jsonl"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Führt einen Befehl aus und loggt ihn."""
    print(f"+ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def log_safepoint(action: str, path: str, entries: int = 0) -> None:
    """Schreibt einen Safepoint-Eintrag in archivp/index.jsonl."""
    ARCHIV_INDEX.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "path": path,
        "entries": entries,
        "agent": "commit_and_pr"
    }
    
    with open(ARCHIV_INDEX, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"📝 Safepoint: {action} → {path}")


def check_git_status() -> bool:
    """Prüft ob Git-Repo sauber ist und Remote erreichbar."""
    # Prüfe ob wir in einem Git-Repo sind
    result = run(["git", "rev-parse", "--git-dir"], check=False)
    if result.returncode != 0:
        print("❌ Nicht in einem Git-Repository!")
        return False
    
    # Prüfe Remote-Erreichbarkeit
    result = run(["git", "ls-remote", "--exit-code", "origin"], check=False)
    if result.returncode != 0:
        print("❌ Git Remote 'origin' nicht erreichbar!")
        return False
    
    return True


def check_gh_auth() -> bool:
    """Prüft ob GitHub CLI eingeloggt ist."""
    result = run(["gh", "auth", "status"], check=False)
    if result.returncode != 0:
        print("⚠️  GitHub CLI nicht eingeloggt. Führe aus: gh auth login")
        return False
    return True


def create_branch_and_pr(branch: str, message: str, dry_run: bool = False) -> dict:
    """Erstellt Branch, committet und erstellt PR."""
    
    # 1. Safepoint vor Änderungen
    log_safepoint("PRE_COMMIT", branch)
    
    # 2. Prüfe Git-Status
    if not check_git_status():
        return {"status": "error", "message": "Git check failed"}
    
    # 3. Aktuellen Branch merken
    current = run(["git", "branch", "--show-current"], check=False)
    original_branch = current.stdout.strip() if current.returncode == 0 else "main"
    
    try:
        # 4. Neuen Branch erstellen
        print(f"\n🌿 Erstelle Branch: {branch}")
        if not dry_run:
            # Prüfe ob Branch existiert
            result = run(["git", "show-ref", "--verify", f"refs/heads/{branch}"], check=False)
            if result.returncode == 0:
                run(["git", "checkout", branch])
            else:
                run(["git", "checkout", "-b", branch])
        
        # 5. Änderungen staged?
        status = run(["git", "status", "--porcelain"], check=False)
        if not status.stdout.strip():
            print("ℹ️  Keine Änderungen zum Committen.")
            return {"status": "no_changes", "branch": branch}
        
        # 6. Add & Commit
        print(f"\n📦 Committe: {message}")
        if not dry_run:
            run(["git", "add", "."])
            run(["git", "commit", "-m", message])
        
        # 7. Push
        print(f"\n🚀 Push zu origin/{branch}")
        if not dry_run:
            run(["git", "push", "--set-upstream", "origin", branch])
        
        # 8. PR erstellen (wenn gh eingeloggt)
        pr_url = None
        if check_gh_auth() and not dry_run:
            print("\n📋 Erstelle Pull Request...")
            result = run([
                "gh", "pr", "create",
                "--fill",
                "--body", f"Automated PR by Portier agents\n\nBranch: {branch}\nMessage: {message}",
                "--title", message
            ], check=False)
            
            if result.returncode == 0:
                pr_url = result.stdout.strip()
                print(f"✅ PR erstellt: {pr_url}")
            else:
                print(f"⚠️  PR-Erstellung fehlgeschlagen: {result.stderr}")
        
        # 9. Safepoint nach Erfolg
        log_safepoint("POST_COMMIT", branch, entries=len(status.stdout.strip().split("\n")))
        
        return {
            "status": "ok",
            "branch": branch,
            "message": message,
            "pr_url": pr_url,
            "files_changed": len(status.stdout.strip().split("\n"))
        }
        
    except subprocess.CalledProcessError as e:
        log_safepoint("COMMIT_ERROR", branch)
        print(f"❌ Fehler: {e}")
        return {"status": "error", "message": str(e)}
    
    finally:
        # Zurück zum ursprünglichen Branch
        if not dry_run:
            run(["git", "checkout", original_branch], check=False)


def main():
    """Hauptfunktion."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Commit & PR Helper")
    parser.add_argument("branch", nargs="?", 
                       default=f"agent-generated/{uuid.uuid4().hex[:8]}",
                       help="Branch-Name (default: agent-generated/<uuid>)")
    parser.add_argument("message", nargs="?",
                       default="AGENT: automated changes",
                       help="Commit-Nachricht")
    parser.add_argument("--dry-run", action="store_true",
                       help="Nur simulieren, keine echten Änderungen")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 Agent Commit & PR Helper")
    print("=" * 60)
    print(f"Branch:  {args.branch}")
    print(f"Message: {args.message}")
    print(f"Dry-Run: {args.dry_run}")
    print("=" * 60)
    
    os.chdir(BASE)
    result = create_branch_and_pr(args.branch, args.message, args.dry_run)
    
    print("\n" + "=" * 60)
    print("📊 Ergebnis:")
    print(json.dumps(result, indent=2))
    print("=" * 60)
    
    return 0 if result.get("status") in ("ok", "no_changes") else 1


if __name__ == "__main__":
    sys.exit(main())
