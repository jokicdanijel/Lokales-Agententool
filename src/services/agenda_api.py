#!/usr/bin/env python3
"""
agenda_api.py — FastAPI-Backend für 16 Agenda-Seiten
- Login/Auth (Bearer Token)
- CRUD-Operationen für Agenda-Seiten
- OpenWebUI Tool-Server Integration
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# ====================================================================
# CONFIGURATION
# ====================================================================

AGENDA_FILE = Path(__file__).parent.parent / "configs" / "agenda_pages.json"
VALID_TOKEN = "250886"  # In Produktion: Vault/Environment
VALID_USERNAME = "admin"
VALID_PASSWORD = "250886"

app = FastAPI(
    title="Agenda Pages API",
    description="16-Seiten Agenda mit Login und CRUD-Operationen",
    version="1.0.0"
)

auth_scheme = HTTPBearer()

# ====================================================================
# MODELS
# ====================================================================

class LoginRequest(BaseModel):
    """Login-Request Modell."""
    username: str
    password: str

class LoginResponse(BaseModel):
    """Login-Response mit Bearer-Token."""
    token: str
    message: str

class PageHistory(BaseModel):
    """Änderungshistorie einer Seite."""
    ts: str
    action: str
    by: str

class PageEntry(BaseModel):
    """Agenda-Seite."""
    id: str
    title: str
    api_endpoint: str
    bromt: str
    status: str
    last_updated: str
    history: List[Dict]

class PageUpdate(BaseModel):
    """Update-Payload für Seite."""
    title: Optional[str] = None
    bromt: Optional[str] = None
    status: Optional[str] = None
    api_endpoint: Optional[str] = None

# ====================================================================
# HELPERS
# ====================================================================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> str:
    """Verifiziere Bearer-Token."""
    if credentials.credentials != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials

def load_agenda() -> Dict:
    """Lade Agenda aus JSON-Datei."""
    if not AGENDA_FILE.exists():
        return {"metadata": {"total_pages": 0}, "pages": []}
    return json.loads(AGENDA_FILE.read_text())

def save_agenda(data: Dict) -> None:
    """Speichere Agenda in JSON-Datei."""
    AGENDA_FILE.write_text(json.dumps(data, indent=2))

def get_page_by_id(page_id: str) -> Optional[Dict]:
    """Finde Seite nach ID."""
    agenda = load_agenda()
    for page in agenda.get("pages", []):
        if page["id"] == page_id:
            return page
    return None

# ====================================================================
# ENDPOINTS
# ====================================================================

@app.get("/health")
async def health():
    """Health-Check."""
    return {"status": "ok", "service": "agenda-api"}

@app.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """Login-Endpunkt mit Benutzername + Passwort."""
    if req.username != VALID_USERNAME or req.password != VALID_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return LoginResponse(
        token=VALID_TOKEN,
        message=f"Willkommen {req.username}! Token ist 30 Minuten gültig."
    )

@app.get("/agenda/pages", response_model=List[PageEntry])
async def list_pages(token: str = Depends(verify_token)):
    """Alle 16 Agenda-Seiten abrufen."""
    agenda = load_agenda()
    return agenda.get("pages", [])

@app.get("/agenda/pages/{page_id}", response_model=PageEntry)
async def get_page(page_id: str, token: str = Depends(verify_token)):
    """Einzelne Agenda-Seite abrufen."""
    page = get_page_by_id(page_id)
    if not page:
        raise HTTPException(status_code=404, detail=f"Page {page_id} not found")
    return page

@app.post("/agenda/pages/{page_id}", response_model=PageEntry)
async def update_page(
    page_id: str,
    update: PageUpdate,
    token: str = Depends(verify_token)
):
    """Agenda-Seite aktualisieren."""
    agenda = load_agenda()
    
    # Finde Seite
    page_index = None
    for i, page in enumerate(agenda.get("pages", [])):
        if page["id"] == page_id:
            page_index = i
            break
    
    if page_index is None:
        raise HTTPException(status_code=404, detail=f"Page {page_id} not found")
    
    # Update-Felder
    page = agenda["pages"][page_index]
    if update.title:
        page["title"] = update.title
    if update.bromt:
        page["bromt"] = update.bromt
    if update.status:
        page["status"] = update.status
    if update.api_endpoint:
        page["api_endpoint"] = update.api_endpoint
    
    # Update Timestamp und History
    page["last_updated"] = datetime.utcnow().isoformat() + "Z"
    page["history"].append({
        "ts": page["last_updated"],
        "action": "updated",
        "by": "admin"
    })
    
    # Speichern
    save_agenda(agenda)
    
    return page

@app.delete("/agenda/pages/{page_id}")
async def delete_page(page_id: str, token: str = Depends(verify_token)):
    """Agenda-Seite löschen."""
    agenda = load_agenda()
    
    # Finde und lösche Seite
    for i, page in enumerate(agenda.get("pages", [])):
        if page["id"] == page_id:
            deleted_page = agenda["pages"].pop(i)
            save_agenda(agenda)
            return {"message": f"Page {page_id} deleted", "deleted": deleted_page}
    
    raise HTTPException(status_code=404, detail=f"Page {page_id} not found")

@app.get("/agenda/api-registry")
async def api_registry(token: str = Depends(verify_token)):
    """Rückgabe aller 20 Service-Endpunkte für OpenWebUI-Integration."""
    services = {
        "portier": 12344,
        "archivator": 12345,
        "telegram": 12346,
        "inference": 12348,
        "browser": 12349,
        "vscode": 12350,
        "email": 12351,
        "whatsapp": 12352,
        "phone": 12353,
        "calendar": 12354,
        "social_media": 12355,
        "shop": 12356,
        "html_creator": 12357,
        "homepage_creator": 12358,
        "stocks_crypto": 12359,
        "influencer": 12360,
        "unlock_master": 12361,
        "local_archiv": 12362,
        "custom_1": 12363,
        "custom_2": 12364,
    }
    
    return {
        "total_services": len(services),
        "services": [
            {
                "name": name,
                "port": port,
                "endpoint": f"http://127.0.0.1:{port}/health",
                "type": "Tool Server"
            }
            for name, port in services.items()
        ]
    }

@app.get("/agenda/stats")
async def agenda_stats(token: str = Depends(verify_token)):
    """Agenda-Statistiken."""
    agenda = load_agenda()
    pages = agenda.get("pages", [])
    
    active = sum(1 for p in pages if p["status"] == "active")
    planned = sum(1 for p in pages if p["status"] == "planned")
    
    return {
        "total_pages": len(pages),
        "active": active,
        "planned": planned,
        "last_updated": agenda.get("metadata", {}).get("last_updated")
    }

# ====================================================================
# ENTRY POINT
# ====================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "agenda_api:app",
        host="127.0.0.1",
        port=12399,
        reload=False,
        access_log=False,
    )
