import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from jose import jwt, JWTError

# Environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "ecommerce-platform-secret-key-2026")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8004")

app = FastAPI(title="Order Service", version="1.0.0")

# ==================== Models ====================

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class CartItem(BaseModel):
    product_id: str
    quantity: int
    price: float


class CartResponse(BaseModel):
    user_id: str
    items: List[CartItem]
    total: float


class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float


class OrderRequest(BaseModel):
    pass  # Cart items are taken from user's cart


class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    items: List[OrderItem]
    total: float
    status: OrderStatus
    created_at: str
    updated_at: str


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# ==================== In-Memory Store ====================

# Structure: {user_id: {item_id: CartItem}}
carts: Dict[str, Dict[str, CartItem]] = {}

# Structure: {order_id: OrderResponse}
orders: Dict[str, OrderResponse] = {}

# Counter for order IDs
order_counter = 0


# ==================== Auth & JWT ====================

def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """Verify JWT token and return user_id."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")


def verify_admin_token(authorization: Optional[str] = Header(None)) -> str:
    """Verify JWT token and check admin role."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        role = payload.get("role", "user")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
        
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")


# ==================== Helper Functions ====================

def get_user_cart(user_id: str) -> Dict[str, CartItem]:
    """Get or create user's cart."""
    if user_id not in carts:
        carts[user_id] = {}
    return carts[user_id]


def calculate_cart_total(cart: Dict[str, CartItem]) -> float:
    """Calculate total price of cart."""
    return sum(item.price * item.quantity for item in cart.values())


async def verify_product_exists(product_id: str) -> Dict[str, Any]:
    """Verify product exists via product-service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PRODUCT_SERVICE_URL}/products/{product_id}",
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Product service unavailable")


async def reserve_product(product_id: str, quantity: int) -> bool:
    """Reserve inventory via product-service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PRODUCT_SERVICE_URL}/products/{product_id}/reserve",
                json={"quantity": quantity},
                timeout=5.0
            )
            return response.status_code == 200
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Product service unavailable")


async def release_product(product_id: str, quantity: int) -> bool:
    """Release inventory via product-service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PRODUCT_SERVICE_URL}/products/{product_id}/release",
                json={"quantity": quantity},
                timeout=5.0
            )
            return response.status_code == 200
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Product service unavailable")


async def send_notification(order_id: str, user_email: str, status: OrderStatus) -> bool:
    """Send notification via notification-service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{NOTIFICATION_SERVICE_URL}/notifications/webhook",
                json={
                    "order_id": order_id,
                    "user_email": user_email,
                    "status": status.value,
                    "timestamp": datetime.utcnow().isoformat()
                },
                timeout=5.0
            )
            return response.status_code in [200, 201]
    except httpx.RequestError:
        # Don't fail the order if notification fails
        return False


# ==================== Cart Endpoints ====================

@app.post("/cart/add")
async def add_to_cart(
    item: CartItem,
    user_id: str = Depends(verify_token)
) -> CartResponse:
    """Add product to cart."""
    # Verify product exists
    await verify_product_exists(item.product_id)
    
    # Get user's cart
    cart = get_user_cart(user_id)
    
    # Add or update item
    if item.product_id in cart:
        cart[item.product_id].quantity += item.quantity
    else:
        cart[item.product_id] = item
    
    # Return updated cart
    total = calculate_cart_total(cart)
    return CartResponse(
        user_id=user_id,
        items=list(cart.values()),
        total=total
    )


@app.get("/cart")
async def get_cart(user_id: str = Depends(verify_token)) -> CartResponse:
    """Get current user's cart."""
    cart = get_user_cart(user_id)
    total = calculate_cart_total(cart)
    return CartResponse(
        user_id=user_id,
        items=list(cart.values()),
        total=total
    )


@app.delete("/cart/{item_id}")
async def remove_from_cart(item_id: str, user_id: str = Depends(verify_token)) -> CartResponse:
    """Remove item from cart."""
    cart = get_user_cart(user_id)
    
    if item_id not in cart:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    del cart[item_id]
    
    total = calculate_cart_total(cart)
    return CartResponse(
        user_id=user_id,
        items=list(cart.values()),
        total=total
    )


# ==================== Order Endpoints ====================

@app.post("/orders")
async def place_order(
    user_id: str = Depends(verify_token)
) -> OrderResponse:
    """Place order from cart."""
    global order_counter
    
    cart = get_user_cart(user_id)
    
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Reserve inventory for all items
    reserved_items = []
    try:
        for product_id, item in cart.items():
            reserved = await reserve_product(product_id, item.quantity)
            if not reserved:
                raise HTTPException(status_code=400, detail=f"Cannot reserve product {product_id}")
            reserved_items.append((product_id, item.quantity))
    except HTTPException:
        # Release already reserved items on failure
        for product_id, quantity in reserved_items:
            try:
                await release_product(product_id, quantity)
            except:
                pass
        raise
    
    # Create order
    order_counter += 1
    order_id = f"ORD-{order_counter:06d}"
    total = calculate_cart_total(cart)
    now = datetime.utcnow().isoformat()
    
    # Convert CartItems to OrderItems
    order_items = [
        OrderItem(product_id=item.product_id, quantity=item.quantity, price=item.price)
        for item in cart.values()
    ]
    
    order = OrderResponse(
        order_id=order_id,
        user_id=user_id,
        items=order_items,
        total=total,
        status=OrderStatus.PENDING,
        created_at=now,
        updated_at=now
    )
    
    orders[order_id] = order
    
    # Clear cart
    carts[user_id] = {}
    
    return order


@app.get("/orders")
async def list_orders(user_id: str = Depends(verify_token)) -> List[OrderResponse]:
    """List user's orders."""
    user_orders = [order for order in orders.values() if order.user_id == user_id]
    return user_orders


@app.get("/orders/{order_id}")
async def get_order(order_id: str, user_id: str = Depends(verify_token)) -> OrderResponse:
    """Get order details."""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders[order_id]
    
    # Ensure user can only see their own orders
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return order


@app.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    admin_id: str = Depends(verify_admin_token)
) -> OrderResponse:
    """Update order status (admin only)."""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders[order_id]
    old_status = order.status
    order.status = status_update.status
    order.updated_at = datetime.utcnow().isoformat()
    
    # If cancelling, release inventory
    if status_update.status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
        for item in order.items:
            try:
                await release_product(item.product_id, item.quantity)
            except:
                pass
    
    # Send notification (best effort, don't fail if it doesn't work)
    # For now, we'll use a placeholder email (in real scenario, we'd get it from auth service)
    user_email = f"{order.user_id}@example.com"
    try:
        await send_notification(order_id, user_email, order.status)
    except:
        pass
    
    return order


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "order-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
