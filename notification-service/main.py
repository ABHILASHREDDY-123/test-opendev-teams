"""
Notification Service for E-Commerce Platform
Handles order event webhooks and notification management.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from jose import JWTError, jwt

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "ecommerce-platform-secret-key-2026")
JWT_ALGORITHM = "HS256"

# Security
security = HTTPBearer()

# In-memory stores
notifications_db: dict[str, list] = {}  # {user_id: [{id, order_id, status, timestamp, read}]}

# FastAPI app
app = FastAPI(title="Notification Service", version="1.0.0")


# ============================================================================
# Pydantic Models
# ============================================================================

class WebhookPayload(BaseModel):
    """Webhook payload from order service"""
    order_id: str = Field(..., description="Order ID")
    user_email: str = Field(..., description="User email")
    status: str = Field(..., description="Order status")
    timestamp: str = Field(..., description="Event timestamp")


class NotificationResponse(BaseModel):
    """Notification response model"""
    id: str
    order_id: str
    user_email: str
    status: str
    timestamp: str
    read: bool


class NotificationListResponse(BaseModel):
    """Notification list response"""
    notifications: list[NotificationResponse]


class UnreadCountResponse(BaseModel):
    """Unread count response"""
    unread_count: int


class ReadStatusResponse(BaseModel):
    """Read status update response"""
    id: str
    read: bool
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
    
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return {
        "user_id": user_id,
        "email": email
    }


def get_user_notifications(user_email: str) -> list:
    """Get or create user notifications list"""
    if user_email not in notifications_db:
        notifications_db[user_email] = []
    return notifications_db[user_email]


# ============================================================================
# Webhook Endpoint
# ============================================================================

@app.post("/notifications/webhook", status_code=status.HTTP_200_OK)
def receive_webhook(payload: WebhookPayload) -> dict:
    """
    Receive order event webhook from order service.
    
    Creates a notification for the user associated with the order.
    
    Payload:
    - order_id: ID of the order
    - user_email: Email of the user who placed the order
    - status: New order status
    - timestamp: Event timestamp
    
    Returns success confirmation.
    """
    user_email = payload.user_email
    
    # Get or create user's notification list
    user_notifications = get_user_notifications(user_email)
    
    # Create notification
    notification = {
        "id": str(uuid.uuid4()),
        "order_id": payload.order_id,
        "user_email": user_email,
        "status": payload.status,
        "timestamp": payload.timestamp,
        "read": False
    }
    
    user_notifications.append(notification)
    
    return {
        "success": True,
        "notification_id": notification["id"]
    }


# ============================================================================
# Notification Endpoints
# ============================================================================

@app.get("/notifications", response_model=NotificationListResponse)
def list_notifications(user: dict = Depends(get_current_user)) -> NotificationListResponse:
    """
    List all notifications for current user.
    
    Requires valid JWT in Authorization header.
    
    Returns list of notifications for the authenticated user's email.
    """
    user_email = user["email"]
    user_notifications = get_user_notifications(user_email)
    
    return NotificationListResponse(
        notifications=[NotificationResponse(**notif) for notif in user_notifications]
    )


@app.get("/notifications/unread", response_model=UnreadCountResponse)
def get_unread_count(user: dict = Depends(get_current_user)) -> UnreadCountResponse:
    """
    Get count of unread notifications for current user.
    
    Requires valid JWT in Authorization header.
    
    Returns count of unread notifications.
    """
    user_email = user["email"]
    user_notifications = get_user_notifications(user_email)
    
    unread_count = sum(1 for notif in user_notifications if not notif["read"])
    
    return UnreadCountResponse(unread_count=unread_count)


@app.patch("/notifications/{notification_id}/read", response_model=ReadStatusResponse)
def mark_notification_read(
    notification_id: str,
    user: dict = Depends(get_current_user)
) -> ReadStatusResponse:
    """
    Mark notification as read.
    
    - notification_id: ID of the notification to mark as read
    
    Requires valid JWT in Authorization header.
    Per-user isolation - user can only mark their own notifications as read.
    
    Returns updated notification status.
    """
    user_email = user["email"]
    user_notifications = get_user_notifications(user_email)
    
    # Find and mark notification as read
    for notif in user_notifications:
        if notif["id"] == notification_id:
            notif["read"] = True
            now = datetime.now(timezone.utc).isoformat()
            return ReadStatusResponse(
                id=notification_id,
                read=True,
                updated_at=now
            )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Notification not found"
    )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
