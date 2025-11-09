"""
opena15_Shop: E-Commerce / Shop Agent
Product catalog, order management, inventory tracking, pricing, cart management
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import logging
import json
import urllib.request
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
import sys
import secrets

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena15_Shop",
    version="1.0.0",
    description="E-Commerce / Shop Agent - Product & Order Management"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12363
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory storage
_products: Dict[str, dict] = {}
_inventory: Dict[str, int] = {}
_orders: Dict[str, dict] = {}
_carts: Dict[str, dict] = {}
_pricing: Dict[str, dict] = {}

# ============================================================================
# DATA MODELS
# ============================================================================


class Product(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int


class OrderCreateRequest(BaseModel):
    customer_name: str
    items: List[Dict[str, Any]]  # {"product_id": "...", "quantity": 2}
    shipping_address: str


class InventoryUpdateRequest(BaseModel):
    product_id: str
    quantity_change: int  # positive (add) or negative (remove)
    reason: str = "adjustment"


class PricingCalculateRequest(BaseModel):
    items: List[Dict[str, Any]]  # {"product_id": "...", "quantity": 2}
    discount_code: Optional[str] = None


class CartManageRequest(BaseModel):
    cart_id: str
    action: str  # add, remove, clear
    product_id: Optional[str] = None
    quantity: Optional[int] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: Optional[str]):
    """Validate Bearer token"""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = auth_header.replace("Bearer ", "").strip()
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


async def _archive(payload: dict):
    """Archive operation to opena2"""
    try:
        data = {
            "src": "opena15_shop",
            "dst": "opena2",
            "kind": "SHOP_OP",
            "payload": {**payload, "ts": datetime.utcnow().isoformat() + "Z"}
        }
        
        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.warning(f"⚠️ Archive failed: {e}")
        return {"written": False}


def _generate_product_id() -> str:
    """Generate unique product ID"""
    return f"PRD_{secrets.token_hex(6).upper()}"


def _generate_order_id() -> str:
    """Generate unique order ID"""
    return f"ORD_{secrets.token_hex(6).upper()}"


def _generate_cart_id() -> str:
    """Generate unique cart ID"""
    return f"CART_{secrets.token_hex(6).upper()}"


def _apply_discount(total: float, discount_code: Optional[str]) -> Dict[str, float]:
    """Apply discount code"""
    discount_rates = {
        "SAVE10": 0.10,
        "SAVE20": 0.20,
        "WELCOME": 0.15
    }
    
    discount_rate = discount_rates.get(discount_code, 0.0)
    discount_amount = total * discount_rate
    
    return {
        "original": total,
        "discount_rate": discount_rate,
        "discount_amount": discount_amount,
        "final_total": total - discount_amount
    }


def _get_product_or_404(product_id: str) -> dict:
    """Get product or raise 404"""
    if product_id not in _products:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return _products[product_id]


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena15_Shop",
        "port": PORT,
        "products": len(_products),
        "orders": len(_orders),
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/product/list")
async def list_products(authorization: str = Header(None)):
    """List all products"""
    _validate_token(authorization)
    
    try:
        products_list = []
        for product_id, product in _products.items():
            stock = _inventory.get(product_id, 0)
            products_list.append({
                "id": product_id,
                **product,
                "stock": stock
            })
        
        logger.info(f"📦 Products listed: {len(products_list)}")
        
        return {
            "strict": True,
            "products": products_list,
            "count": len(products_list),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Product listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/order/create")
async def create_order(req: OrderCreateRequest, authorization: str = Header(None)):
    """Create new order"""
    _validate_token(authorization)
    
    try:
        order_id = _generate_order_id()
        order_items = []
        total_price = 0.0
        
        # Validate and calculate price
        for item in req.items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            
            product = _get_product_or_404(product_id)
            stock = _inventory.get(product_id, 0)
            
            if stock < quantity:
                raise HTTPException(
                    status_code=422,
                    detail=f"Insufficient stock for {product_id}: {stock} available, {quantity} requested"
                )
            
            item_total = product["price"] * quantity
            total_price += item_total
            
            order_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "price": product["price"],
                "subtotal": item_total
            })
            
            # Update inventory
            _inventory[product_id] = stock - quantity
        
        order_entry = {
            "order_id": order_id,
            "customer_name": req.customer_name,
            "items": order_items,
            "total": total_price,
            "shipping_address": req.shipping_address,
            "status": "confirmed",
            "created_at": datetime.utcnow().isoformat()
        }
        
        _orders[order_id] = order_entry
        logger.info(f"🛒 Order created: {order_id} (total: ${total_price:.2f})")
        
        await _archive({
            "op": "ORDER_CREATE",
            "order_id": order_id,
            "customer": req.customer_name,
            "items_count": len(req.items),
            "total": total_price
        })
        
        return {
            "strict": True,
            "order_id": order_id,
            "total": total_price,
            "status": "confirmed",
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Order creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/inventory/update")
async def update_inventory(req: InventoryUpdateRequest, authorization: str = Header(None)):
    """Update product inventory"""
    _validate_token(authorization)
    
    try:
        _get_product_or_404(req.product_id)
        
        current_stock = _inventory.get(req.product_id, 0)
        new_stock = current_stock + req.quantity_change
        
        if new_stock < 0:
            raise HTTPException(
                status_code=422,
                detail=f"Cannot reduce stock below 0. Current: {current_stock}, Change: {req.quantity_change}"
            )
        
        _inventory[req.product_id] = new_stock
        
        logger.info(f"📊 Inventory updated: {req.product_id} ({current_stock} -> {new_stock})")
        
        await _archive({
            "op": "INVENTORY_UPDATE",
            "product_id": req.product_id,
            "change": req.quantity_change,
            "new_stock": new_stock,
            "reason": req.reason
        })
        
        return {
            "strict": True,
            "product_id": req.product_id,
            "previous_stock": current_stock,
            "new_stock": new_stock,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Inventory update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pricing/calculate")
async def calculate_pricing(req: PricingCalculateRequest, authorization: str = Header(None)):
    """Calculate total pricing with discounts"""
    _validate_token(authorization)
    
    try:
        items_breakdown = []
        subtotal = 0.0
        
        for item in req.items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            
            product = _get_product_or_404(product_id)
            item_total = product["price"] * quantity
            
            items_breakdown.append({
                "product_id": product_id,
                "name": product["name"],
                "quantity": quantity,
                "unit_price": product["price"],
                "item_total": item_total
            })
            
            subtotal += item_total
        
        # Apply discount
        discount_info = _apply_discount(subtotal, req.discount_code)
        
        pricing = {
            "items": items_breakdown,
            "subtotal": subtotal,
            "discount_code": req.discount_code or "none",
            "discount_rate": discount_info["discount_rate"],
            "discount_amount": discount_info["discount_amount"],
            "total": discount_info["final_total"],
            "tax": round(discount_info["final_total"] * 0.08, 2),
            "grand_total": round(discount_info["final_total"] * 1.08, 2)
        }
        
        logger.info(f"💰 Pricing calculated: ${pricing['grand_total']:.2f} (discount: {discount_info['discount_rate']*100:.0f}%)")
        
        await _archive({
            "op": "PRICING_CALCULATE",
            "items_count": len(req.items),
            "subtotal": subtotal,
            "total": pricing["grand_total"],
            "discount_code": req.discount_code or "none"
        })
        
        return {
            "strict": True,
            "pricing": pricing,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Pricing calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cart/manage")
async def manage_cart(req: CartManageRequest, authorization: str = Header(None)):
    """Manage shopping cart"""
    _validate_token(authorization)
    
    try:
        if req.action == "add":
            if not req.product_id or not req.quantity:
                raise HTTPException(status_code=422, detail="product_id and quantity required for add")
            
            _get_product_or_404(req.product_id)
            
            if req.cart_id not in _carts:
                _carts[req.cart_id] = {
                    "items": {},
                    "created_at": datetime.utcnow().isoformat()
                }
            
            cart = _carts[req.cart_id]
            if req.product_id in cart["items"]:
                cart["items"][req.product_id]["quantity"] += req.quantity
            else:
                cart["items"][req.product_id] = {"quantity": req.quantity}
            
            logger.info(f"🛒 Item added to cart: {req.cart_id} ({req.product_id} x{req.quantity})")
        
        elif req.action == "remove":
            if not req.product_id:
                raise HTTPException(status_code=422, detail="product_id required for remove")
            
            if req.cart_id in _carts and req.product_id in _carts[req.cart_id]["items"]:
                del _carts[req.cart_id]["items"][req.product_id]
                logger.info(f"🗑️ Item removed from cart: {req.cart_id} ({req.product_id})")
        
        elif req.action == "clear":
            if req.cart_id in _carts:
                _carts[req.cart_id]["items"] = {}
                logger.info(f"🧹 Cart cleared: {req.cart_id}")
        
        else:
            raise HTTPException(status_code=422, detail=f"Unknown action: {req.action}")
        
        cart_data = _carts.get(req.cart_id, {"items": {}})
        
        await _archive({
            "op": "CART_MANAGE",
            "cart_id": req.cart_id,
            "action": req.action,
            "items_count": len(cart_data.get("items", {}))
        })
        
        return {
            "strict": True,
            "cart_id": req.cart_id,
            "action": req.action,
            "items": cart_data.get("items", {}),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Cart management failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)
    
    return {
        "service": "opena15_Shop",
        "version": "1.0.0",
        "port": PORT,
        "products": len(_products),
        "orders": len(_orders),
        "active_carts": len(_carts),
        "endpoints": 6,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    # Pre-populate some products for testing
    prod1_id = _generate_product_id()
    prod2_id = _generate_product_id()
    
    _products[prod1_id] = {
        "name": "Laptop",
        "description": "High-performance laptop",
        "price": 999.99,
        "category": "electronics"
    }
    _inventory[prod1_id] = 10
    
    _products[prod2_id] = {
        "name": "Mouse",
        "description": "Wireless mouse",
        "price": 29.99,
        "category": "accessories"
    }
    _inventory[prod2_id] = 50
    
    logger.info(f"🚀 Starting opena15_Shop on port {PORT}")
    logger.info(f"📦 Pre-loaded {len(_products)} sample products")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
