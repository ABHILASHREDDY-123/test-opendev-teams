"""
Order Service for E-Commerce Platform
Handles shopping cart, order management, and order status tracking with notifications.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from jose import JWTError, jwt
import httpx

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "ecommerce-platform-secret-key-2026")
JWT_ALGORITHM = "HS256"
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8004")

# Security
security = HTTPBearer()

# In-memory stores
carts_db: dict[str, dict] = {}  # {user_id: {items: [{item_id, product_id, quantity, price}], total}}
orders_db: dict[str, list] = {}  # {user_id: [{order_id, items, total, status, created_at}]}

# FastAPI app
app = FastAPI(title="Order Service", version="1.0.0")


# ============================================================================
# Enums
# ============================================================================

class OrderStatus(str, Enum):
    """Order status values"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# ============================================================================
# Pydantic Models
# ============================================================================

class CartItem(BaseModel):
    """Cart item model"""
    item_id: str
    product_id: str
    quantity: int
    price: float


class CartResponse(BaseModel):
    """Cart response model"""
    items: list[CartItem]
    total: float


class AddToCartRequest(BaseModel):
    """Add to cart request"""
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity (must be > 0)")


class OrderItem(BaseModel):
    """Order item model"""
    product_id: str
    quantity: int
    price: float


class OrderResponse(BaseModel):
    """Order response model"""
    order_id: str
    user_id: str
    items: list[OrderItem]
    total: float
    status: str
    created_at: str


class OrderListResponse(BaseModel):
    """Order list response"""
    orders: list[dict]


class OrderStatusUpdate(BaseModel):
    """Order status update request"""
    status: OrderStatus


class OrderStatusResponse(BaseModel):
    """Order status update response"""
    order_id: str
    status: str
    updated_at: str


# ============================================================================
# Utility Functions
# ============================================================================

def decode_jwt_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        ) from e


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to extract and validate JWT from Authorization header"""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    user_id = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role", "customer")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return {
        "user_id": user_id,
        "email": email,
        "role": role
    }


def check_admin(user: dict = Depends(get_current_user)) -> dict:
    """Dependency to check if user is admin"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


async def get_product(product_id: str) -> dict:
    """Get product from product service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PRODUCT_SERVICE_URL}/products/{product_id}",
                timeout=5.0
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product: {str(e)}"
        )


async def reserve_inventory(product_id: str, quantity: int) -> bool:
    """Reserve inventory from product service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PRODUCT_SERVICE_URL}/products/{product_id}/reserve",
                json={"quantity": quantity},
                timeout=5.0
            )
            if response.status_code == 400:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient inventory"
                )
            response.raise_for_status()
            return True
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reserve inventory: {str(e)}"
        )


async def release_inventory(product_id: str, quantity: int) -> bool:
    """Release inventory back to product service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PRODUCT_SERVICE_URL}/products/{product_id}/release",
                json={"quantity": quantity},
                timeout=5.0
            )
            response.raise_for_status()
            return True
    except Exception as e:
        # Log but don't fail - inventory release is best effort
        print(f"Warning: Failed to release inventory: {str(e)}")
        return False


async def send_notification(order_id: str, user_email: str, status: str) -> bool:
    """Send notification webhook to notification service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{NOTIFICATION_SERVICE_URL}/notifications/webhook",
                json={
                    "order_id": order_id,
                    "user_email": user_email,
                    "status": status,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                timeout=5.0
            )
            # Don't fail if notification fails - log and continue
            if response.status_code != 200:
                print(f"Warning: Notification webhook failed with status {response.status_code}")
            return True
    except Exception as e:
        # Log but don't fail - notifications are best effort
        print(f"Warning: Failed to send notification: {str(e)}")
        return True


def get_user_cart(user_id: str) -> dict:
    """Get or create user cart"""
    if user_id not in carts_db:
        carts_db[user_id] = {"items": [], "total": 0.0}
    return carts_db[user_id]


def get_user_orders(user_id: str) -> list:
    """Get user orders"""
    return orders_db.get(user_id, [])


# ============================================================================
# Cart Endpoints
# ============================================================================

@app.post("/cart/add", response_model=CartItem, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    request: AddToCartRequest,
    user: dict = Depends(get_current_user)
) -> CartItem:
    """
    Add product to cart.
    
    - product_id: ID of product to add
    - quantity: Quantity to add (must be > 0)
    
    Validates product exists via product-service.
    Returns added cart item.
    """
    user_id = user["user_id"]
    
    # Validate product exists
    product = await get_product(request.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get user cart
    cart = get_user_cart(user_id)
    
    # Check if product already in cart
    item_id = None
    for item in cart["items"]:
        if item["product_id"] == request.product_id:
            item_id = item["item_id"]
            item["quantity"] += request.quantity
            break
    
    # Add new item if not found
    if not item_id:
        item_id = str(uuid.uuid4())
        cart["items"].append({
            "item_id": item_id,
            "product_id": request.product_id,
            "quantity": request.quantity,
            "price": product["price"]
        })
    
    # Update total
    cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"])
    
    return CartItem(
        item_id=item_id,
        product_id=request.product_id,
        quantity=request.quantity,
        price=product["price"]
    )


@app.get("/cart", response_model=CartResponse)
def get_cart(user: dict = Depends(get_current_user)) -> CartResponse:
    """
    Get current user's cart.
    
    Returns list of cart items and total price.
    """
    user_id = user["user_id"]
    cart = get_user_cart(user_id)
    
    return CartResponse(
        items=[CartItem(**item) for item in cart["items"]],
        total=cart["total"]
    )


@app.delete("/cart/{item_id}", status_code=status.HTTP_200_OK)
def remove_from_cart(
    item_id: str,
    user: dict = Depends(get_current_user)
) -> dict:
    """
    Remove item from cart.
    
    - item_id: ID of cart item to remove
    
    Returns success response.
    """
    user_id = user["user_id"]
    cart = get_user_cart(user_id)
    
    # Find and remove item
    original_count = len(cart["items"])
    cart["items"] = [item for item in cart["items"] if item["item_id"] != item_id]
    
    if len(cart["items"]) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Update total
    cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"])
    
    return {"success": True}


# ============================================================================
# Order Endpoints
# ============================================================================

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(user: dict = Depends(get_current_user)) -> OrderResponse:
    """
    Place order from cart.
    
    Reserves inventory via product-service.
    Clears user's cart.
    Triggers notification webhook.
    
    Returns created order details.
    """
    user_id = user["user_id"]
    user_email = user["email"]
    
    # Get user cart
    cart = get_user_cart(user_id)
    
    if not cart["items"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create order from empty cart"
        )
    
    # Reserve inventory for all items
    reserved_items = []
    try:
        for item in cart["items"]:
            await reserve_inventory(item["product_id"], item["quantity"])
            reserved_items.append(item)
    except HTTPException:
        # Release already reserved items
        for reserved_item in reserved_items:
            await release_inventory(reserved_item["product_id"], reserved_item["quantity"])
        raise
    
    # Create order
    order_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    order_items = [
        OrderItem(
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"]
        )
        for item in cart["items"]
    ]
    
    order = {
        "order_id": order_id,
        "user_id": user_id,
        "items": [item.model_dump() for item in order_items],
        "total": cart["total"],
        "status": OrderStatus.PENDING.value,
        "created_at": now
    }
    
    # Store order
    if user_id not in orders_db:
        orders_db[user_id] = []
    orders_db[user_id].append(order)
    
    # Clear cart
    carts_db[user_id] = {"items": [], "total": 0.0}
    
    # Send notification
    await send_notification(order_id, user_email, OrderStatus.PENDING.value)
    
    return OrderResponse(**order)


@app.get("/orders", response_model=OrderListResponse)
def list_orders(user: dict = Depends(get_current_user)) -> OrderListResponse:
    """
    List user's orders.
    
    Per-user isolation - user sees only their orders.
    
    Returns list of orders with summary info.
    """
    user_id = user["user_id"]
    orders = get_user_orders(user_id)
    
    return OrderListResponse(
        orders=[
            {
                "order_id": order["order_id"],
                "total": order["total"],
                "status": order["status"],
                "created_at": order["created_at"]
            }
            for order in orders
        ]
    )


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    user: dict = Depends(get_current_user)
) -> OrderResponse:
    """
    Get order details.
    
    Per-user isolation - user can only view their own orders.
    
    Returns full order details including items.
    """
    user_id = user["user_id"]
    orders = get_user_orders(user_id)
    
    for order in orders:
        if order["order_id"] == order_id:
            return OrderResponse(**order)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Order not found"
    )


@app.patch("/orders/{order_id}/status", response_model=OrderStatusResponse)
async def update_order_status(
    order_id: str,
    request: OrderStatusUpdate,
    user: dict = Depends(check_admin)
) -> OrderStatusResponse:
    """
    Update order status (admin only).
    
    Triggers notification webhook on status change.
    
    Valid status transitions:
    - pending -> confirmed, cancelled
    - confirmed -> shipped, cancelled
    - shipped -> delivered, cancelled
    - delivered -> (terminal state)
    - cancelled -> (terminal state)
    """
    new_status = request.status.value
    now = datetime.now(timezone.utc).isoformat()
    
    # Find order across all users
    for user_orders in orders_db.values():
        for order in user_orders:
            if order["order_id"] == order_id:
                current_status = order["status"]
                
                # Validate status transition
                valid_transitions = {
                    OrderStatus.PENDING.value: [OrderStatus.CONFIRMED.value, OrderStatus.CANCELLED.value],
                    OrderStatus.CONFIRMED.value: [OrderStatus.SHIPPED.value, OrderStatus.CANCELLED.value],
                    OrderStatus.SHIPPED.value: [OrderStatus.DELIVERED.value, OrderStatus.CANCELLED.value],
                    OrderStatus.DELIVERED.value: [],
                    OrderStatus.CANCELLED.value: []
                }
                
                if new_status not in valid_transitions.get(current_status, []):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot transition from {current_status} to {new_status}"
                    )
                
                # If cancelling, release inventory
                if new_status == OrderStatus.CANCELLED.value and current_status != OrderStatus.CANCELLED.value:
                    for item in order["items"]:
                        await release_inventory(item["product_id"], item["quantity"])
                
                # Update status
                order["status"] = new_status
                
                # Send notification
                await send_notification(order_id, order["user_id"], new_status)
                
                return OrderStatusResponse(
                    order_id=order_id,
                    status=new_status,
                    updated_at=now
                )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Order not found"
    )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
