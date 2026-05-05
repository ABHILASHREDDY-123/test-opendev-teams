"""
Product Service - Catalog and Inventory Management

This service manages the product catalog and inventory for the e-commerce platform.
It provides public endpoints for browsing products and admin endpoints for managing inventory.
"""

import os
import uuid
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from jose import JWTError, jwt

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "ecommerce-platform-secret-key-2026")
PORT = int(os.getenv("PORT", 8002))

# Initialize FastAPI app
app = FastAPI(title="Product Service", version="1.0.0")

# ============================================================================
# Pydantic Models
# ============================================================================


class ProductCreate(BaseModel):
    """Request model for creating a product."""
    name: str = Field(..., min_length=1, description="Product name")
    description: str = Field(..., min_length=1, description="Product description")
    price: float = Field(..., gt=0, description="Product price")
    inventory_count: int = Field(..., ge=0, description="Initial inventory count")
    category: str = Field(..., min_length=1, description="Product category")


class ProductUpdate(BaseModel):
    """Request model for updating a product."""
    name: Optional[str] = Field(None, min_length=1, description="Product name")
    description: Optional[str] = Field(None, min_length=1, description="Product description")
    price: Optional[float] = Field(None, gt=0, description="Product price")
    inventory_count: Optional[int] = Field(None, ge=0, description="Inventory count")
    category: Optional[str] = Field(None, min_length=1, description="Product category")


class Product(BaseModel):
    """Response model for a product."""
    id: str = Field(..., description="Product ID (UUID)")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    price: float = Field(..., description="Product price")
    inventory_count: int = Field(..., description="Current inventory count")
    category: str = Field(..., description="Product category")


class ProductListResponse(BaseModel):
    """Response model for product list."""
    products: List[Product]


class InventoryRequest(BaseModel):
    """Request model for inventory operations (reserve/release)."""
    quantity: int = Field(..., gt=0, description="Quantity to reserve or release")


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user_id
    email: str
    role: str
    exp: int


# ============================================================================
# In-Memory Data Store
# ============================================================================

# Store products in memory: {product_id: product_dict}
products_db: dict = {}


# ============================================================================
# JWT Validation
# ============================================================================


def verify_jwt_token(authorization: Optional[str] = Header(None)) -> TokenPayload:
    """
    Verify JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")
        
    Returns:
        TokenPayload with decoded token data
        
    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        # Extract token from "Bearer <token>" format
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        # Verify token is not expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token has expired")
        
        return TokenPayload(
            sub=payload.get("sub"),
            email=payload.get("email"),
            role=payload.get("role"),
            exp=exp
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_admin(token: TokenPayload = Depends(verify_jwt_token)) -> TokenPayload:
    """
    Verify that the user has admin role.
    
    Args:
        token: Decoded JWT token
        
    Returns:
        TokenPayload if user is admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if token.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return token


# ============================================================================
# Public Endpoints
# ============================================================================


@app.get("/products", response_model=ProductListResponse)
def list_products():
    """
    List all products.
    
    Returns:
        List of all products in the catalog
    """
    products_list = [Product(**product) for product in products_db.values()]
    return ProductListResponse(products=products_list)


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    """
    Get a single product by ID.
    
    Args:
        product_id: Product ID (UUID)
        
    Returns:
        Product details
        
    Raises:
        HTTPException: 404 if product not found
    """
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return Product(**products_db[product_id])


# ============================================================================
# Admin Endpoints
# ============================================================================


@app.post("/products", response_model=Product, status_code=201)
def create_product(
    product_data: ProductCreate,
    token: TokenPayload = Depends(verify_admin)
):
    """
    Create a new product (admin only).
    
    Args:
        product_data: Product creation data
        token: Verified admin JWT token
        
    Returns:
        Created product with generated ID
        
    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin
    """
    product_id = str(uuid.uuid4())
    
    product = {
        "id": product_id,
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "inventory_count": product_data.inventory_count,
        "category": product_data.category,
    }
    
    products_db[product_id] = product
    return Product(**product)


@app.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: str,
    product_data: ProductUpdate,
    token: TokenPayload = Depends(verify_admin)
):
    """
    Update an existing product (admin only).
    
    Args:
        product_id: Product ID to update
        product_data: Updated product data
        token: Verified admin JWT token
        
    Returns:
        Updated product
        
    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin, 404 if not found
    """
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products_db[product_id]
    
    # Update only provided fields
    if product_data.name is not None:
        product["name"] = product_data.name
    if product_data.description is not None:
        product["description"] = product_data.description
    if product_data.price is not None:
        product["price"] = product_data.price
    if product_data.inventory_count is not None:
        product["inventory_count"] = product_data.inventory_count
    if product_data.category is not None:
        product["category"] = product_data.category
    
    return Product(**product)


@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: str,
    token: TokenPayload = Depends(verify_admin)
):
    """
    Delete a product (admin only).
    
    Args:
        product_id: Product ID to delete
        token: Verified admin JWT token
        
    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin, 404 if not found
    """
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    del products_db[product_id]


# ============================================================================
# Internal Endpoints (for order-service)
# ============================================================================


@app.post("/products/{product_id}/reserve", response_model=Product)
def reserve_inventory(product_id: str, request: InventoryRequest):
    """
    Reserve (decrement) inventory for a product.
    
    Called by order-service when placing an order.
    
    Args:
        product_id: Product ID
        request: Inventory request with quantity to reserve
        
    Returns:
        Updated product with new inventory count
        
    Raises:
        HTTPException: 400 if insufficient inventory, 404 if product not found
    """
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products_db[product_id]
    
    if product["inventory_count"] < request.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient inventory. Available: {product['inventory_count']}, Requested: {request.quantity}"
        )
    
    product["inventory_count"] -= request.quantity
    return Product(**product)


@app.post("/products/{product_id}/release", response_model=Product)
def release_inventory(product_id: str, request: InventoryRequest):
    """
    Release (increment) inventory for a product.
    
    Called by order-service when cancelling an order.
    
    Args:
        product_id: Product ID
        request: Inventory request with quantity to release
        
    Returns:
        Updated product with new inventory count
        
    Raises:
        HTTPException: 404 if product not found
    """
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products_db[product_id]
    product["inventory_count"] += request.quantity
    
    return Product(**product)


# ============================================================================
# Health Check
# ============================================================================


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "product-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
