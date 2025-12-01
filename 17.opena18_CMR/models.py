#!/usr/bin/env python3
"""
opena18 - CRM Agent
Models Module - PORTIER 3.0 Compliant

Pydantic Models mit extra="forbid" (Strict JSON Schema)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, EmailStr


# ================== ENUMS ==================

class DealStage(str, Enum):
    """Deal Pipeline Stages"""
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ActivityType(str, Enum):
    """Aktivitätstypen"""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"
    FOLLOW_UP = "follow_up"


class OrganizationSize(str, Enum):
    """Organisationsgrößen"""
    SMALL = "small"          # 1-50
    MEDIUM = "medium"        # 51-250
    LARGE = "large"          # 251-1000
    ENTERPRISE = "enterprise"  # 1000+


class ContactStatus(str, Enum):
    """Kontaktstatus"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    CHURNED = "churned"


class Priority(str, Enum):
    """Prioritätsstufen"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# ================== CONTACT MODELS ==================

class ContactCreate(BaseModel):
    """Request: Kontakt erstellen"""
    model_config = ConfigDict(extra="forbid")
    
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    mobile: Optional[str] = Field(default=None, max_length=30)
    organization_id: Optional[str] = Field(default=None)
    position: Optional[str] = Field(default=None, max_length=100)
    department: Optional[str] = Field(default=None, max_length=100)
    status: ContactStatus = Field(default=ContactStatus.PROSPECT)
    tags: List[str] = Field(default_factory=list, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=5000)
    gdpr_consent: bool = Field(default=False)
    marketing_consent: bool = Field(default=False)


class ContactUpdate(BaseModel):
    """Request: Kontakt aktualisieren"""
    model_config = ConfigDict(extra="forbid")
    
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(default=None)
    phone: Optional[str] = Field(default=None, max_length=30)
    mobile: Optional[str] = Field(default=None, max_length=30)
    organization_id: Optional[str] = Field(default=None)
    position: Optional[str] = Field(default=None, max_length=100)
    department: Optional[str] = Field(default=None, max_length=100)
    status: Optional[ContactStatus] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=5000)


class Contact(BaseModel):
    """Contact Entity"""
    model_config = ConfigDict(extra="forbid")
    
    contact_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    mobile: Optional[str] = None
    organization_id: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    status: str
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    gdpr_consent: bool = False
    marketing_consent: bool = False
    created_at: str
    updated_at: str


# ================== ORGANIZATION MODELS ==================

class OrganizationCreate(BaseModel):
    """Request: Organisation erstellen"""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., min_length=1, max_length=200)
    industry: Optional[str] = Field(default=None, max_length=100)
    size: OrganizationSize = Field(default=OrganizationSize.SMALL)
    website: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    phone: Optional[str] = Field(default=None, max_length=30)
    annual_revenue: Optional[float] = Field(default=None, ge=0)
    employees_count: Optional[int] = Field(default=None, ge=0)
    tags: List[str] = Field(default_factory=list, max_length=20)


class OrganizationUpdate(BaseModel):
    """Request: Organisation aktualisieren"""
    model_config = ConfigDict(extra="forbid")
    
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    industry: Optional[str] = Field(default=None, max_length=100)
    size: Optional[OrganizationSize] = Field(default=None)
    website: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    phone: Optional[str] = Field(default=None, max_length=30)
    annual_revenue: Optional[float] = Field(default=None, ge=0)
    employees_count: Optional[int] = Field(default=None, ge=0)
    tags: Optional[List[str]] = Field(default=None, max_length=20)


class Organization(BaseModel):
    """Organization Entity"""
    model_config = ConfigDict(extra="forbid")
    
    organization_id: str
    name: str
    industry: Optional[str] = None
    size: str
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    annual_revenue: Optional[float] = None
    employees_count: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    contacts_count: int = 0
    deals_count: int = 0
    created_at: str
    updated_at: str


# ================== DEAL MODELS ==================

class DealCreate(BaseModel):
    """Request: Deal erstellen"""
    model_config = ConfigDict(extra="forbid")
    
    title: str = Field(..., min_length=1, max_length=200)
    value: float = Field(..., ge=0, le=1000000000)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    stage: DealStage = Field(default=DealStage.LEAD)
    contact_id: Optional[str] = Field(default=None)
    organization_id: Optional[str] = Field(default=None)
    close_date: Optional[str] = Field(default=None)
    probability: int = Field(default=0, ge=0, le=100)
    priority: Priority = Field(default=Priority.MEDIUM)
    source: Optional[str] = Field(default=None, max_length=100)
    tags: List[str] = Field(default_factory=list, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=5000)


class DealUpdate(BaseModel):
    """Request: Deal aktualisieren"""
    model_config = ConfigDict(extra="forbid")
    
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    value: Optional[float] = Field(default=None, ge=0, le=1000000000)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    stage: Optional[DealStage] = Field(default=None)
    contact_id: Optional[str] = Field(default=None)
    organization_id: Optional[str] = Field(default=None)
    close_date: Optional[str] = Field(default=None)
    probability: Optional[int] = Field(default=None, ge=0, le=100)
    priority: Optional[Priority] = Field(default=None)
    source: Optional[str] = Field(default=None, max_length=100)
    tags: Optional[List[str]] = Field(default=None, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=5000)


class Deal(BaseModel):
    """Deal Entity"""
    model_config = ConfigDict(extra="forbid")
    
    deal_id: str
    title: str
    value: float
    currency: str
    stage: str
    contact_id: Optional[str] = None
    organization_id: Optional[str] = None
    close_date: Optional[str] = None
    probability: int
    priority: str
    source: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    weighted_value: float = 0.0
    created_at: str
    updated_at: str


# ================== ACTIVITY MODELS ==================

class ActivityCreate(BaseModel):
    """Request: Aktivität erstellen"""
    model_config = ConfigDict(extra="forbid")
    
    activity_type: ActivityType
    subject: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    contact_id: Optional[str] = Field(default=None)
    organization_id: Optional[str] = Field(default=None)
    deal_id: Optional[str] = Field(default=None)
    scheduled_at: Optional[str] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None, ge=0, le=1440)
    completed: bool = Field(default=False)


class Activity(BaseModel):
    """Activity Entity"""
    model_config = ConfigDict(extra="forbid")
    
    activity_id: str
    activity_type: str
    subject: str
    description: Optional[str] = None
    contact_id: Optional[str] = None
    organization_id: Optional[str] = None
    deal_id: Optional[str] = None
    scheduled_at: Optional[str] = None
    duration_minutes: Optional[int] = None
    completed: bool
    timestamp: str


# ================== SEARCH & COMMAND MODELS ==================

class SearchRequest(BaseModel):
    """Request: Suche"""
    model_config = ConfigDict(extra="forbid")
    
    query: str = Field(..., min_length=1, max_length=200)
    entity_types: List[str] = Field(default=["contacts", "organizations", "deals"])
    max_results: int = Field(default=50, ge=1, le=500)
    include_archived: bool = Field(default=False)


class CommandRequest(BaseModel):
    """Option-2-Flow Command"""
    model_config = ConfigDict(extra="forbid")
    
    action: str = Field(..., min_length=1, max_length=100)
    params: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = Field(default=None)


# ================== RESPONSE MODELS ==================

class HealthResponse(BaseModel):
    """Health-Check Response"""
    model_config = ConfigDict(extra="forbid")
    
    status: str
    service: str
    kuerzel: str
    port: int
    uptime_seconds: float
    version: str
    total_contacts: int
    total_organizations: int
    total_deals: int
    total_activities: int
    gdpr_compliance: bool = True
    strict: bool = True


class PipelineStats(BaseModel):
    """Pipeline Statistiken"""
    model_config = ConfigDict(extra="forbid")
    
    total_deals: int
    total_value: float
    weighted_value: float
    by_stage: Dict[str, int]
    average_deal_size: float
    win_rate: float


class CommandResponse(BaseModel):
    """Command Response für Option-2-Flow"""
    model_config = ConfigDict(extra="forbid")
    
    status: str
    action: str
    result: Any
    request_id: Optional[str] = None
    timestamp: str
