from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from openai import OpenAI
import os

# Konfiguration
MODEL_DEFAULT = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
SYSTEM_PROMPT = (
    "You are a precise senior code generator. "
    "Return production-quality code without placeholders or TODOs. "
    "Honor explicit requirements and project constraints."
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(
    title="Portier Code Generator",
    description="Erzeugt produktionsreifen Code über OpenAI-API (ohne Unllama).",
    version="1.0.0",
)

class GenReq(BaseModel):
    language: str = Field(..., description="Zielsprache, z.B. 'python', 'typescript', 'bash'")
    task: str = Field(..., description="Klare Aufgabenbeschreibung: Input/Output, Nebenbedingungen")
    files: Optional[List[str]] = Field(default=None, description="Optionale Dateinamen, wenn mehrere Artefakte gewünscht sind")
    style_notes: Optional[str] = Field(default=None, description="Optionale Stilvorgaben (Architektur, Patterns, Format)")
    constraints: Optional[str] = Field(default=None, description="Harte Constraints (Ports, Pfade, Abhängigkeiten)")
    unit_tests: bool = Field(default=False, description="Falls True, Unit-Tests zusätzlich generieren")

class GenResp(BaseModel):
    code: str
    notes: Optional[str] = None
    model: str = MODEL_DEFAULT

@app.post("/generate", response_model=GenResp)
def generate(req: GenReq):
    # Prompt bauen
    user_prompt = f"""Erzeuge {req.language}-Code für folgende Aufgabe.

AUFGABE:
{req.task}

{"DATEIEN:\n" + ", ".join(req.files) if req.files else ""}
{"STIL:\n" + req.style_notes if req.style_notes else ""}
{"CONSTRAINTS:\n" + req.constraints if req.constraints else ""}

ANFORDERUNGEN:
- Keine Platzhalter/Kein TODO.
- Produktionsreif und lauffähig.
- Behalte Pfade/Ports exakt ein.
- Erkläre nur kurz, falls zwingend nötig.
{"- Zusätzlich Unit-Tests erstellen." if req.unit_tests else ""}
"""

    try:
        chat = client.chat.completions.create(
            model=MODEL_DEFAULT,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI-Fehler: {e}") from e

    content = chat.choices[0].message.content if chat.choices else ""
    if not content:
        raise HTTPException(status_code=502, detail="Leere Antwort vom Modell")

    # Schlankes Protokoll
    return GenResp(code=content, notes="Generiert über OpenAI Chat Completions API", model=MODEL_DEFAULT)

@app.get("/health")
def health():
    return {"service": "portier-codegen", "status": "ok"}

