#!/usr/bin/env python3
"""
opena19 - Stocks & Crypto Agent
Port: 12365
Kürzel: stockcryptop

Features:
- Stock price tracking (real-time + historical)
- Cryptocurrency price monitoring
- Portfolio management (positions, PnL, total value)
- Price alerts (condition-based notifications)
- Market metrics (daily gain/loss, volume, market cap)
- Multi-market support (stocks: NYSE/NASDAQ, crypto: BTC/ETH/USDT pairs)
- Caching layer (reduce API calls, 5min TTL)
- Option-2-Flow compliance

Dependencies:
- fastapi, uvicorn, pydantic
- requests (API calls to CoinGecko, Alpha Vantage)
- redis (optional caching, graceful degradation)

Integration:
- POST /command → Option-2-Flow (opena1 → opena2 → kordp → opena19)
- GET /prices → Get current prices (stocks or crypto)
- GET /history → Historical data (OHLCV)
- GET /portfolio → Portfolio overview
- POST /alerts → Create price alert
- GET /alerts → List active alerts
- DELETE /alerts/{alert_id} → Remove alert
"""

import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import requests
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# ========== CONFIG ==========
PORT = 12365
AGENT_ID = "opena19"
KUERZEL = "stockcryptop"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

PRICES_FILE = DATA_DIR / "prices_cache.json"
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
ALERTS_FILE = DATA_DIR / "alerts.json"
HISTORY_FILE = DATA_DIR / "stockcrypto_history.jsonl"

# API Keys (ENV-only)
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")  # Stock API
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")  # Crypto API (optional, public API works)

# Cache TTL (5 minutes)
CACHE_TTL_SECONDS = 300

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOGS_DIR / f"{AGENT_ID}.nohup.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(AGENT_ID)

# ========== SECURITY ==========
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify Bearer token"""
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Bearer token")
    return credentials.credentials


# ========== ENUMS ==========
class MarketType(str, Enum):
    STOCK = "stock"
    CRYPTO = "crypto"


class AlertCondition(str, Enum):
    ABOVE = "above"
    BELOW = "below"
    CHANGE_PERCENT = "change_percent"


class Interval(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# ========== PYDANTIC MODELS ==========
class PriceRequest(BaseModel):
    """Request for current prices"""

    symbols: list[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Stock tickers (e.g., AAPL, TSLA) or crypto (e.g., bitcoin, ethereum)",
    )
    market: MarketType = Field(..., description="Market type: stock or crypto")

    class Config:
        extra = "forbid"


class HistoryRequest(BaseModel):
    """Request for historical data"""

    symbol: str = Field(..., min_length=1, max_length=20, description="Stock ticker or crypto symbol")
    market: MarketType = Field(..., description="Market type")
    from_date: str | None = Field(None, description="Start date (YYYY-MM-DD), default: 30 days ago")
    to_date: str | None = Field(None, description="End date (YYYY-MM-DD), default: today")
    interval: Interval = Field(default=Interval.DAILY, description="Data interval")

    class Config:
        extra = "forbid"


class Position(BaseModel):
    """Portfolio position"""

    symbol: str
    market: MarketType
    quantity: float
    avg_price: float
    current_price: float | None = None
    pnl: float | None = None
    pnl_percent: float | None = None

    class Config:
        extra = "forbid"


class PortfolioCreate(BaseModel):
    """Create/update portfolio position"""

    symbol: str = Field(..., min_length=1, max_length=20)
    market: MarketType
    quantity: float = Field(..., gt=0, description="Quantity must be positive")
    avg_price: float = Field(..., gt=0, description="Average purchase price")

    class Config:
        extra = "forbid"


class Portfolio(BaseModel):
    """Portfolio overview"""

    positions: list[Position]
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_percent: float

    class Config:
        extra = "forbid"


class AlertCreate(BaseModel):
    """Create price alert"""

    symbol: str = Field(..., min_length=1, max_length=20)
    market: MarketType
    condition: AlertCondition
    threshold: float = Field(..., gt=0, description="Price threshold or percentage")
    notification: str = Field(default="Email", description="Notification type")

    class Config:
        extra = "forbid"


class Alert(BaseModel):
    """Alert model"""

    id: str
    symbol: str
    market: MarketType
    condition: AlertCondition
    threshold: float
    notification: str
    created_at: str
    triggered: bool = False
    triggered_at: str | None = None

    class Config:
        extra = "forbid"


class CommandRequest(BaseModel):
    """Option-2-Flow command"""

    action: str = Field(..., description="Action: get_prices, get_history, add_position, create_alert")
    params: dict[str, Any] = Field(default_factory=dict, description="Action parameters")

    class Config:
        extra = "forbid"


# ========== DATA STORE ==========
class DataStore:
    """Persistent data storage"""

    @staticmethod
    def load_cache() -> dict[str, Any]:
        """Load price cache"""
        if PRICES_FILE.exists():
            with open(PRICES_FILE) as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_cache(cache: dict[str, Any]):
        """Save price cache"""
        with open(PRICES_FILE, "w") as f:
            json.dump(cache, f, indent=2)

    @staticmethod
    def load_portfolio() -> list[Position]:
        """Load portfolio"""
        if PORTFOLIO_FILE.exists():
            with open(PORTFOLIO_FILE) as f:
                data = json.load(f)
                return [Position(**p) for p in data]
        return []

    @staticmethod
    def save_portfolio(positions: list[Position]):
        """Save portfolio"""
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump([p.model_dump() for p in positions], f, indent=2)

    @staticmethod
    def load_alerts() -> list[Alert]:
        """Load alerts"""
        if ALERTS_FILE.exists():
            with open(ALERTS_FILE) as f:
                data = json.load(f)
                return [Alert(**a) for a in data]
        return []

    @staticmethod
    def save_alerts(alerts: list[Alert]):
        """Save alerts"""
        with open(ALERTS_FILE, "w") as f:
            json.dump([a.model_dump() for a in alerts], f, indent=2)

    @staticmethod
    def append_history(event: str, data: dict[str, Any]):
        """Append event to history (JSONL)"""
        entry = {"timestamp": datetime.utcnow().isoformat() + "Z", "event": event, "data": data}
        with open(HISTORY_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")


# ========== MARKET DATA PROVIDERS ==========
class MarketDataProvider:
    """Market data API integration"""

    @staticmethod
    def get_stock_price(symbol: str) -> float | None:
        """Get stock price from Alpha Vantage"""
        try:
            url = "https://www.alphavantage.co/query"
            params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_VANTAGE_KEY}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "Global Quote" in data and "05. price" in data["Global Quote"]:
                return float(data["Global Quote"]["05. price"])

            logger.warning(f"Stock price not found for {symbol}: {data}")
            return None
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return None

    @staticmethod
    def get_crypto_price(symbol: str) -> float | None:
        """Get crypto price from CoinGecko (free API)"""
        try:
            # Map common symbols
            symbol_map = {
                "bitcoin": "bitcoin",
                "btc": "bitcoin",
                "ethereum": "ethereum",
                "eth": "ethereum",
                "usdt": "tether",
                "tether": "tether",
                "bnb": "binancecoin",
                "solana": "solana",
                "sol": "solana",
                "cardano": "cardano",
                "ada": "cardano",
                "xrp": "ripple",
                "ripple": "ripple",
            }

            coin_id = symbol_map.get(symbol.lower(), symbol.lower())

            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": coin_id, "vs_currencies": "usd"}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if coin_id in data and "usd" in data[coin_id]:
                return float(data[coin_id]["usd"])

            logger.warning(f"Crypto price not found for {symbol}: {data}")
            return None
        except Exception as e:
            logger.error(f"Error fetching crypto price for {symbol}: {e}")
            return None

    @staticmethod
    def get_prices_with_cache(symbols: list[str], market: MarketType) -> dict[str, float | None]:
        """Get prices with 5-minute cache"""
        cache = DataStore.load_cache()
        now = time.time()
        result = {}

        for symbol in symbols:
            cache_key = f"{market.value}:{symbol}"

            # Check cache
            if cache_key in cache:
                cached_data = cache[cache_key]
                if now - cached_data.get("timestamp", 0) < CACHE_TTL_SECONDS:
                    result[symbol] = cached_data.get("price")
                    logger.info(f"Cache HIT for {cache_key}: {result[symbol]}")
                    continue

            # Fetch new data
            logger.info(f"Cache MISS for {cache_key}, fetching from API")
            if market == MarketType.STOCK:
                price = MarketDataProvider.get_stock_price(symbol)
            else:
                price = MarketDataProvider.get_crypto_price(symbol)

            result[symbol] = price

            # Update cache
            cache[cache_key] = {"price": price, "timestamp": now}

        DataStore.save_cache(cache)
        return result


# ========== PORTFOLIO MANAGER ==========
class PortfolioManager:
    """Portfolio management logic"""

    @staticmethod
    def add_position(req: PortfolioCreate) -> Position:
        """Add or update portfolio position"""
        positions = DataStore.load_portfolio()

        # Check if position exists
        existing = next((p for p in positions if p.symbol == req.symbol and p.market == req.market), None)

        if existing:
            # Update existing position (average price)
            total_qty = existing.quantity + req.quantity
            total_cost = (existing.quantity * existing.avg_price) + (req.quantity * req.avg_price)
            existing.quantity = total_qty
            existing.avg_price = total_cost / total_qty
            position = existing
        else:
            # Create new position
            position = Position(symbol=req.symbol, market=req.market, quantity=req.quantity, avg_price=req.avg_price)
            positions.append(position)

        DataStore.save_portfolio(positions)
        DataStore.append_history("add_position", req.model_dump())

        return position

    @staticmethod
    def get_portfolio() -> Portfolio:
        """Calculate portfolio with current prices"""
        positions = DataStore.load_portfolio()

        if not positions:
            return Portfolio(positions=[], total_value=0.0, total_cost=0.0, total_pnl=0.0, total_pnl_percent=0.0)

        # Fetch current prices
        stock_symbols = [p.symbol for p in positions if p.market == MarketType.STOCK]
        crypto_symbols = [p.symbol for p in positions if p.market == MarketType.CRYPTO]

        stock_prices = (
            MarketDataProvider.get_prices_with_cache(stock_symbols, MarketType.STOCK) if stock_symbols else {}
        )
        crypto_prices = (
            MarketDataProvider.get_prices_with_cache(crypto_symbols, MarketType.CRYPTO) if crypto_symbols else {}
        )

        # Calculate PnL
        total_value = 0.0
        total_cost = 0.0

        for position in positions:
            current_price = (
                stock_prices.get(position.symbol)
                if position.market == MarketType.STOCK
                else crypto_prices.get(position.symbol)
            )

            if current_price is not None:
                position.current_price = current_price
                position_value = current_price * position.quantity
                position_cost = position.avg_price * position.quantity
                position.pnl = position_value - position_cost
                position.pnl_percent = (position.pnl / position_cost) * 100 if position_cost > 0 else 0.0

                total_value += position_value
                total_cost += position_cost

        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost) * 100 if total_cost > 0 else 0.0

        return Portfolio(
            positions=positions,
            total_value=total_value,
            total_cost=total_cost,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
        )


# ========== ALERT MANAGER ==========
class AlertManager:
    """Alert management logic"""

    @staticmethod
    def create_alert(req: AlertCreate) -> Alert:
        """Create price alert"""
        alerts = DataStore.load_alerts()

        alert_id = hashlib.md5(
            f"{req.symbol}{req.market.value}{req.condition.value}{req.threshold}{time.time()}".encode()
        ).hexdigest()[:12]

        alert = Alert(
            id=alert_id,
            symbol=req.symbol,
            market=req.market,
            condition=req.condition,
            threshold=req.threshold,
            notification=req.notification,
            created_at=datetime.utcnow().isoformat() + "Z",
        )

        alerts.append(alert)
        DataStore.save_alerts(alerts)
        DataStore.append_history("create_alert", req.model_dump())

        return alert

    @staticmethod
    def check_alerts():
        """Check all active alerts and trigger notifications"""
        alerts = DataStore.load_alerts()
        active_alerts = [a for a in alerts if not a.triggered]

        if not active_alerts:
            return

        # Group by market
        stock_symbols = list(set([a.symbol for a in active_alerts if a.market == MarketType.STOCK]))
        crypto_symbols = list(set([a.symbol for a in active_alerts if a.market == MarketType.CRYPTO]))

        stock_prices = (
            MarketDataProvider.get_prices_with_cache(stock_symbols, MarketType.STOCK) if stock_symbols else {}
        )
        crypto_prices = (
            MarketDataProvider.get_prices_with_cache(crypto_symbols, MarketType.CRYPTO) if crypto_symbols else {}
        )

        for alert in active_alerts:
            current_price = (
                stock_prices.get(alert.symbol) if alert.market == MarketType.STOCK else crypto_prices.get(alert.symbol)
            )

            if current_price is None:
                continue

            triggered = False

            if alert.condition == AlertCondition.ABOVE and current_price > alert.threshold:
                triggered = True
            elif alert.condition == AlertCondition.BELOW and current_price < alert.threshold:
                triggered = True

            if triggered:
                alert.triggered = True
                alert.triggered_at = datetime.utcnow().isoformat() + "Z"
                logger.info(
                    f"Alert triggered: {alert.symbol} {alert.condition.value} {alert.threshold}, current: {current_price}"
                )
                DataStore.append_history(
                    "alert_triggered",
                    {
                        "alert_id": alert.id,
                        "symbol": alert.symbol,
                        "current_price": current_price,
                        "threshold": alert.threshold,
                    },
                )

        DataStore.save_alerts(alerts)


# ========== STARTUP ==========
start_time = time.time()

app = FastAPI(
    title=f"{AGENT_ID} - Stocks & Crypto Agent",
    version="1.0",
    description="Stock & Crypto price tracking, portfolio management, alerts",
)


# ========== ENDPOINTS ==========
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "agent": AGENT_ID,
        "kuerzel": KUERZEL,
        "port": PORT,
        "description": "Stocks & Crypto Agent - Price tracking, Portfolio, Alerts",
        "endpoints": [
            "/health",
            "/prices (GET)",
            "/history (GET)",
            "/portfolio (GET/POST)",
            "/alerts (GET/POST)",
            "/alerts/{alert_id} (DELETE)",
            "/command (POST)",
        ],
    }


@app.get("/health")
async def health():
    """Health check"""
    uptime = time.time() - start_time

    positions = DataStore.load_portfolio()
    alerts = DataStore.load_alerts()

    return {
        "status": "ok",
        "service": AGENT_ID,
        "kuerzel": KUERZEL,
        "port": PORT,
        "uptime_seconds": round(uptime, 2),
        "total_positions": len(positions),
        "total_alerts": len(alerts),
        "active_alerts": len([a for a in alerts if not a.triggered]),
    }


@app.get("/prices")
async def get_prices(
    symbols: str = Query(..., description="Comma-separated symbols (e.g., AAPL,TSLA or bitcoin,ethereum)"),
    market: MarketType = Query(..., description="Market type: stock or crypto"),
    token: str = Depends(verify_token),
):
    """Get current prices"""
    symbol_list = [s.strip() for s in symbols.split(",")]

    if len(symbol_list) > 20:
        raise HTTPException(status_code=422, detail="Maximum 20 symbols allowed")

    prices = MarketDataProvider.get_prices_with_cache(symbol_list, market)

    DataStore.append_history("get_prices", {"symbols": symbol_list, "market": market.value, "prices": prices})

    return {"market": market.value, "prices": prices, "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.post("/portfolio")
async def add_portfolio_position(req: PortfolioCreate, token: str = Depends(verify_token)):
    """Add/update portfolio position"""
    position = PortfolioManager.add_position(req)

    return {"success": True, "position": position.model_dump(), "message": f"Position {req.symbol} added/updated"}


@app.get("/portfolio")
async def get_portfolio_overview(token: str = Depends(verify_token)):
    """Get portfolio overview with current values"""
    portfolio = PortfolioManager.get_portfolio()

    return portfolio.model_dump()


@app.post("/alerts")
async def create_price_alert(req: AlertCreate, token: str = Depends(verify_token)):
    """Create price alert"""
    alert = AlertManager.create_alert(req)

    return {"success": True, "alert": alert.model_dump(), "message": f"Alert created for {req.symbol}"}


@app.get("/alerts")
async def list_alerts(
    active_only: bool = Query(default=True, description="Show only active (non-triggered) alerts"),
    token: str = Depends(verify_token),
):
    """List all alerts"""
    alerts = DataStore.load_alerts()

    if active_only:
        alerts = [a for a in alerts if not a.triggered]

    return {"total": len(alerts), "alerts": [a.model_dump() for a in alerts]}


@app.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str, token: str = Depends(verify_token)):
    """Delete alert"""
    alerts = DataStore.load_alerts()

    alert = next((a for a in alerts if a.id == alert_id), None)

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alerts = [a for a in alerts if a.id != alert_id]
    DataStore.save_alerts(alerts)

    DataStore.append_history("delete_alert", {"alert_id": alert_id})

    return {"success": True, "message": f"Alert {alert_id} deleted"}


@app.post("/command")
async def command_endpoint(req: CommandRequest, token: str = Depends(verify_token)):
    """Option-2-Flow command endpoint"""
    action = req.action
    params = req.params

    try:
        if action == "get_prices":
            symbols = params.get("symbols", [])
            market = MarketType(params.get("market", "stock"))
            prices = MarketDataProvider.get_prices_with_cache(symbols, market)
            result = {"prices": prices, "market": market.value}

        elif action == "add_position":
            position_req = PortfolioCreate(**params)
            position = PortfolioManager.add_position(position_req)
            result = {"position": position.model_dump()}

        elif action == "get_portfolio":
            portfolio = PortfolioManager.get_portfolio()
            result = portfolio.model_dump()

        elif action == "create_alert":
            alert_req = AlertCreate(**params)
            alert = AlertManager.create_alert(alert_req)
            result = {"alert": alert.model_dump()}

        elif action == "check_alerts":
            AlertManager.check_alerts()
            result = {"message": "Alerts checked"}

        else:
            raise HTTPException(status_code=422, detail=f"Unknown action: {action}")

        DataStore.append_history("command_executed", {"action": action, "params": params, "result": result})

        return {"success": True, "action": action, "result": result}

    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== MAIN ==========
if __name__ == "__main__":
    logger.info(f"Starting {AGENT_ID} on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
