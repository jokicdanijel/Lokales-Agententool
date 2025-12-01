#!/usr/bin/env python3
"""
opena18 - CRM Agent
Port: 12363
Kürzel: crmp

Customer Relationship Management System für Kontakte, Organisationen, Deals und Aktivitäten.
Unterstützt CRUD-Operationen, Suche, Relationen und Deal-Pipeline-Management.
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict, EmailStr
import uvicorn


# ================== CONFIG ==================

PORT = 12363
SERVICE_NAME = "opena18"
KUERZEL = "crmp"
VERSION = "1.0"

DATA_DIR = Path(__file__).parent / "data"
CONTACTS_FILE = DATA_DIR / "contacts.json"
ORGANIZATIONS_FILE = DATA_DIR / "organizations.json"
DEALS_FILE = DATA_DIR / "deals.json"
ACTIVITIES_FILE = DATA_DIR / "activities.json"
HISTORY_FILE = DATA_DIR / "crm_history.jsonl"

# Erstelle Verzeichnisse
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Bearer Token aus ENV
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")

# Start-Zeit für Uptime
START_TIME = datetime.now(timezone.utc)


# ================== ENUMS ==================

class DealStage(str, Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ActivityType(str, Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"


class OrganizationSize(str, Enum):
    SMALL = "small"          # 1-50
    MEDIUM = "medium"        # 51-250
    LARGE = "large"          # 251-1000
    ENTERPRISE = "enterprise"  # 1000+


# ================== DATA MODELS ==================

class ContactCreate(BaseModel):
    """Request: Kontakt erstellen"""
    model_config = ConfigDict(extra="forbid")
    
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    organization_id: Optional[str] = Field(default=None)
    position: Optional[str] = Field(default=None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(default=None)


class ContactUpdate(BaseModel):
    """Request: Kontakt aktualisieren"""
    model_config = ConfigDict(extra="forbid")
    
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(default=None)
    phone: Optional[str] = Field(default=None, max_length=30)
    organization_id: Optional[str] = Field(default=None)
    position: Optional[str] = Field(default=None, max_length=100)
    tags: Optional[List[str]] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class Contact(BaseModel):
    """Contact Entity"""
    model_config = ConfigDict(extra="forbid")
    
    contact_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    organization_id: Optional[str] = None
    position: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    created_at: str
    updated_at: str


class OrganizationCreate(BaseModel):
    """Request: Organisation erstellen"""
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., min_length=1, max_length=200)
    industry: Optional[str] = Field(default=None, max_length=100)
    size: OrganizationSize = Field(default=OrganizationSize.SMALL)
    website: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = Field(default=None, max_length=500)
    tags: List[str] = Field(default_factory=list)


class OrganizationUpdate(BaseModel):
    """Request: Organisation aktualisieren"""
    model_config = ConfigDict(extra="forbid")
    
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    industry: Optional[str] = Field(default=None, max_length=100)
    size: Optional[OrganizationSize] = Field(default=None)
    website: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = Field(default=None, max_length=500)
    tags: Optional[List[str]] = Field(default=None)


class Organization(BaseModel):
    """Organization Entity"""
    model_config = ConfigDict(extra="forbid")
    
    organization_id: str
    name: str
    industry: Optional[str] = None
    size: str
    website: Optional[str] = None
    address: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


class DealCreate(BaseModel):
    """Request: Deal erstellen"""
    model_config = ConfigDict(extra="forbid")
    
    title: str = Field(..., min_length=1, max_length=200)
    value: float = Field(..., ge=0, le=1000000000)  # Max 1 Mrd
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    stage: DealStage = Field(default=DealStage.LEAD)
    contact_id: Optional[str] = Field(default=None)
    organization_id: Optional[str] = Field(default=None)
    close_date: Optional[str] = Field(default=None)  # ISO-Format
    probability: int = Field(default=0, ge=0, le=100)  # Prozent
    tags: List[str] = Field(default_factory=list)


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
    tags: Optional[List[str]] = Field(default=None)


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
    tags: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


class ActivityCreate(BaseModel):
    """Request: Aktivität erstellen"""
    model_config = ConfigDict(extra="forbid")
    
    activity_type: ActivityType
    subject: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    contact_id: Optional[str] = Field(default=None)
    deal_id: Optional[str] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None, ge=0, le=1440)


class Activity(BaseModel):
    """Activity Entity"""
    model_config = ConfigDict(extra="forbid")
    
    activity_id: str
    activity_type: str
    subject: str
    description: Optional[str] = None
    contact_id: Optional[str] = None
    deal_id: Optional[str] = None
    duration_minutes: Optional[int] = None
    timestamp: str


class SearchRequest(BaseModel):
    """Request: Suche"""
    model_config = ConfigDict(extra="forbid")
    
    query: str = Field(..., min_length=1, max_length=200)
    entity_types: List[str] = Field(default=["contacts", "organizations", "deals"])
    max_results: int = Field(default=50, ge=1, le=500)


class CommandRequest(BaseModel):
    """Option-2-Flow Command"""
    model_config = ConfigDict(extra="forbid")
    
    action: str = Field(..., min_length=1)
    params: Dict[str, Any] = Field(default_factory=dict)


# ================== SECURITY ==================

async def verify_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    """Bearer Token validieren"""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    if token != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    
    return token


# ================== DATA PERSISTENCE ==================

class DataStore:
    """Persistenz-Layer für CRM-Daten"""
    
    @staticmethod
    def load_contacts() -> List[Contact]:
        """Lade alle Kontakte"""
        if not CONTACTS_FILE.exists():
            return []
        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Contact(**c) for c in data]
    
    @staticmethod
    def save_contacts(contacts: List[Contact]) -> None:
        """Speichere alle Kontakte"""
        with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([c.model_dump() for c in contacts], f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_organizations() -> List[Organization]:
        """Lade alle Organisationen"""
        if not ORGANIZATIONS_FILE.exists():
            return []
        with open(ORGANIZATIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Organization(**o) for o in data]
    
    @staticmethod
    def save_organizations(organizations: List[Organization]) -> None:
        """Speichere alle Organisationen"""
        with open(ORGANIZATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump([o.model_dump() for o in organizations], f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_deals() -> List[Deal]:
        """Lade alle Deals"""
        if not DEALS_FILE.exists():
            return []
        with open(DEALS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Deal(**d) for d in data]
    
    @staticmethod
    def save_deals(deals: List[Deal]) -> None:
        """Speichere alle Deals"""
        with open(DEALS_FILE, 'w', encoding='utf-8') as f:
            json.dump([d.model_dump() for d in deals], f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_activities() -> List[Activity]:
        """Lade alle Aktivitäten"""
        if not ACTIVITIES_FILE.exists():
            return []
        with open(ACTIVITIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Activity(**a) for a in data]
    
    @staticmethod
    def save_activities(activities: List[Activity]) -> None:
        """Speichere alle Aktivitäten"""
        with open(ACTIVITIES_FILE, 'w', encoding='utf-8') as f:
            json.dump([a.model_dump() for a in activities], f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def log_history(event_type: str, data: Dict[str, Any]) -> None:
        """Append-only History Log"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "data": data
        }
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ================== CRM MANAGER ==================

class CRMManager:
    """CRM Business Logic"""
    
    @staticmethod
    def create_contact(req: ContactCreate) -> Contact:
        """Erstelle Kontakt"""
        contacts = DataStore.load_contacts()
        
        # Email-Uniqueness prüfen
        if any(c.email.lower() == req.email.lower() for c in contacts):
            raise HTTPException(status_code=409, detail=f"Contact with email {req.email} already exists")
        
        # Organisation validieren (falls angegeben)
        if req.organization_id:
            organizations = DataStore.load_organizations()
            if not any(o.organization_id == req.organization_id for o in organizations):
                raise HTTPException(status_code=404, detail=f"Organization not found: {req.organization_id}")
        
        now = datetime.now(timezone.utc).isoformat()
        contact = Contact(
            contact_id=str(uuid.uuid4())[:12],
            first_name=req.first_name,
            last_name=req.last_name,
            email=req.email,
            phone=req.phone,
            organization_id=req.organization_id,
            position=req.position,
            tags=req.tags,
            notes=req.notes,
            created_at=now,
            updated_at=now
        )
        
        contacts.append(contact)
        DataStore.save_contacts(contacts)
        
        # History Log
        DataStore.log_history("create_contact", {
            "contact_id": contact.contact_id,
            "email": contact.email,
            "organization_id": contact.organization_id
        })
        
        return contact
    
    @staticmethod
    def update_contact(contact_id: str, req: ContactUpdate) -> Contact:
        """Aktualisiere Kontakt"""
        contacts = DataStore.load_contacts()
        contact = next((c for c in contacts if c.contact_id == contact_id), None)
        
        if not contact:
            raise HTTPException(status_code=404, detail=f"Contact not found: {contact_id}")
        
        # Email-Uniqueness prüfen (falls geändert)
        if req.email and req.email.lower() != contact.email.lower():
            if any(c.email.lower() == req.email.lower() for c in contacts if c.contact_id != contact_id):
                raise HTTPException(status_code=409, detail=f"Contact with email {req.email} already exists")
        
        # Organisation validieren (falls geändert)
        if req.organization_id:
            organizations = DataStore.load_organizations()
            if not any(o.organization_id == req.organization_id for o in organizations):
                raise HTTPException(status_code=404, detail=f"Organization not found: {req.organization_id}")
        
        # Update Fields (nur gesetzte)
        update_data = req.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)
        
        contact.updated_at = datetime.now(timezone.utc).isoformat()
        
        DataStore.save_contacts(contacts)
        
        # History Log
        DataStore.log_history("update_contact", {
            "contact_id": contact_id,
            "updated_fields": list(update_data.keys())
        })
        
        return contact
    
    @staticmethod
    def list_contacts(organization_id: Optional[str] = None, search: Optional[str] = None, max_results: int = 100) -> List[Contact]:
        """Liste Kontakte"""
        contacts = DataStore.load_contacts()
        
        # Filter: Organization
        if organization_id:
            contacts = [c for c in contacts if c.organization_id == organization_id]
        
        # Filter: Search (Name, Email)
        if search:
            search_lower = search.lower()
            contacts = [
                c for c in contacts
                if search_lower in c.first_name.lower()
                or search_lower in c.last_name.lower()
                or search_lower in c.email.lower()
            ]
        
        return contacts[:max_results]
    
    @staticmethod
    def delete_contact(contact_id: str) -> None:
        """Lösche Kontakt"""
        contacts = DataStore.load_contacts()
        contact = next((c for c in contacts if c.contact_id == contact_id), None)
        
        if not contact:
            raise HTTPException(status_code=404, detail=f"Contact not found: {contact_id}")
        
        # Entferne aus Liste
        contacts = [c for c in contacts if c.contact_id != contact_id]
        DataStore.save_contacts(contacts)
        
        # History Log
        DataStore.log_history("delete_contact", {
            "contact_id": contact_id,
            "email": contact.email
        })
    
    @staticmethod
    def create_organization(req: OrganizationCreate) -> Organization:
        """Erstelle Organisation"""
        organizations = DataStore.load_organizations()
        
        # Name-Uniqueness prüfen
        if any(o.name.lower() == req.name.lower() for o in organizations):
            raise HTTPException(status_code=409, detail=f"Organization with name {req.name} already exists")
        
        now = datetime.now(timezone.utc).isoformat()
        organization = Organization(
            organization_id=str(uuid.uuid4())[:12],
            name=req.name,
            industry=req.industry,
            size=req.size.value,
            website=req.website,
            address=req.address,
            tags=req.tags,
            created_at=now,
            updated_at=now
        )
        
        organizations.append(organization)
        DataStore.save_organizations(organizations)
        
        # History Log
        DataStore.log_history("create_organization", {
            "organization_id": organization.organization_id,
            "name": organization.name,
            "industry": organization.industry
        })
        
        return organization
    
    @staticmethod
    def update_organization(organization_id: str, req: OrganizationUpdate) -> Organization:
        """Aktualisiere Organisation"""
        organizations = DataStore.load_organizations()
        organization = next((o for o in organizations if o.organization_id == organization_id), None)
        
        if not organization:
            raise HTTPException(status_code=404, detail=f"Organization not found: {organization_id}")
        
        # Name-Uniqueness prüfen (falls geändert)
        if req.name and req.name.lower() != organization.name.lower():
            if any(o.name.lower() == req.name.lower() for o in organizations if o.organization_id != organization_id):
                raise HTTPException(status_code=409, detail=f"Organization with name {req.name} already exists")
        
        # Update Fields
        update_data = req.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "size" and value:
                setattr(organization, field, value.value)
            else:
                setattr(organization, field, value)
        
        organization.updated_at = datetime.now(timezone.utc).isoformat()
        
        DataStore.save_organizations(organizations)
        
        # History Log
        DataStore.log_history("update_organization", {
            "organization_id": organization_id,
            "updated_fields": list(update_data.keys())
        })
        
        return organization
    
    @staticmethod
    def list_organizations(search: Optional[str] = None, max_results: int = 100) -> List[Organization]:
        """Liste Organisationen"""
        organizations = DataStore.load_organizations()
        
        # Filter: Search (Name, Industry)
        if search:
            search_lower = search.lower()
            organizations = [
                o for o in organizations
                if search_lower in o.name.lower()
                or (o.industry and search_lower in o.industry.lower())
            ]
        
        return organizations[:max_results]
    
    @staticmethod
    def delete_organization(organization_id: str) -> None:
        """Lösche Organisation"""
        organizations = DataStore.load_organizations()
        organization = next((o for o in organizations if o.organization_id == organization_id), None)
        
        if not organization:
            raise HTTPException(status_code=404, detail=f"Organization not found: {organization_id}")
        
        # Entferne aus Liste
        organizations = [o for o in organizations if o.organization_id != organization_id]
        DataStore.save_organizations(organizations)
        
        # History Log
        DataStore.log_history("delete_organization", {
            "organization_id": organization_id,
            "name": organization.name
        })
    
    @staticmethod
    def create_deal(req: DealCreate) -> Deal:
        """Erstelle Deal"""
        # Contact validieren (falls angegeben)
        if req.contact_id:
            contacts = DataStore.load_contacts()
            if not any(c.contact_id == req.contact_id for c in contacts):
                raise HTTPException(status_code=404, detail=f"Contact not found: {req.contact_id}")
        
        # Organization validieren (falls angegeben)
        if req.organization_id:
            organizations = DataStore.load_organizations()
            if not any(o.organization_id == req.organization_id for o in organizations):
                raise HTTPException(status_code=404, detail=f"Organization not found: {req.organization_id}")
        
        now = datetime.now(timezone.utc).isoformat()
        deal = Deal(
            deal_id=str(uuid.uuid4())[:12],
            title=req.title,
            value=req.value,
            currency=req.currency,
            stage=req.stage.value,
            contact_id=req.contact_id,
            organization_id=req.organization_id,
            close_date=req.close_date,
            probability=req.probability,
            tags=req.tags,
            created_at=now,
            updated_at=now
        )
        
        deals = DataStore.load_deals()
        deals.append(deal)
        DataStore.save_deals(deals)
        
        # History Log
        DataStore.log_history("create_deal", {
            "deal_id": deal.deal_id,
            "title": deal.title,
            "value": deal.value,
            "stage": deal.stage
        })
        
        return deal
    
    @staticmethod
    def update_deal(deal_id: str, req: DealUpdate) -> Deal:
        """Aktualisiere Deal"""
        deals = DataStore.load_deals()
        deal = next((d for d in deals if d.deal_id == deal_id), None)
        
        if not deal:
            raise HTTPException(status_code=404, detail=f"Deal not found: {deal_id}")
        
        # Contact validieren (falls geändert)
        if req.contact_id:
            contacts = DataStore.load_contacts()
            if not any(c.contact_id == req.contact_id for c in contacts):
                raise HTTPException(status_code=404, detail=f"Contact not found: {req.contact_id}")
        
        # Organization validieren (falls geändert)
        if req.organization_id:
            organizations = DataStore.load_organizations()
            if not any(o.organization_id == req.organization_id for o in organizations):
                raise HTTPException(status_code=404, detail=f"Organization not found: {req.organization_id}")
        
        # Update Fields
        update_data = req.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "stage" and value:
                setattr(deal, field, value.value)
            else:
                setattr(deal, field, value)
        
        deal.updated_at = datetime.now(timezone.utc).isoformat()
        
        DataStore.save_deals(deals)
        
        # History Log
        DataStore.log_history("update_deal", {
            "deal_id": deal_id,
            "updated_fields": list(update_data.keys()),
            "new_stage": deal.stage
        })
        
        return deal
    
    @staticmethod
    def list_deals(stage: Optional[str] = None, contact_id: Optional[str] = None, max_results: int = 100) -> List[Deal]:
        """Liste Deals"""
        deals = DataStore.load_deals()
        
        # Filter: Stage
        if stage:
            deals = [d for d in deals if d.stage == stage]
        
        # Filter: Contact
        if contact_id:
            deals = [d for d in deals if d.contact_id == contact_id]
        
        return deals[:max_results]
    
    @staticmethod
    def delete_deal(deal_id: str) -> None:
        """Lösche Deal"""
        deals = DataStore.load_deals()
        deal = next((d for d in deals if d.deal_id == deal_id), None)
        
        if not deal:
            raise HTTPException(status_code=404, detail=f"Deal not found: {deal_id}")
        
        # Entferne aus Liste
        deals = [d for d in deals if d.deal_id != deal_id]
        DataStore.save_deals(deals)
        
        # History Log
        DataStore.log_history("delete_deal", {
            "deal_id": deal_id,
            "title": deal.title
        })
    
    @staticmethod
    def create_activity(req: ActivityCreate) -> Activity:
        """Erstelle Aktivität"""
        # Contact validieren (falls angegeben)
        if req.contact_id:
            contacts = DataStore.load_contacts()
            if not any(c.contact_id == req.contact_id for c in contacts):
                raise HTTPException(status_code=404, detail=f"Contact not found: {req.contact_id}")
        
        # Deal validieren (falls angegeben)
        if req.deal_id:
            deals = DataStore.load_deals()
            if not any(d.deal_id == req.deal_id for d in deals):
                raise HTTPException(status_code=404, detail=f"Deal not found: {req.deal_id}")
        
        activity = Activity(
            activity_id=str(uuid.uuid4())[:12],
            activity_type=req.activity_type.value,
            subject=req.subject,
            description=req.description,
            contact_id=req.contact_id,
            deal_id=req.deal_id,
            duration_minutes=req.duration_minutes,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        activities = DataStore.load_activities()
        activities.append(activity)
        DataStore.save_activities(activities)
        
        # History Log
        DataStore.log_history("create_activity", {
            "activity_id": activity.activity_id,
            "type": activity.activity_type,
            "contact_id": activity.contact_id,
            "deal_id": activity.deal_id
        })
        
        return activity
    
    @staticmethod
    def list_activities(contact_id: Optional[str] = None, deal_id: Optional[str] = None, max_results: int = 100) -> List[Activity]:
        """Liste Aktivitäten"""
        activities = DataStore.load_activities()
        
        # Filter: Contact
        if contact_id:
            activities = [a for a in activities if a.contact_id == contact_id]
        
        # Filter: Deal
        if deal_id:
            activities = [a for a in activities if a.deal_id == deal_id]
        
        # Sortiere: Neueste zuerst
        activities = sorted(activities, key=lambda a: a.timestamp, reverse=True)
        
        return activities[:max_results]
    
    @staticmethod
    def search(req: SearchRequest) -> Dict[str, List[Any]]:
        """Globale Suche"""
        results = {
            "contacts": [],
            "organizations": [],
            "deals": []
        }
        
        query_lower = req.query.lower()
        
        # Suche Contacts
        if "contacts" in req.entity_types:
            contacts = DataStore.load_contacts()
            matches = [
                c.model_dump() for c in contacts
                if query_lower in c.first_name.lower()
                or query_lower in c.last_name.lower()
                or query_lower in c.email.lower()
            ]
            results["contacts"] = matches[:req.max_results]
        
        # Suche Organizations
        if "organizations" in req.entity_types:
            organizations = DataStore.load_organizations()
            matches = [
                o.model_dump() for o in organizations
                if query_lower in o.name.lower()
                or (o.industry and query_lower in o.industry.lower())
            ]
            results["organizations"] = matches[:req.max_results]
        
        # Suche Deals
        if "deals" in req.entity_types:
            deals = DataStore.load_deals()
            matches = [
                d.model_dump() for d in deals
                if query_lower in d.title.lower()
            ]
            results["deals"] = matches[:req.max_results]
        
        return results


# ================== FASTAPI APP ==================

app = FastAPI(
    title=f"{SERVICE_NAME} - CRM Agent",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/")
async def root():
    """Root Endpoint"""
    return {
        "service": SERVICE_NAME,
        "kuerzel": KUERZEL,
        "version": VERSION,
        "port": PORT,
        "status": "running",
        "endpoints": [
            "/health",
            "/contacts",
            "/organizations",
            "/deals",
            "/activities",
            "/search",
            "/command"
        ]
    }


@app.get("/health")
async def health():
    """Health Check (ohne Auth)"""
    uptime = (datetime.now(timezone.utc) - START_TIME).total_seconds()
    
    # Zähle Entities
    total_contacts = len(DataStore.load_contacts())
    total_organizations = len(DataStore.load_organizations())
    total_deals = len(DataStore.load_deals())
    total_activities = len(DataStore.load_activities())
    
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "kuerzel": KUERZEL,
        "port": PORT,
        "uptime_seconds": round(uptime, 2),
        "total_contacts": total_contacts,
        "total_organizations": total_organizations,
        "total_deals": total_deals,
        "total_activities": total_activities
    }


# ========== CONTACTS ==========

@app.post("/contacts", response_model=Contact)
async def create_contact(req: ContactCreate, token: str = Depends(verify_bearer_token)):
    """Erstelle Kontakt"""
    return CRMManager.create_contact(req)


@app.put("/contacts/{contact_id}", response_model=Contact)
async def update_contact(contact_id: str, req: ContactUpdate, token: str = Depends(verify_bearer_token)):
    """Aktualisiere Kontakt"""
    return CRMManager.update_contact(contact_id, req)


@app.get("/contacts", response_model=List[Contact])
async def list_contacts(
    organization_id: Optional[str] = None,
    search: Optional[str] = None,
    max_results: int = 100,
    token: str = Depends(verify_bearer_token)
):
    """Liste Kontakte"""
    return CRMManager.list_contacts(organization_id, search, max_results)


@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str, token: str = Depends(verify_bearer_token)):
    """Lösche Kontakt"""
    CRMManager.delete_contact(contact_id)
    return {"status": "deleted", "contact_id": contact_id}


# ========== ORGANIZATIONS ==========

@app.post("/organizations", response_model=Organization)
async def create_organization(req: OrganizationCreate, token: str = Depends(verify_bearer_token)):
    """Erstelle Organisation"""
    return CRMManager.create_organization(req)


@app.put("/organizations/{organization_id}", response_model=Organization)
async def update_organization(organization_id: str, req: OrganizationUpdate, token: str = Depends(verify_bearer_token)):
    """Aktualisiere Organisation"""
    return CRMManager.update_organization(organization_id, req)


@app.get("/organizations", response_model=List[Organization])
async def list_organizations(
    search: Optional[str] = None,
    max_results: int = 100,
    token: str = Depends(verify_bearer_token)
):
    """Liste Organisationen"""
    return CRMManager.list_organizations(search, max_results)


@app.delete("/organizations/{organization_id}")
async def delete_organization(organization_id: str, token: str = Depends(verify_bearer_token)):
    """Lösche Organisation"""
    CRMManager.delete_organization(organization_id)
    return {"status": "deleted", "organization_id": organization_id}


# ========== DEALS ==========

@app.post("/deals", response_model=Deal)
async def create_deal(req: DealCreate, token: str = Depends(verify_bearer_token)):
    """Erstelle Deal"""
    return CRMManager.create_deal(req)


@app.put("/deals/{deal_id}", response_model=Deal)
async def update_deal(deal_id: str, req: DealUpdate, token: str = Depends(verify_bearer_token)):
    """Aktualisiere Deal"""
    return CRMManager.update_deal(deal_id, req)


@app.get("/deals", response_model=List[Deal])
async def list_deals(
    stage: Optional[str] = None,
    contact_id: Optional[str] = None,
    max_results: int = 100,
    token: str = Depends(verify_bearer_token)
):
    """Liste Deals"""
    return CRMManager.list_deals(stage, contact_id, max_results)


@app.delete("/deals/{deal_id}")
async def delete_deal(deal_id: str, token: str = Depends(verify_bearer_token)):
    """Lösche Deal"""
    CRMManager.delete_deal(deal_id)
    return {"status": "deleted", "deal_id": deal_id}


# ========== ACTIVITIES ==========

@app.post("/activities", response_model=Activity)
async def create_activity(req: ActivityCreate, token: str = Depends(verify_bearer_token)):
    """Erstelle Aktivität"""
    return CRMManager.create_activity(req)


@app.get("/activities", response_model=List[Activity])
async def list_activities(
    contact_id: Optional[str] = None,
    deal_id: Optional[str] = None,
    max_results: int = 100,
    token: str = Depends(verify_bearer_token)
):
    """Liste Aktivitäten"""
    return CRMManager.list_activities(contact_id, deal_id, max_results)


# ========== SEARCH ==========

@app.post("/search")
async def search(req: SearchRequest, token: str = Depends(verify_bearer_token)):
    """Globale Suche"""
    return CRMManager.search(req)


# ========== COMMAND ==========

@app.post("/command")
async def command(req: CommandRequest, token: str = Depends(verify_bearer_token)):
    """Option-2-Flow: Universeller Command-Endpoint"""
    action = req.action
    params = req.params
    
    try:
        if action == "create_contact":
            contact_req = ContactCreate(**params)
            contact = CRMManager.create_contact(contact_req)
            return {"status": "success", "action": action, "result": contact.model_dump()}
        
        elif action == "create_organization":
            org_req = OrganizationCreate(**params)
            organization = CRMManager.create_organization(org_req)
            return {"status": "success", "action": action, "result": organization.model_dump()}
        
        elif action == "create_deal":
            deal_req = DealCreate(**params)
            deal = CRMManager.create_deal(deal_req)
            return {"status": "success", "action": action, "result": deal.model_dump()}
        
        elif action == "create_activity":
            activity_req = ActivityCreate(**params)
            activity = CRMManager.create_activity(activity_req)
            return {"status": "success", "action": action, "result": activity.model_dump()}
        
        elif action == "list_contacts":
            contacts = CRMManager.list_contacts(
                organization_id=params.get("organization_id"),
                search=params.get("search"),
                max_results=params.get("max_results", 100)
            )
            return {"status": "success", "action": action, "result": [c.model_dump() for c in contacts]}
        
        elif action == "search":
            search_req = SearchRequest(**params)
            results = CRMManager.search(search_req)
            return {"status": "success", "action": action, "result": results}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Command failed: {str(e)}")


# ================== MAIN ==================

if __name__ == "__main__":
    print(f"[INFO] Starting {SERVICE_NAME} ({KUERZEL}) on port {PORT}...")
    print(f"[INFO] Data Directory: {DATA_DIR}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
