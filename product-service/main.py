import os
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status, Header
from pydantic import BaseModel, Field
from jose import JWTError, jwt
import uuid

# Environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "ecommerce-platform-secret-key-2026")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")

app = FastAPI(title="Product Service", version="1.0.0")

# ============================================================================
# Data Models
# ============================================================================

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    inventory_count: int
    category: str

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    inventory_count: int
    category: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    inventory_count: Optional[int] = None
    category: Optional[str] = None

class ReserveRequest(BaseModel):
    quantity: int

class ReleaseRequest(BaseModel):
    quantity: int

class TokenPayload(BaseModel):
    sub: str
    email: str
    role: str
    exp: int

# ============================================================================
# In-Memory Data Store
# ============================================================================

products_store: dict[str, Product] = {}

# ============================================================================
# JWT Validation
# ============================================================================

def verify_token(token: str) -> TokenPayload:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.get_unverified_claims(token)
        sub: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        exp: int = payload.get("exp")
        
        if sub is None or email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims"
            )
        
        # Check expiration
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        
        return TokenPayload(sub=sub, email=email, role=role, exp=exp)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(authorization: Optional[str] = Header(None)) -> TokenPayload:
    """Extract and verify JWT from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = parts[1]
    return verify_token(token)

def require_admin(authorization: Optional[str] = Header(None)) -> TokenPayload:
    """Require admin role."""
    user = get_current_user(authorization)
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return user

# ============================================================================
# Public Endpoints (No Auth Required)
# ============================================================================

@app.get("/products", response_model=List[Product])
def list_products():
    """List all products (public endpoint)."""
    return list(products_store.values())

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    """Get a single product by ID."""
    if product_id not in products_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    return products_store[product_id]

# ============================================================================
# Admin Endpoints (Require JWT with role=admin)
# ============================================================================

@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    user: TokenPayload = Depends(require_admin)
):
    """Create a new product (admin only)."""
    
    # Validate input
    if not product.name or not product.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product name cannot be empty"
        )
    if product.price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price cannot be negative"
        )
    if product.inventory_count < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory count cannot be negative"
        )
    
    product_id = str(uuid.uuid4())
    new_product = Product(
        id=product_id,
        name=product.name,
        description=product.description,
        price=product.price,
        inventory_count=product.inventory_count,
        category=product.category
    )
    products_store[product_id] = new_product
    return new_product

@app.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: str,
    product_update: ProductUpdate,
    user: TokenPayload = Depends(require_admin)
):
    """Update a product (admin only)."""
    
    if product_id not in products_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    
    existing_product = products_store[product_id]
    
    # Validate updates
    if product_update.price is not None and product_update.price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price cannot be negative"
        )
    if product_update.inventory_count is not None and product_update.inventory_count < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory count cannot be negative"
        )
    
    # Update fields using Pydantic v2 model_copy
    update_data = product_update.model_dump(exclude_unset=True)
    updated_product = existing_product.model_copy(update={**update_data})
    products_store[product_id] = updated_product
    return updated_product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    user: TokenPayload = Depends(require_admin)
):
    """Delete a product (admin only)."""
    
    if product_id not in products_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    
    del products_store[product_id]
    return None

# ============================================================================
# Inventory Management Endpoints (Called by Order Service)
# ============================================================================

@app.post("/products/{product_id}/reserve", response_model=Product)
def reserve_inventory(
    product_id: str,
    reserve_request: ReserveRequest
):
    """Reserve (decrement) inventory for a product."""
    if product_id not in products_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    
    if reserve_request.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be positive"
        )
    
    product = products_store[product_id]
    if product.inventory_count < reserve_request.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient inventory. Available: {product.inventory_count}, Requested: {reserve_request.quantity}"
        )
    
    # Decrement inventory
    product.inventory_count -= reserve_request.quantity
    products_store[product_id] = product
    return product

@app.post("/products/{product_id}/release", response_model=Product)
def release_inventory(
    product_id: str,
    release_request: ReleaseRequest
):
    """Release (increment) inventory for a product."""
    if product_id not in products_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    
    if release_request.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be positive"
        )
    
    product = products_store[product_id]
    product.inventory_count += release_request.quantity
    products_store[product_id] = product
    return product

# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "product-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
