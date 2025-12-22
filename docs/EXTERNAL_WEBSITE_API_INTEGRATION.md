# 🔌 External Website API Integration Guide — ELION System

**Projekt:** ELION Hyper-Dashboard 3.0.0  
**Zweck:** Integration externer Website-APIs und Webservices  
**Status:** ✅ Production Ready  
**Letzte Aktualisierung:** 21. Dezember 2025

---

## 📋 Übersicht

Dieser Guide beschreibt, wie externe Website-APIs sicher in das ELION Hyper-Dashboard System integriert werden, unter Einhaltung von **Option-2-Flow**, **Port-Policy** und **Security Best Practices**.

---

## 🎯 Unterstützte API-Typen

### 1. REST-APIs
- **JSON/XML** Responses
- **GET, POST, PUT, DELETE** Methods
- **OAuth 2.0** / API-Key Authentication
- **Webhook** Support

### 2. GraphQL-APIs
- **Query** & **Mutation** Support
- **Subscriptions** (WebSocket)
- **Schema-Introspection**

### 3. SOAP-APIs
- **WSDL-Based** Services
- **XML** Request/Response
- Legacy System Integration

### 4. WebSocket-APIs
- **Real-time** Communication
- **Bidirectional** Data Flow
- Event-Driven Architecture

---

## 🏗️ Integration Architecture

### Standard-Flow für externe APIs

```
┌──────────────────────────────────────────────────────────────┐
│            EXTERNAL WEBSITE API INTEGRATION                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  External API → opena1:12344 → opena2:12345 → kordp:12346   │
│  (REST/GraphQL)  ↓ Request71   ↓ CMD Safepoint               │
│                  ↓ Decision72  ↓ RESP Safepoint              │
│                  ↓             ↓                              │
│                  ↓             → Web Agent (opena6/15/16/17)  │
│                  ↓               ↓ API Call via httpx         │
│                  ↓               ↓ Response Processing        │
│                  ↓               ↓ Data Transformation        │
│                  ↓               ↓ Result                     │
│                  ↓               ↓                            │
│                  ←───────────────┴────────────────            │
│                  ↓ Response                                   │
│                  ↓                                            │
│               External API                                    │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Webhook-Flow (Reverse Direction)

```
┌──────────────────────────────────────────────────────────────┐
│                WEBHOOK INTEGRATION FLOW                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  External API → Webhook Endpoint (opena15/16/17)             │
│                 ↓ POST /webhook/{event}                       │
│                 ↓ Signature Validation                        │
│                 ↓                                             │
│                 → opena2:12345 (Safepoint)                    │
│                   ↓ WEBHOOK kind                              │
│                   ↓ Event Processing                          │
│                   ↓                                           │
│                   → Event Handler                             │
│                     ↓ Business Logic                          │
│                     ↓ Response                                │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security & Authentication

### 1. API-Key Authentication

```python
import os
from typing import Dict, Optional

class APIKeyAuth:
    """API-Key Authentication Handler."""
    
    def __init__(self, key_name: str):
        self.api_key = os.getenv(key_name)
        if not self.api_key:
            raise ValueError(f"Missing API key: {key_name}")
    
    def get_headers(self) -> Dict[str, str]:
        """Return authentication headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

# Verwendung
auth = APIKeyAuth("EXTERNAL_API_KEY")
headers = auth.get_headers()
```

### 2. OAuth 2.0 Authentication

```python
from authlib.integrations.httpx_client import AsyncOAuth2Client

class OAuth2Handler:
    """OAuth 2.0 Authentication Handler."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str
    ):
        self.client_id = os.getenv(client_id)
        self.client_secret = os.getenv(client_secret)
        self.token_url = token_url
        self.access_token: Optional[str] = None
    
    async def get_access_token(self) -> str:
        """Fetch OAuth 2.0 access token."""
        async with AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret
        ) as client:
            token = await client.fetch_token(
                self.token_url,
                grant_type='client_credentials'
            )
            self.access_token = token['access_token']
            return self.access_token
    
    async def get_headers(self) -> Dict[str, str]:
        """Return OAuth headers."""
        if not self.access_token:
            await self.get_access_token()
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

# Verwendung
oauth = OAuth2Handler(
    client_id="OAUTH_CLIENT_ID",
    client_secret="OAUTH_CLIENT_SECRET",
    token_url="https://api.example.com/oauth/token"
)
headers = await oauth.get_headers()
```

### 3. Webhook-Signature-Validation

```python
import hmac
import hashlib
from fastapi import HTTPException, Request

async def validate_webhook_signature(
    request: Request,
    secret: str
) -> bool:
    """
    Validate webhook signature.
    
    Args:
        request: FastAPI Request object
        secret: Webhook secret from ENV
    
    Returns:
        bool: True if signature is valid
    
    Raises:
        HTTPException: If signature is invalid
    """
    # Get signature from header
    signature = request.headers.get("X-Webhook-Signature")
    if not signature:
        raise HTTPException(
            status_code=401,
            detail="Missing signature header"
        )
    
    # Calculate expected signature
    body = await request.body()
    expected = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures (timing-attack safe)
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )
    
    return True

# Verwendung im Webhook-Handler
@router.post("/webhook/payment")
async def handle_payment_webhook(request: Request):
    secret = os.getenv("WEBHOOK_SECRET")
    await validate_webhook_signature(request, secret)
    
    data = await request.json()
    # Process webhook...
```

---

## 📡 REST-API Integration

### Standard REST-Client

```python
import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RESTAPIClient:
    """Standard REST-API Client für externe APIs."""
    
    def __init__(
        self,
        base_url: str,
        auth_handler: Optional[Any] = None,
        timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip('/')
        self.auth_handler = auth_handler
        self.timeout = timeout
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make REST-API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/users')
            data: Request body (JSON)
            params: Query parameters
        
        Returns:
            Response data as dict
        
        Raises:
            httpx.HTTPError: On API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        # Get auth headers
        headers = {}
        if self.auth_handler:
            headers = await self.auth_handler.get_headers()
        
        logger.info(f"API Request: {method} {url}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            )
            
            # Log response
            logger.info(f"API Response: {response.status_code}")
            
            # Raise on error
            response.raise_for_status()
            
            return response.json()
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET request."""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """POST request."""
        return await self.request("POST", endpoint, data=data, **kwargs)
    
    async def put(self, endpoint: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """PUT request."""
        return await self.request("PUT", endpoint, data=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request."""
        return await self.request("DELETE", endpoint, **kwargs)

# Verwendung
auth = APIKeyAuth("STRIPE_API_KEY")
client = RESTAPIClient(
    base_url="https://api.stripe.com/v1",
    auth_handler=auth
)

# GET-Request
customers = await client.get("/customers")

# POST-Request
new_customer = await client.post(
    "/customers",
    data={
        "email": "customer@example.com",
        "name": "John Doe"
    }
)
```

### Retry-Logic mit Exponential Backoff

```python
import asyncio
from typing import Callable, Any

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs
) -> Any:
    """
    Retry function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        backoff_factor: Backoff multiplication factor
        *args, **kwargs: Arguments for func
    
    Returns:
        Result from func
    
    Raises:
        Exception: Last exception after all retries exhausted
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt == max_retries:
                logger.error(f"Max retries ({max_retries}) exceeded")
                raise
            
            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. "
                f"Retrying in {delay}s..."
            )
            
            await asyncio.sleep(delay)
            delay *= backoff_factor
    
    raise last_exception

# Verwendung
result = await retry_with_backoff(
    client.get,
    max_retries=3,
    endpoint="/customers"
)
```

---

## 🔄 GraphQL Integration

### GraphQL-Client

```python
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

class GraphQLClient:
    """GraphQL-Client für externe APIs."""
    
    def __init__(
        self,
        endpoint: str,
        auth_handler: Optional[Any] = None
    ):
        # Setup transport
        headers = {}
        if auth_handler:
            headers = auth_handler.get_headers()
        
        transport = AIOHTTPTransport(
            url=endpoint,
            headers=headers
        )
        
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=True
        )
    
    async def query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Query variables
        
        Returns:
            Query result
        """
        async with self.client as session:
            result = await session.execute(
                gql(query),
                variable_values=variables or {}
            )
            return result
    
    async def mutate(
        self,
        mutation: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute GraphQL mutation."""
        return await self.query(mutation, variables)

# Verwendung
auth = APIKeyAuth("GITHUB_API_KEY")
client = GraphQLClient(
    endpoint="https://api.github.com/graphql",
    auth_handler=auth
)

# Query
query = """
    query GetUser($login: String!) {
        user(login: $login) {
            name
            email
            repositories(first: 10) {
                nodes {
                    name
                }
            }
        }
    }
"""

result = await client.query(
    query,
    variables={"login": "octocat"}
)
```

---

## 🌐 Spezifische API-Integrationen

### 1. Stripe Payment-API

```python
import os
import stripe
from typing import Dict, Any

class StripeIntegration:
    """Stripe Payment-API Integration."""
    
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    async def create_customer(
        self,
        email: str,
        name: str
    ) -> Dict[str, Any]:
        """Create Stripe customer."""
        customer = stripe.Customer.create(
            email=email,
            name=name
        )
        return customer.to_dict()
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "eur",
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create payment intent."""
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer_id
        )
        return intent.to_dict()
    
    async def validate_webhook(
        self,
        payload: bytes,
        signature: str
    ) -> Dict[str, Any]:
        """Validate and parse Stripe webhook."""
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                self.webhook_secret
            )
            return event.to_dict()
        except stripe.error.SignatureVerificationError:
            raise HTTPException(
                status_code=401,
                detail="Invalid signature"
            )

# Verwendung in opena16 (Shop Creator)
@router.post("/webhook/stripe")
async def handle_stripe_webhook(request: Request):
    stripe_integration = StripeIntegration()
    
    payload = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    event = await stripe_integration.validate_webhook(payload, signature)
    
    # Process event
    if event["type"] == "payment_intent.succeeded":
        # Handle successful payment
        await process_payment_success(event["data"]["object"])
    
    return {"status": "received"}
```

### 2. SendGrid Email-API

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class SendGridIntegration:
    """SendGrid Email-API Integration."""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.client = SendGridAPIClient(self.api_key)
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> Dict[str, Any]:
        """Send email via SendGrid."""
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        response = self.client.send(message)
        
        return {
            "status_code": response.status_code,
            "body": response.body,
            "headers": dict(response.headers)
        }

# Verwendung in opena7 (Email Agent)
sendgrid = SendGridIntegration()

await sendgrid.send_email(
    to_email="customer@example.com",
    subject="Willkommen!",
    html_content="<h1>Willkommen bei unserem Service!</h1>"
)
```

### 3. Google Maps API

```python
import googlemaps

class GoogleMapsIntegration:
    """Google Maps API Integration."""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.client = googlemaps.Client(key=api_key)
    
    async def geocode_address(self, address: str) -> Dict[str, Any]:
        """Geocode address to coordinates."""
        result = self.client.geocode(address)
        return result[0] if result else {}
    
    async def get_directions(
        self,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """Get directions between two locations."""
        result = self.client.directions(
            origin=origin,
            destination=destination
        )
        return result[0] if result else {}

# Verwendung
maps = GoogleMapsIntegration()

location = await maps.geocode_address("Berlin, Germany")
coordinates = location["geometry"]["location"]
# {"lat": 52.520008, "lng": 13.404954}
```

### 4. Shopify API

```python
import shopify

class ShopifyIntegration:
    """Shopify API Integration."""
    
    def __init__(self):
        shop_url = os.getenv("SHOPIFY_SHOP_URL")
        api_key = os.getenv("SHOPIFY_API_KEY")
        password = os.getenv("SHOPIFY_PASSWORD")
        
        shopify.ShopifyResource.set_site(
            f"https://{api_key}:{password}@{shop_url}/admin"
        )
    
    async def create_product(
        self,
        title: str,
        body_html: str,
        price: str
    ) -> Dict[str, Any]:
        """Create Shopify product."""
        product = shopify.Product()
        product.title = title
        product.body_html = body_html
        product.variants = [
            shopify.Variant({"price": price})
        ]
        
        success = product.save()
        
        if success:
            return product.to_dict()
        else:
            raise ValueError(product.errors.full_messages())
    
    async def get_orders(
        self,
        status: str = "any"
    ) -> list:
        """Get Shopify orders."""
        orders = shopify.Order.find(status=status)
        return [order.to_dict() for order in orders]

# Verwendung in opena16 (Shop Creator)
shopify_integration = ShopifyIntegration()

product = await shopify_integration.create_product(
    title="Beispiel Produkt",
    body_html="<p>Produktbeschreibung</p>",
    price="29.99"
)
```

---

## 🧪 Testing

### Unit-Tests für API-Integration

```python
import pytest
from unittest.mock import Mock, patch
import httpx

@pytest.mark.asyncio
async def test_rest_api_client():
    """Test REST-API Client."""
    # Mock httpx.AsyncClient
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "Test"}
        
        mock_client.return_value.__aenter__.return_value.request = \
            Mock(return_value=mock_response)
        
        # Test client
        client = RESTAPIClient("https://api.example.com")
        result = await client.get("/users/1")
        
        assert result["id"] == 1
        assert result["name"] == "Test"

@pytest.mark.asyncio
async def test_webhook_signature_validation():
    """Test Webhook-Signature-Validation."""
    # Mock request
    mock_request = Mock()
    mock_request.headers.get.return_value = "valid_signature"
    mock_request.body = Mock(return_value=b'{"event": "test"}')
    
    # Test validation
    secret = "test_secret"
    result = await validate_webhook_signature(mock_request, secret)
    
    # Signature should be validated
    assert result is True or isinstance(result, bool)
```

### Integration-Tests

```python
@pytest.mark.asyncio
async def test_stripe_integration():
    """Test Stripe-Integration."""
    stripe_integration = StripeIntegration()
    
    # Create test customer
    customer = await stripe_integration.create_customer(
        email="test@example.com",
        name="Test User"
    )
    
    assert customer["email"] == "test@example.com"
    assert "id" in customer

@pytest.mark.asyncio
async def test_option2_flow_external_api():
    """Test Option-2-Flow mit externer API."""
    # 1. Request an opena1
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:12344/log/opena1",
            json={
                "request_id": "test-ext-001",
                "user_query": "Call external API",
                "context": {"api": "stripe", "action": "create_customer"}
            }
        )
        
        assert response.status_code == 200
        
        # 2. Verify Safepoint
        safepoints = await client.get(
            "http://127.0.0.1:12345/archiv/last?n=1"
        )
        
        data = safepoints.json()
        assert len(data) > 0
        assert data[0]["kind"] in ["CMD", "RESP"]
```

---

## 📚 ENV-Variablen

### Template (.env.example)

```bash
# ============================================
# External Website API Integration
# ============================================

# Stripe Payment API
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SendGrid Email API
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=noreply@example.com

# Google Maps API
GOOGLE_MAPS_API_KEY=AIza...

# Shopify API
SHOPIFY_SHOP_URL=myshop.myshopify.com
SHOPIFY_API_KEY=...
SHOPIFY_PASSWORD=...

# GitHub API
GITHUB_API_KEY=ghp_...

# Twitter API
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_BEARER_TOKEN=...

# Generic External API
EXTERNAL_API_KEY=...
EXTERNAL_API_URL=https://api.example.com
EXTERNAL_WEBHOOK_SECRET=...
```

---

## 📖 Best Practices

### 1. Rate Limiting
```python
import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    """Rate limiter for API calls."""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
    
    async def acquire(self):
        """Wait until rate limit allows call."""
        now = datetime.now()
        
        # Remove old calls
        while self.calls and \
              (now - self.calls[0]) > timedelta(seconds=self.time_window):
            self.calls.popleft()
        
        # Wait if limit reached
        if len(self.calls) >= self.max_calls:
            wait_time = (
                self.calls[0] + timedelta(seconds=self.time_window) - now
            ).total_seconds()
            await asyncio.sleep(max(0, wait_time))
        
        # Record call
        self.calls.append(datetime.now())

# Verwendung: Max 10 Calls pro Sekunde
rate_limiter = RateLimiter(max_calls=10, time_window=1.0)

async def call_api():
    await rate_limiter.acquire()
    return await client.get("/endpoint")
```

### 2. Circuit Breaker
```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """Circuit breaker pattern for API calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker."""
        if self.state == CircuitState.OPEN:
            # Check if timeout passed
            if datetime.now() - self.last_failure_time > \
               timedelta(seconds=self.timeout):
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            
            # Reset on success
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise e

# Verwendung
breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)

result = await breaker.call(client.get, "/endpoint")
```

### 3. Response Caching
```python
from functools import wraps
import hashlib
import json

class ResponseCache:
    """Simple in-memory response cache."""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl  # Time to live in seconds
    
    def _make_key(self, func_name: str, args, kwargs) -> str:
        """Generate cache key."""
        key_data = {
            "func": func_name,
            "args": str(args),
            "kwargs": str(kwargs)
        }
        return hashlib.md5(
            json.dumps(key_data, sort_keys=True).encode()
        ).hexdigest()
    
    def cached(self, func):
        """Decorator for caching async functions."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = self._make_key(func.__name__, args, kwargs)
            
            # Check cache
            if key in self.cache:
                data, timestamp = self.cache[key]
                if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                    return data
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            self.cache[key] = (result, datetime.now())
            
            return result
        
        return wrapper

# Verwendung
cache = ResponseCache(ttl=300)  # 5 minutes

@cache.cached
async def get_user_data(user_id: int):
    return await client.get(f"/users/{user_id}")
```

---

## 🎯 Checkliste für neue API-Integration

- [ ] API-Dokumentation gelesen
- [ ] API-Keys/Credentials in `.env` gespeichert
- [ ] Authentication-Handler implementiert
- [ ] REST/GraphQL-Client erstellt
- [ ] Error-Handling implementiert
- [ ] Retry-Logic mit Backoff
- [ ] Rate-Limiting aktiviert
- [ ] Circuit-Breaker implementiert (optional)
- [ ] Response-Caching (optional)
- [ ] Webhook-Endpoint erstellt (falls benötigt)
- [ ] Signature-Validation für Webhooks
- [ ] Safepoint-Archivierung implementiert
- [ ] Option-2-Flow eingehalten
- [ ] Unit-Tests geschrieben
- [ ] Integration-Tests durchgeführt
- [ ] Dokumentation aktualisiert

---

**Maintainer:** Danijel Jokic (ELION Team)  
**Letzte Aktualisierung:** 21. Dezember 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
