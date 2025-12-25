"""
ELION opena_finance – Finance Agent (Port 12347)
FastAPI-basierter Service für Finanz-Datenbank-Queries & Storage.

Architektur:
- SQLite DB: finance.db (local, append-only)
- Tabellen: accounts, transactions, statements
- Archiv: Alle Queries & Writes zu opena2 (Archivator)
- Port: 12347
- Auth: Bearer Token via .env
"""

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# ===== CONFIG =====
PORT = 12347
DB_PATH = Path("finance.db")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
ARCHIV_ENDPOINT = "http://127.0.0.1:12345/store/archivp"
ENV_FILE = Path(".env")

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "opena_finance.log"), logging.StreamHandler()],
)
logger = logging.getLogger("opena_finance")

# ===== APP =====
app = FastAPI(
    title="ELION Finance Agent (opena_finance)",
    version="1.0",
    description="Finance DB Agent mit SQLite + Archiv-Integration",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


# ===== TOKEN & AUTH =====
def _read_token() -> str:
    """Lese Token aus .env (gegenüber von opena19)"""
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text().strip().split("\n")
        for line in lines:
            if line.startswith("DASHBOARD_ADMIN_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("DASHBOARD_ADMIN_TOKEN nicht in .env gefunden!")


_TOKEN = _read_token()


def verify_token(credentials: HTTPAuthorizationCredentials) -> bool:
    """Validiere Bearer Token"""
    return credentials.credentials == _TOKEN


# ===== DATABASE INITIALIZATION =====
def init_db() -> None:
    """Erstelle SQLite DB mit Tabellen (idempotent)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabelle: Accounts (Konten)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            account_type TEXT NOT NULL,  -- 'savings', 'checking', 'investment', 'crypto'
            balance REAL DEFAULT 0.0,
            currency TEXT DEFAULT 'EUR',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """
    )

    # Tabelle: Transactions (Transaktionen)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category TEXT,  -- 'income', 'expense', 'transfer'
            transaction_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        )
    """
    )

    # Tabelle: Statements (Kontoauszüge)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS statements (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            opening_balance REAL NOT NULL,
            closing_balance REAL NOT NULL,
            transaction_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        )
    """
    )

    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")


init_db()


# ===== HELPER FUNCTIONS =====
async def _archive_write(payload: dict[str, Any]) -> bool:
    """Schreibe Daten zu opena2 (Archivator)"""
    import urllib.request

    try:
        data = {"src": "opena_finance", "dst": "opena2", "kind": "TRANSACTION", "payload": payload}
        req = urllib.request.Request(
            ARCHIV_ENDPOINT,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            result = json.loads(r.read().decode())
            logger.info(f"Archiv write OK: {result.get('written')}")
            return result.get("written", False)
    except Exception as e:
        logger.error(f"Archiv write failed: {e}")
        return False


def _get_now() -> str:
    """ISO 8601 Timestamp"""
    return datetime.utcnow().isoformat() + "Z"


def _gen_id() -> str:
    """Generiere eindeutige ID"""
    return str(uuid.uuid4())


# ===== ENDPOINTS =====


@app.get("/health")
async def health():
    """Health Check"""
    return {"status": "healthy", "service": "opena_finance", "port": PORT, "db": str(DB_PATH), "timestamp": _get_now()}


@app.post("/account/create")
async def create_account(
    credentials: HTTPAuthorizationCredentials = Security(security),
    name: str = None,
    account_type: str = "checking",
    initial_balance: float = 0.0,
    currency: str = "EUR",
) -> dict[str, Any]:
    """Neues Konto erstellen"""
    if not verify_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid token")

    if not name:
        raise HTTPException(status_code=400, detail="name required")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        account_id = _gen_id()
        now = _get_now()

        c.execute(
            """INSERT INTO accounts (id, name, account_type, balance, currency, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (account_id, name, account_type, initial_balance, currency, now, now),
        )
        conn.commit()
        conn.close()

        logger.info(f"Account created: {account_id} ({name})")

        # Archive
        await _archive_write(
            {
                "action": "account_created",
                "account_id": account_id,
                "name": name,
                "type": account_type,
                "initial_balance": initial_balance,
                "strict": True,
            }
        )

        return {
            "id": account_id,
            "name": name,
            "type": account_type,
            "balance": initial_balance,
            "currency": currency,
            "created_at": now,
        }
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Account name duplicate: {e!s}")
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts")
async def list_accounts(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Liste alle Konten"""
    if not verify_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, name, account_type, balance, currency, created_at FROM accounts")
        rows = c.fetchall()
        conn.close()

        accounts = [
            {"id": row[0], "name": row[1], "type": row[2], "balance": row[3], "currency": row[4], "created_at": row[5]}
            for row in rows
        ]

        logger.info(f"Listed {len(accounts)} accounts")
        return {"count": len(accounts), "accounts": accounts}

    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transaction/add")
async def add_transaction(
    credentials: HTTPAuthorizationCredentials = Security(security),
    account_id: str = None,
    amount: float = None,
    description: str = None,
    category: str = "expense",
) -> dict[str, Any]:
    """Neue Transaktion hinzufügen"""
    if not verify_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid token")

    if not all([account_id, amount, description]):
        raise HTTPException(status_code=400, detail="account_id, amount, description required")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Überprüfe ob Konto existiert
        c.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        result = c.fetchone()
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Account {account_id} not found")

        old_balance = result[0]
        new_balance = old_balance + amount

        # Schreibe Transaktion
        tx_id = _gen_id()
        now = _get_now()
        c.execute(
            """INSERT INTO transactions (id, account_id, amount, description, category, transaction_date, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (tx_id, account_id, amount, description, category, now, now),
        )

        # Update account balance
        c.execute("UPDATE accounts SET balance = ?, updated_at = ? WHERE id = ?", (new_balance, now, account_id))

        conn.commit()
        conn.close()

        logger.info(f"Transaction added: {tx_id} (${amount}) to {account_id}")

        # Archive
        await _archive_write(
            {
                "action": "transaction_added",
                "tx_id": tx_id,
                "account_id": account_id,
                "amount": amount,
                "description": description,
                "category": category,
                "old_balance": old_balance,
                "new_balance": new_balance,
                "strict": True,
            }
        )

        return {
            "id": tx_id,
            "account_id": account_id,
            "amount": amount,
            "description": description,
            "category": category,
            "old_balance": old_balance,
            "new_balance": new_balance,
            "timestamp": now,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transactions")
async def list_transactions(
    credentials: HTTPAuthorizationCredentials = Security(security), account_id: str = None
) -> dict[str, Any]:
    """Liste Transaktionen (optional filtert nach account_id)"""
    if not verify_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        if account_id:
            c.execute(
                """SELECT id, account_id, amount, description, category, transaction_date, created_at
                   FROM transactions WHERE account_id = ? ORDER BY transaction_date DESC""",
                (account_id,),
            )
        else:
            c.execute(
                """SELECT id, account_id, amount, description, category, transaction_date, created_at
                   FROM transactions ORDER BY transaction_date DESC"""
            )

        rows = c.fetchall()
        conn.close()

        transactions = [
            {
                "id": row[0],
                "account_id": row[1],
                "amount": row[2],
                "description": row[3],
                "category": row[4],
                "date": row[5],
                "created_at": row[6],
            }
            for row in rows
        ]

        logger.info(f"Listed {len(transactions)} transactions")
        return {"count": len(transactions), "transactions": transactions}

    except Exception as e:
        logger.error(f"Error listing transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/statement/generate")
async def generate_statement(
    credentials: HTTPAuthorizationCredentials = Security(security), account_id: str = None, period_days: int = 30
) -> dict[str, Any]:
    """Generiere Kontoauszug für Account (letzte N Tage)"""
    if not verify_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid token")

    if not account_id:
        raise HTTPException(status_code=400, detail="account_id required")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Überprüfe Konto
        c.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        result = c.fetchone()
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Account {account_id} not found")

        closing_balance = result[0]

        # Calculate period
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)

        # Sum transactions in period
        c.execute(
            """SELECT COUNT(*), SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END),
                      SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END)
               FROM transactions
               WHERE account_id = ? AND transaction_date >= ? AND transaction_date <= ?""",
            (account_id, period_start.isoformat() + "Z", period_end.isoformat() + "Z"),
        )
        tx_count, deposits, withdrawals = c.fetchone()
        deposits = deposits or 0.0
        withdrawals = withdrawals or 0.0

        # Calculated opening balance
        opening_balance = closing_balance - (deposits - withdrawals)

        # Create statement
        stmt_id = _gen_id()
        now = _get_now()

        c.execute(
            """INSERT INTO statements (id, account_id, period_start, period_end, opening_balance, closing_balance, transaction_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                stmt_id,
                account_id,
                period_start.isoformat() + "Z",
                period_end.isoformat() + "Z",
                opening_balance,
                closing_balance,
                tx_count or 0,
                now,
            ),
        )

        conn.commit()
        conn.close()

        logger.info(f"Statement generated: {stmt_id} for {account_id}")

        # Archive
        await _archive_write(
            {
                "action": "statement_generated",
                "stmt_id": stmt_id,
                "account_id": account_id,
                "period_start": period_start.isoformat() + "Z",
                "period_end": period_end.isoformat() + "Z",
                "opening_balance": opening_balance,
                "closing_balance": closing_balance,
                "deposits": deposits,
                "withdrawals": withdrawals,
                "transaction_count": tx_count or 0,
                "strict": True,
            }
        )

        return {
            "id": stmt_id,
            "account_id": account_id,
            "period_start": period_start.isoformat() + "Z",
            "period_end": period_end.isoformat() + "Z",
            "opening_balance": opening_balance,
            "closing_balance": closing_balance,
            "deposits": deposits,
            "withdrawals": withdrawals,
            "transaction_count": tx_count or 0,
            "created_at": now,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating statement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statement/{stmt_id}")
async def get_statement(stmt_id: str, credentials: HTTPAuthorizationCredentials = Security(security)) -> dict[str, Any]:
    """Hole Kontoauszug nach ID"""
    if not verify_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """SELECT id, account_id, period_start, period_end, opening_balance, closing_balance, transaction_count, created_at
               FROM statements WHERE id = ?""",
            (stmt_id,),
        )
        row = c.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail=f"Statement {stmt_id} not found")

        return {
            "id": row[0],
            "account_id": row[1],
            "period_start": row[2],
            "period_end": row[3],
            "opening_balance": row[4],
            "closing_balance": row[5],
            "transaction_count": row[6],
            "created_at": row[7],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching statement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard")
async def dashboard_summary(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict[str, Any]:
    """Dashboard-Zusammenfassung (alle Konten, Totals)"""
    if not verify_token(credentials):
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Accounts
        c.execute("SELECT COUNT(*), SUM(balance) FROM accounts")
        account_count, total_balance = c.fetchone()
        account_count = account_count or 0
        total_balance = total_balance or 0.0

        # Transactions (letzte 7 Tage)
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
        c.execute("SELECT COUNT(*), SUM(amount) FROM transactions WHERE transaction_date >= ?", (week_ago,))
        recent_tx_count, recent_tx_sum = c.fetchone()
        recent_tx_count = recent_tx_count or 0
        recent_tx_sum = recent_tx_sum or 0.0

        # Statements
        c.execute("SELECT COUNT(*) FROM statements")
        stmt_count = c.fetchone()[0] or 0

        conn.close()

        return {
            "timestamp": _get_now(),
            "accounts": {"count": account_count, "total_balance": total_balance},
            "transactions": {"count": recent_tx_count, "sum_week": recent_tx_sum},
            "statements": {"count": stmt_count},
        }

    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== MAIN =====
if __name__ == "__main__":
    logger.info(f"🚀 Starting opena_finance on port {PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
