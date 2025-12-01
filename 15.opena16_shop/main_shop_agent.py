#!/usr/bin/env python3
"""
opena16 - Shop Management Agent
Port: 12361
Kürzel: shopp

Features:
- Product Management (CRUD)
- Inventory Tracking
- Order Management
- Price Management
- Category Management
- Multi-Shop Support
"""

import os
import sys
import time
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field, field_validator
from fastapi.responses import JSONResponse

# ============================================================================
# CONFIG & CONSTANTS
# ============================================================================

PORT = 12361
SERVICE_NAME = "opena16"
KUERZEL = "shopp"
VERSION = "1.0"

# ENV-Token
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")

# Pfade
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
PRODUCTS_FILE = DATA_DIR / "products.json"
ORDERS_FILE = DATA_DIR / "orders.json"
INVENTORY_FILE = DATA_DIR / "inventory.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
SHOP_HISTORY_FILE = DATA_DIR / "shop_history.jsonl"

# Directories erstellen
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# App-Start-Zeit
START_TIME = time.time()

# ============================================================================
# ENUMS
# ============================================================================

class ProductStatus(str, Enum):
    """Product Status"""
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"
    OUT_OF_STOCK = "out_of_stock"

class OrderStatus(str, Enum):
    """Order Status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Currency(str, Enum):
    """Supported Currencies"""
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"

# ============================================================================
# DATA MODELS (Pydantic)
# ============================================================================

class ProductCreate(BaseModel):
    """Create Product"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    sku: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, le=1_000_000)
    currency: Currency = Currency.EUR
    category_id: Optional[str] = None
    status: ProductStatus = ProductStatus.ACTIVE
    tags: List[str] = Field(default_factory=list, max_items=20)
    
    class Config:
        extra = "forbid"
    
    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v: str) -> str:
        # Alphanumeric + dashes/underscores
        if not all(c.isalnum() or c in "-_" for c in v):
            raise ValueError("SKU must be alphanumeric with dashes/underscores")
        return v.upper()

class ProductUpdate(BaseModel):
    """Update Product"""
    product_id: str = Field(..., min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, gt=0, le=1_000_000)
    status: Optional[ProductStatus] = None
    tags: Optional[List[str]] = Field(None, max_items=20)
    
    class Config:
        extra = "forbid"

class ProductListRequest(BaseModel):
    """List Products with Filters"""
    category_id: Optional[str] = None
    status: Optional[ProductStatus] = None
    search: Optional[str] = Field(None, max_length=100)
    max_results: int = Field(default=50, ge=1, le=500)
    
    class Config:
        extra = "forbid"

class InventoryUpdate(BaseModel):
    """Update Inventory"""
    sku: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0, le=1_000_000)
    warehouse: str = Field(default="main", max_length=50)
    
    class Config:
        extra = "forbid"

class OrderCreate(BaseModel):
    """Create Order"""
    customer_name: str = Field(..., min_length=1, max_length=200)
    customer_email: str = Field(..., min_length=1, max_length=200)
    items: List[Dict[str, Any]] = Field(..., min_items=1, max_items=100)
    currency: Currency = Currency.EUR
    shipping_address: Optional[str] = Field(None, max_length=500)
    
    class Config:
        extra = "forbid"
    
    @field_validator("customer_email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

class OrderListRequest(BaseModel):
    """List Orders with Filters"""
    status: Optional[OrderStatus] = None
    customer_email: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    max_results: int = Field(default=50, ge=1, le=500)
    
    class Config:
        extra = "forbid"

class CategoryCreate(BaseModel):
    """Create Category"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[str] = None
    
    class Config:
        extra = "forbid"

class ProductResponse(BaseModel):
    """Product Response"""
    product_id: str
    title: str
    description: Optional[str]
    sku: str
    price: float
    currency: str
    category_id: Optional[str]
    status: str
    tags: List[str]
    created_at: str
    updated_at: str

class OrderResponse(BaseModel):
    """Order Response"""
    order_id: str
    customer_name: str
    customer_email: str
    items: List[Dict[str, Any]]
    total: float
    currency: str
    status: str
    created_at: str
    updated_at: str

class CommandRequest(BaseModel):
    """Option-2-Flow Command Endpoint"""
    action: str = Field(..., min_length=1, max_length=100)
    params: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "forbid"

# ============================================================================
# DATACLASSES (Persistence)
# ============================================================================

@dataclass
class Product:
    """Product Entity"""
    product_id: str
    title: str
    description: Optional[str]
    sku: str
    price: float
    currency: str
    category_id: Optional[str]
    status: str
    tags: List[str]
    created_at: str
    updated_at: str

@dataclass
class Order:
    """Order Entity"""
    order_id: str
    customer_name: str
    customer_email: str
    items: List[Dict[str, Any]]
    total: float
    currency: str
    status: str
    shipping_address: Optional[str]
    created_at: str
    updated_at: str

@dataclass
class Inventory:
    """Inventory Entry"""
    sku: str
    quantity: int
    warehouse: str
    updated_at: str

@dataclass
class Category:
    """Product Category"""
    category_id: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    created_at: str

@dataclass
class ShopHistoryRecord:
    """Shop Operation History"""
    record_id: str
    timestamp: str
    operation: str
    entity_type: str
    entity_id: str
    details: Dict[str, Any]

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="opena16 - Shop Management Agent",
    version=VERSION,
    description="E-Commerce Management, Product CRUD, Orders, Inventory (shopp)"
)

# ============================================================================
# AUTH DEPENDENCY
# ============================================================================

def verify_token(authorization: Optional[str] = Header(None)) -> bool:
    """Bearer Token Verification"""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
    
    token = authorization.replace("Bearer ", "")
    if token != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return True

# ============================================================================
# DATA STORE
# ============================================================================

class DataStore:
    """Persistence Layer"""
    
    @staticmethod
    def load_products() -> List[Product]:
        """Load all products"""
        if not PRODUCTS_FILE.exists():
            return []
        
        data = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
        return [Product(**p) for p in data]
    
    @staticmethod
    def save_products(products: List[Product]):
        """Save all products"""
        data = [asdict(p) for p in products]
        PRODUCTS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    @staticmethod
    def load_orders() -> List[Order]:
        """Load all orders"""
        if not ORDERS_FILE.exists():
            return []
        
        data = json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
        return [Order(**o) for o in data]
    
    @staticmethod
    def save_orders(orders: List[Order]):
        """Save all orders"""
        data = [asdict(o) for o in orders]
        ORDERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    @staticmethod
    def load_inventory() -> List[Inventory]:
        """Load inventory"""
        if not INVENTORY_FILE.exists():
            return []
        
        data = json.loads(INVENTORY_FILE.read_text(encoding="utf-8"))
        return [Inventory(**i) for i in data]
    
    @staticmethod
    def save_inventory(inventory: List[Inventory]):
        """Save inventory"""
        data = [asdict(i) for i in inventory]
        INVENTORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    @staticmethod
    def load_categories() -> List[Category]:
        """Load categories"""
        if not CATEGORIES_FILE.exists():
            return []
        
        data = json.loads(CATEGORIES_FILE.read_text(encoding="utf-8"))
        return [Category(**c) for c in data]
    
    @staticmethod
    def save_categories(categories: List[Category]):
        """Save categories"""
        data = [asdict(c) for c in categories]
        CATEGORIES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    @staticmethod
    def append_history(record: ShopHistoryRecord):
        """Append to history log"""
        with SHOP_HISTORY_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

# ============================================================================
# BUSINESS LOGIC
# ============================================================================

class ShopManager:
    """Shop Operations Manager"""
    
    @staticmethod
    def create_product(req: ProductCreate) -> Product:
        """Create new product"""
        products = DataStore.load_products()
        
        # Check SKU uniqueness
        if any(p.sku == req.sku for p in products):
            raise HTTPException(status_code=409, detail=f"SKU already exists: {req.sku}")
        
        now = datetime.now(timezone.utc).isoformat()
        
        product = Product(
            product_id=uuid.uuid4().hex[:12],
            title=req.title,
            description=req.description,
            sku=req.sku,
            price=req.price,
            currency=req.currency.value,
            category_id=req.category_id,
            status=req.status.value,
            tags=req.tags,
            created_at=now,
            updated_at=now
        )
        
        products.append(product)
        DataStore.save_products(products)
        
        # Initialize inventory
        inventory = DataStore.load_inventory()
        inventory.append(Inventory(
            sku=req.sku,
            quantity=0,
            warehouse="main",
            updated_at=now
        ))
        DataStore.save_inventory(inventory)
        
        # History
        DataStore.append_history(ShopHistoryRecord(
            record_id=uuid.uuid4().hex,
            timestamp=now,
            operation="create_product",
            entity_type="product",
            entity_id=product.product_id,
            details={"sku": req.sku, "title": req.title, "price": req.price}
        ))
        
        return product
    
    @staticmethod
    def update_product(req: ProductUpdate) -> Product:
        """Update existing product"""
        products = DataStore.load_products()
        
        product = next((p for p in products if p.product_id == req.product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product not found: {req.product_id}")
        
        # Update fields
        if req.title is not None:
            product.title = req.title
        if req.description is not None:
            product.description = req.description
        if req.price is not None:
            product.price = req.price
        if req.status is not None:
            product.status = req.status.value
        if req.tags is not None:
            product.tags = req.tags
        
        product.updated_at = datetime.now(timezone.utc).isoformat()
        
        DataStore.save_products(products)
        
        # History
        DataStore.append_history(ShopHistoryRecord(
            record_id=uuid.uuid4().hex,
            timestamp=product.updated_at,
            operation="update_product",
            entity_type="product",
            entity_id=product.product_id,
            details={"sku": product.sku, "changes": req.model_dump(exclude_unset=True)}
        ))
        
        return product
    
    @staticmethod
    def list_products(req: ProductListRequest) -> List[Product]:
        """List products with filters"""
        products = DataStore.load_products()
        
        # Filter by category
        if req.category_id:
            products = [p for p in products if p.category_id == req.category_id]
        
        # Filter by status
        if req.status:
            products = [p for p in products if p.status == req.status.value]
        
        # Search in title/description
        if req.search:
            search_lower = req.search.lower()
            products = [
                p for p in products
                if search_lower in p.title.lower() or (p.description and search_lower in p.description.lower())
            ]
        
        # Limit results
        return products[:req.max_results]
    
    @staticmethod
    def delete_product(product_id: str):
        """Delete product"""
        products = DataStore.load_products()
        
        product = next((p for p in products if p.product_id == product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product not found: {product_id}")
        
        products = [p for p in products if p.product_id != product_id]
        DataStore.save_products(products)
        
        # History
        DataStore.append_history(ShopHistoryRecord(
            record_id=uuid.uuid4().hex,
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation="delete_product",
            entity_type="product",
            entity_id=product_id,
            details={"sku": product.sku, "title": product.title}
        ))
    
    @staticmethod
    def update_inventory(req: InventoryUpdate) -> Inventory:
        """Update inventory"""
        inventory = DataStore.load_inventory()
        
        entry = next((i for i in inventory if i.sku == req.sku and i.warehouse == req.warehouse), None)
        
        now = datetime.now(timezone.utc).isoformat()
        
        if entry:
            entry.quantity = req.quantity
            entry.updated_at = now
        else:
            entry = Inventory(
                sku=req.sku,
                quantity=req.quantity,
                warehouse=req.warehouse,
                updated_at=now
            )
            inventory.append(entry)
        
        DataStore.save_inventory(inventory)
        
        # Update product status if out of stock
        products = DataStore.load_products()
        product = next((p for p in products if p.sku == req.sku), None)
        if product:
            if req.quantity == 0 and product.status == ProductStatus.ACTIVE.value:
                product.status = ProductStatus.OUT_OF_STOCK.value
                product.updated_at = now
                DataStore.save_products(products)
            elif req.quantity > 0 and product.status == ProductStatus.OUT_OF_STOCK.value:
                product.status = ProductStatus.ACTIVE.value
                product.updated_at = now
                DataStore.save_products(products)
        
        # History
        DataStore.append_history(ShopHistoryRecord(
            record_id=uuid.uuid4().hex,
            timestamp=now,
            operation="update_inventory",
            entity_type="inventory",
            entity_id=req.sku,
            details={"quantity": req.quantity, "warehouse": req.warehouse}
        ))
        
        return entry
    
    @staticmethod
    def create_order(req: OrderCreate) -> Order:
        """Create new order"""
        # Calculate total
        total = 0.0
        products = DataStore.load_products()
        
        for item in req.items:
            sku = item.get("sku")
            quantity = item.get("quantity", 1)
            
            product = next((p for p in products if p.sku == sku), None)
            if not product:
                raise HTTPException(status_code=404, detail=f"Product not found: {sku}")
            
            total += product.price * quantity
        
        now = datetime.now(timezone.utc).isoformat()
        
        order = Order(
            order_id=uuid.uuid4().hex[:12],
            customer_name=req.customer_name,
            customer_email=req.customer_email,
            items=req.items,
            total=round(total, 2),
            currency=req.currency.value,
            status=OrderStatus.PENDING.value,
            shipping_address=req.shipping_address,
            created_at=now,
            updated_at=now
        )
        
        orders = DataStore.load_orders()
        orders.append(order)
        DataStore.save_orders(orders)
        
        # History
        DataStore.append_history(ShopHistoryRecord(
            record_id=uuid.uuid4().hex,
            timestamp=now,
            operation="create_order",
            entity_type="order",
            entity_id=order.order_id,
            details={"customer": req.customer_email, "total": total, "items_count": len(req.items)}
        ))
        
        return order
    
    @staticmethod
    def list_orders(req: OrderListRequest) -> List[Order]:
        """List orders with filters"""
        orders = DataStore.load_orders()
        
        # Filter by status
        if req.status:
            orders = [o for o in orders if o.status == req.status.value]
        
        # Filter by customer email
        if req.customer_email:
            orders = [o for o in orders if o.customer_email == req.customer_email.lower()]
        
        # Filter by date range
        if req.date_from:
            date_from = datetime.fromisoformat(req.date_from.replace("Z", "+00:00"))
            orders = [o for o in orders if datetime.fromisoformat(o.created_at.replace("Z", "+00:00")) >= date_from]
        
        if req.date_to:
            date_to = datetime.fromisoformat(req.date_to.replace("Z", "+00:00"))
            orders = [o for o in orders if datetime.fromisoformat(o.created_at.replace("Z", "+00:00")) <= date_to]
        
        # Limit results
        return orders[:req.max_results]
    
    @staticmethod
    def create_category(req: CategoryCreate) -> Category:
        """Create new category"""
        categories = DataStore.load_categories()
        
        # Check name uniqueness
        if any(c.name.lower() == req.name.lower() for c in categories):
            raise HTTPException(status_code=409, detail=f"Category already exists: {req.name}")
        
        category = Category(
            category_id=uuid.uuid4().hex[:8],
            name=req.name,
            description=req.description,
            parent_id=req.parent_id,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        categories.append(category)
        DataStore.save_categories(categories)
        
        return category

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": SERVICE_NAME,
        "kuerzel": KUERZEL,
        "version": VERSION,
        "port": PORT,
        "description": "Shop Management Agent - E-Commerce, Products, Orders, Inventory (shopp)"
    }

@app.get("/health")
async def health():
    """Health check (no auth)"""
    uptime = round(time.time() - START_TIME, 2)
    
    products = DataStore.load_products()
    orders = DataStore.load_orders()
    
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "kuerzel": KUERZEL,
        "port": PORT,
        "uptime_seconds": uptime,
        "total_products": len(products),
        "total_orders": len(orders)
    }

@app.post("/products/create", response_model=ProductResponse)
async def create_product(req: ProductCreate, _: bool = Depends(verify_token)):
    """Create new product"""
    product = ShopManager.create_product(req)
    return ProductResponse(**asdict(product))

@app.put("/products/update", response_model=ProductResponse)
async def update_product(req: ProductUpdate, _: bool = Depends(verify_token)):
    """Update existing product"""
    product = ShopManager.update_product(req)
    return ProductResponse(**asdict(product))

@app.post("/products/list", response_model=List[ProductResponse])
async def list_products(req: ProductListRequest, _: bool = Depends(verify_token)):
    """List products with filters"""
    products = ShopManager.list_products(req)
    return [ProductResponse(**asdict(p)) for p in products]

@app.delete("/products/delete")
async def delete_product(product_id: str, _: bool = Depends(verify_token)):
    """Delete product"""
    ShopManager.delete_product(product_id)
    return {"success": True, "message": f"Product deleted: {product_id}"}

@app.post("/inventory/update")
async def update_inventory(req: InventoryUpdate, _: bool = Depends(verify_token)):
    """Update inventory"""
    entry = ShopManager.update_inventory(req)
    return {
        "success": True,
        "sku": entry.sku,
        "quantity": entry.quantity,
        "warehouse": entry.warehouse,
        "updated_at": entry.updated_at
    }

@app.get("/inventory/list")
async def list_inventory(_: bool = Depends(verify_token)):
    """List all inventory"""
    inventory = DataStore.load_inventory()
    return [asdict(i) for i in inventory]

@app.post("/orders/create", response_model=OrderResponse)
async def create_order(req: OrderCreate, _: bool = Depends(verify_token)):
    """Create new order"""
    order = ShopManager.create_order(req)
    return OrderResponse(**asdict(order))

@app.post("/orders/list", response_model=List[OrderResponse])
async def list_orders(req: OrderListRequest, _: bool = Depends(verify_token)):
    """List orders with filters"""
    orders = ShopManager.list_orders(req)
    return [OrderResponse(**asdict(o)) for o in orders]

@app.post("/categories/create")
async def create_category(req: CategoryCreate, _: bool = Depends(verify_token)):
    """Create new category"""
    category = ShopManager.create_category(req)
    return asdict(category)

@app.get("/categories/list")
async def list_categories(_: bool = Depends(verify_token)):
    """List all categories"""
    categories = DataStore.load_categories()
    return [asdict(c) for c in categories]

@app.post("/command")
async def command_endpoint(req: CommandRequest, _: bool = Depends(verify_token)):
    """Option-2-Flow command endpoint"""
    action = req.action
    params = req.params
    
    if action == "create_product":
        prod_req = ProductCreate(**params)
        product = ShopManager.create_product(prod_req)
        
        return {
            "action": action,
            "success": True,
            "result": asdict(product),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    elif action == "update_inventory":
        inv_req = InventoryUpdate(**params)
        entry = ShopManager.update_inventory(inv_req)
        
        return {
            "action": action,
            "success": True,
            "result": asdict(entry),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    elif action == "create_order":
        order_req = OrderCreate(**params)
        order = ShopManager.create_order(order_req)
        
        return {
            "action": action,
            "success": True,
            "result": asdict(order),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    elif action == "list_products":
        list_req = ProductListRequest(**params)
        products = ShopManager.list_products(list_req)
        
        return {
            "action": action,
            "success": True,
            "result": [asdict(p) for p in products],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print(f"[INFO] Starting {SERVICE_NAME} ({KUERZEL}) on port {PORT}...")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
