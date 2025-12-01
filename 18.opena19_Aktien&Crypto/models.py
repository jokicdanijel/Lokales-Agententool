#!/usr/bin/env python3
"""
opena19 - Stocks & Crypto Agent
Models Module - PORTIER 3.0 Compliant

Pydantic Models mit extra="forbid" (Strict JSON Schema)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ================== ENUMS ==================

class MarketType(str, Enum):
    """Markttyp"""
    STOCK = "stock"
    CRYPTO = "crypto"


class AlertCondition(str, Enum):
    """Alert-Bedingungen"""
    ABOVE = "above"
    BELOW = "below"
    CHANGE_PERCENT = "change_percent"


class Interval(str, Enum):
    """Daten-Intervalle"""
    MINUTELY = "1min"
    FIVE_MIN = "5min"
    FIFTEEN_MIN = "15min"
    HOURLY = "1h"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class OrderType(str, Enum):
    """Order-Typen"""
    BUY = "buy"
    SELL = "sell"


class PositionStatus(str, Enum):
    """Position Status"""
    OPEN = "open"
    CLOSED = "closed"


# ================== REQUEST MODELS ==================

class PriceRequest(BaseModel):
    """Request für aktuelle Preise"""
    model_config = ConfigDict(extra="forbid")
    
    symbols: List[str] = Field(..., min_length=1, max_length=20)
    market: MarketType = Field(...)


class HistoryRequest(BaseModel):
    """Request für historische Daten"""
    model_config = ConfigDict(extra="forbid")
    
    symbol: str = Field(..., min_length=1, max_length=20)
    market: MarketType = Field(...)
    from_date: Optional[str] = Field(None)
    to_date: Optional[str] = Field(None)
    interval: Interval = Field(default=Interval.DAILY)


class PositionCreate(BaseModel):
    """Portfolio Position erstellen"""
    model_config = ConfigDict(extra="forbid")
    
    symbol: str = Field(..., min_length=1, max_length=20)
    market: MarketType = Field(...)
    quantity: float = Field(..., gt=0)
    avg_price: float = Field(..., gt=0)
    notes: Optional[str] = Field(default=None, max_length=500)


class PositionUpdate(BaseModel):
    """Portfolio Position aktualisieren"""
    model_config = ConfigDict(extra="forbid")
    
    quantity: Optional[float] = Field(default=None, gt=0)
    avg_price: Optional[float] = Field(default=None, gt=0)
    notes: Optional[str] = Field(default=None, max_length=500)


class AlertCreate(BaseModel):
    """Alert erstellen"""
    model_config = ConfigDict(extra="forbid")
    
    symbol: str = Field(..., min_length=1, max_length=20)
    market: MarketType = Field(...)
    condition: AlertCondition = Field(...)
    threshold: float = Field(..., gt=0)
    notification: str = Field(default="dashboard")
    note: Optional[str] = Field(default=None, max_length=200)


class WatchlistAdd(BaseModel):
    """Symbol zur Watchlist hinzufügen"""
    model_config = ConfigDict(extra="forbid")
    
    symbol: str = Field(..., min_length=1, max_length=20)
    market: MarketType = Field(...)
    notes: Optional[str] = Field(default=None, max_length=200)


class CommandRequest(BaseModel):
    """Option-2-Flow Command"""
    model_config = ConfigDict(extra="forbid")
    
    action: str = Field(...)
    params: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = Field(default=None)


# ================== DATA MODELS ==================

class Position(BaseModel):
    """Portfolio Position"""
    model_config = ConfigDict(extra="forbid")
    
    position_id: str
    symbol: str
    market: MarketType
    quantity: float
    avg_price: float
    current_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    value: Optional[float] = None
    status: PositionStatus = PositionStatus.OPEN
    notes: Optional[str] = None
    created_at: str
    updated_at: str


class Alert(BaseModel):
    """Preis-Alert"""
    model_config = ConfigDict(extra="forbid")
    
    alert_id: str
    symbol: str
    market: MarketType
    condition: AlertCondition
    threshold: float
    notification: str
    note: Optional[str] = None
    triggered: bool = False
    triggered_at: Optional[str] = None
    created_at: str


class WatchlistItem(BaseModel):
    """Watchlist Item"""
    model_config = ConfigDict(extra="forbid")
    
    symbol: str
    market: MarketType
    current_price: Optional[float] = None
    change_24h: Optional[float] = None
    change_percent_24h: Optional[float] = None
    notes: Optional[str] = None
    added_at: str


class PriceData(BaseModel):
    """Preisdaten"""
    model_config = ConfigDict(extra="forbid")
    
    symbol: str
    market: str
    price: float
    change_24h: Optional[float] = None
    change_percent_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    timestamp: str


class OHLCVData(BaseModel):
    """OHLCV Daten (Open, High, Low, Close, Volume)"""
    model_config = ConfigDict(extra="forbid")
    
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


# ================== RESPONSE MODELS ==================

class Portfolio(BaseModel):
    """Portfolio Übersicht"""
    model_config = ConfigDict(extra="forbid")
    
    positions: List[Position]
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_percent: float
    positions_count: int
    last_updated: str


class HealthResponse(BaseModel):
    """Health-Check Response"""
    model_config = ConfigDict(extra="forbid")
    
    status: str
    service: str
    kuerzel: str
    port: int
    uptime_seconds: float
    version: str
    total_positions: int
    total_alerts: int
    active_alerts: int
    watchlist_count: int
    cache_status: str
    strict: bool = True


class PriceResponse(BaseModel):
    """Preis-Response"""
    model_config = ConfigDict(extra="forbid")
    
    market: str
    prices: Dict[str, Optional[float]]
    timestamp: str


class HistoryResponse(BaseModel):
    """Historische Daten Response"""
    model_config = ConfigDict(extra="forbid")
    
    symbol: str
    market: str
    interval: str
    data: List[OHLCVData]
    from_date: str
    to_date: str


class CommandResponse(BaseModel):
    """Command Response für Option-2-Flow"""
    model_config = ConfigDict(extra="forbid")
    
    success: bool
    action: str
    result: Any
    request_id: Optional[str] = None
    timestamp: str


class MarketStats(BaseModel):
    """Markt-Statistiken"""
    model_config = ConfigDict(extra="forbid")
    
    market: str
    total_symbols_tracked: int
    last_update: str
    api_calls_today: int
    cache_hit_rate: float
