# Option-2-Flow - Processed Core Version

## 1. Heilige Regel
Der gesamte Stack folgt EINEM einzigen erlaubten Pfad.

## 2. Hinweg (Command-Flow)

### Sequenz
```
OpenAI → opena1 → opena2 → kordp → Tool
```

### Details
1. **OpenAI** sendet Request
2. **opena1** empfaengt, validiert (7.1)
3. **opena1** waehlt Tool
4. **opena1** baut CMD-Envelope
5. **opena2** erzeugt Safepoint CMD
6. **opena2** leitet an kordp weiter
7. **kordp** dispatcht an Tool
8. **Tool** fuehrt Business Logic aus

## 3. Rueckweg (Response-Flow)

### Sequenz
```
Tool → kordp → opena2 → opena1 → OpenAI
```

### Details
1. **Tool** erzeugt Response
2. **kordp** sammelt Response
3. **kordp** leitet an opena2 zurueck
4. **opena2** erzeugt Safepoint RESP
5. **opena2** leitet an opena1 zurueck
6. **opena1** baut 7.2-Response
7. **opena1** sendet an OpenAI

## 4. Verboten

### Direktcalls
- OpenAI → Tool (VERBOTEN)
- OpenAI → kordp (VERBOTEN)
- OpenAI → opena2 (VERBOTEN)

### Shortcuts
- opena1 → kordp (VERBOTEN, opena2 muss zwischen)
- opena1 → Tool (VERBOTEN)
- Tool → opena1 (VERBOTEN, opena2 muss zwischen)

### Backdoors
- Jegliche Umgehung (VERBOTEN)
- Developer-Overrides (VERBOTEN ohne explizite Freigabe)
- Test-Bypasses (VERBOTEN im Production-Code)

### Tool-zu-Tool
- Direkte Tool-Kommunikation (VERBOTEN)
- Immer ueber Koordinator

## 5. Ablaufregeln

### Regel 1: opena1 ist Eingang
- Alle OpenAI-Requests gehen an opena1
- Keine Alternative-Eingang erlaubt

### Regel 2: opena2 ist immer dabei
- Jeder Command durchlaeuft opena2
- Jede Response durchlaeuft opena2
- Safepoints sind Pflicht

### Regel 3: kordp dispatcht
- Nur kordp fuehrt Tools aus
- Keine direkte Tool-Invocation

### Regel 4: Tool ist Endpunkt
- Tool ist letzter Schritt im Hinweg
- Tool startet Rueckweg

### Regel 5: Rueckweg spiegelbildlich
- Gleicher Pfad zurueck
- Keine Abkuerzungen

## 6. Enforcement

### Code-Ebene
```python
# In opena1
if request.source != "openai":
    raise Forbidden("Only OpenAI allowed")

# In opena2
if request.source not in ["opena1", "kordp"]:
    raise Forbidden("Invalid source")

# In kordp
if request.source != "opena2":
    raise Forbidden("Only opena2 allowed")
```

### Middleware
- Port-Policy-Middleware prueft Quelle
- Routing-Middleware erzwingt Pfad
- Security-Middleware validiert Token

### Testing
- Integration-Tests pruefen kompletten Flow
- Unit-Tests pruefen einzelne Hops
- E2E-Tests validieren OpenAI → Tool → OpenAI

## 7. Audit-Trail
- Jeder Hop erzeugt Safepoint
- Vollstaendige Nachvollziehbarkeit
- Append-Only Logging
- Index fuer Recherche
