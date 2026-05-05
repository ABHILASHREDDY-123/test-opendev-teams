"""
Unit tests for Notification Service endpoints.
"""

import pytest
from datetime import datetime, timezone
from .conftest import create_test_token


# ============================================================================
# Webhook Tests
# ============================================================================

class TestWebhookEndpoint:
    """Tests for webhook endpoint"""
    
    def test_receive_webhook_success(self, client, clear_db):
        """Test receiving webhook successfully"""
        payload = {
            "order_id": "order-123",
            "user_email": "user@example.com",
            "status": "confirmed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response = client.post("/notifications/webhook", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "notification_id" in data
    
    def test_receive_webhook_multiple_statuses(self, client, clear_db):
        """Test receiving webhooks for different order statuses"""
        user_email = "user@example.com"
        order_id = "order-123"
        statuses = ["pending", "confirmed", "shipped", "delivered"]
        
        for status in statuses:
            payload = {
                "order_id": order_id,
                "user_email": user_email,
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            response = client.post("/notifications/webhook", json=payload)
            assert response.status_code == 200
        
        # Verify all notifications were stored
        token = create_test_token(email=user_email)
        auth_header = {"Authorization": f"Bearer {token}"}
        
        list_response = client.get("/notifications", headers=auth_header)
        assert list_response.status_code == 200
        notifications = list_response.json()["notifications"]
        assert len(notifications) == 4
    
    def test_receive_webhook_missing_fields(self, client, clear_db):
        """Test webhook with missing required fields"""
        payload = {
            "order_id": "order-123",
            "user_email": "user@example.com"
            # Missing status and timestamp
        }
        
        response = client.post("/notifications/webhook", json=payload)
        
        assert response.status_code == 422  # Validation error


# ============================================================================
# Notification List Tests
# ============================================================================

class TestNotificationList:
    """Tests for notification list endpoint"""
    
    def test_list_notifications_empty(self, client, clear_db, auth_header):
        """Test listing empty notifications"""
        response = client.get("/notifications", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert data["notifications"] == []
    
    def test_list_notifications_with_items(self, client, clear_db, auth_header):
        """Test listing notifications with items"""
        user_email = "test@example.com"
        
        # Create some notifications via webhook
        for i in range(3):
            payload = {
                "order_id": f"order-{i}",
                "user_email": user_email,
                "status": "confirmed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            client.post("/notifications/webhook", json=payload)
        
        # List notifications
        response = client.get("/notifications", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 3
        
        # Verify notification structure
        for notif in data["notifications"]:
            assert "id" in notif
            assert "order_id" in notif
            assert "user_email" in notif
            assert "status" in notif
            assert "timestamp" in notif
            assert "read" in notif
            assert notif["read"] is False
    
    def test_list_notifications_no_auth(self, client, clear_db):
        """Test listing notifications without authentication"""
        response = client.get("/notifications")
        
        assert response.status_code == 403  # Forbidden (no auth header)
    
    def test_per_user_notification_isolation(self, client, clear_db):
        """Test that notifications are isolated per user"""
        user1_email = "user1@example.com"
        user2_email = "user2@example.com"
        
        # Create notifications for user 1
        for i in range(2):
            payload = {
                "order_id": f"order-{i}",
                "user_email": user1_email,
                "status": "confirmed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            client.post("/notifications/webhook", json=payload)
        
        # Create notifications for user 2
        for i in range(3):
            payload = {
                "order_id": f"order-{i}",
                "user_email": user2_email,
                "status": "shipped",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            client.post("/notifications/webhook", json=payload)
        
        # Get user 1 notifications
        user1_token = create_test_token(email=user1_email)
        user1_header = {"Authorization": f"Bearer {user1_token}"}
        
        response1 = client.get("/notifications", headers=user1_header)
        assert len(response1.json()["notifications"]) == 2
        
        # Get user 2 notifications
        user2_token = create_test_token(email=user2_email)
        user2_header = {"Authorization": f"Bearer {user2_token}"}
        
        response2 = client.get("/notifications", headers=user2_header)
        assert len(response2.json()["notifications"]) == 3


# ============================================================================
# Unread Count Tests
# ============================================================================

class TestUnreadCount:
    """Tests for unread count endpoint"""
    
    def test_unread_count_empty(self, client, clear_db, auth_header):
        """Test unread count with no notifications"""
        response = client.get("/notifications/unread", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 0
    
    def test_unread_count_all_unread(self, client, clear_db, auth_header):
        """Test unread count with all unread notifications"""
        user_email = "test@example.com"
        
        # Create 3 unread notifications
        for i in range(3):
            payload = {
                "order_id": f"order-{i}",
                "user_email": user_email,
                "status": "confirmed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            client.post("/notifications/webhook", json=payload)
        
        response = client.get("/notifications/unread", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 3
    
    def test_unread_count_mixed(self, client, clear_db, auth_header):
        """Test unread count with mix of read and unread"""
        user_email = "test@example.com"
        
        # Create 5 notifications
        notification_ids = []
        for i in range(5):
            payload = {
                "order_id": f"order-{i}",
                "user_email": user_email,
                "status": "confirmed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            response = client.post("/notifications/webhook", json=payload)
            notification_ids.append(response.json()["notification_id"])
        
        # Mark 2 as read
        for notif_id in notification_ids[:2]:
            client.patch(f"/notifications/{notif_id}/read", headers=auth_header)
        
        # Check unread count
        response = client.get("/notifications/unread", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 3
    
    def test_unread_count_no_auth(self, client, clear_db):
        """Test unread count without authentication"""
        response = client.get("/notifications/unread")
        
        assert response.status_code == 403


# ============================================================================
# Mark as Read Tests
# ============================================================================

class TestMarkAsRead:
    """Tests for mark as read endpoint"""
    
    def test_mark_notification_read_success(self, client, clear_db, auth_header):
        """Test marking notification as read"""
        user_email = "test@example.com"
        
        # Create notification
        payload = {
            "order_id": "order-123",
            "user_email": user_email,
            "status": "confirmed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        webhook_response = client.post("/notifications/webhook", json=payload)
        notification_id = webhook_response.json()["notification_id"]
        
        # Mark as read
        response = client.patch(f"/notifications/{notification_id}/read", headers=auth_header)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == notification_id
        assert data["read"] is True
        assert "updated_at" in data
    
    def test_mark_notification_read_updates_list(self, client, clear_db, auth_header):
        """Test that marking as read updates the notification list"""
        user_email = "test@example.com"
        
        # Create notification
        payload = {
            "order_id": "order-123",
            "user_email": user_email,
            "status": "confirmed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        webhook_response = client.post("/notifications/webhook", json=payload)
        notification_id = webhook_response.json()["notification_id"]
        
        # Mark as read
        client.patch(f"/notifications/{notification_id}/read", headers=auth_header)
        
        # Get notifications list
        list_response = client.get("/notifications", headers=auth_header)
        notifications = list_response.json()["notifications"]
        
        assert len(notifications) == 1
        assert notifications[0]["id"] == notification_id
        assert notifications[0]["read"] is True
    
    def test_mark_notification_read_not_found(self, client, clear_db, auth_header):
        """Test marking non-existent notification as read"""
        response = client.patch("/notifications/invalid-id/read", headers=auth_header)
        
        assert response.status_code == 404
        assert "Notification not found" in response.json()["detail"]
    
    def test_mark_notification_read_no_auth(self, client, clear_db):
        """Test marking as read without authentication"""
        response = client.patch("/notifications/notif-123/read")
        
        assert response.status_code == 403
    
    def test_mark_notification_read_per_user_isolation(self, client, clear_db):
        """Test that user can only mark their own notifications as read"""
        user1_email = "user1@example.com"
        user2_email = "user2@example.com"
        
        # Create notification for user 1
        payload = {
            "order_id": "order-123",
            "user_email": user1_email,
            "status": "confirmed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        webhook_response = client.post("/notifications/webhook", json=payload)
        notification_id = webhook_response.json()["notification_id"]
        
        # Try to mark as read with user 2's token
        user2_token = create_test_token(email=user2_email)
        user2_header = {"Authorization": f"Bearer {user2_token}"}
        
        response = client.patch(f"/notifications/{notification_id}/read", headers=user2_header)
        
        assert response.status_code == 404  # User 2 can't see user 1's notifications


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealthCheck:
    """Tests for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for notification workflow"""
    
    def test_complete_notification_workflow(self, client, clear_db):
        """Test complete workflow: webhook -> list -> mark read"""
        user_email = "user@example.com"
        user_token = create_test_token(email=user_email)
        auth_header = {"Authorization": f"Bearer {user_token}"}
        
        # Step 1: Receive webhook for order placed
        payload1 = {
            "order_id": "order-123",
            "user_email": user_email,
            "status": "pending",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        response = client.post("/notifications/webhook", json=payload1)
        assert response.status_code == 200
        notif_id_1 = response.json()["notification_id"]
        
        # Step 2: Check unread count (should be 1)
        response = client.get("/notifications/unread", headers=auth_header)
        assert response.json()["unread_count"] == 1
        
        # Step 3: Receive webhook for order confirmed
        payload2 = {
            "order_id": "order-123",
            "user_email": user_email,
            "status": "confirmed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        response = client.post("/notifications/webhook", json=payload2)
        assert response.status_code == 200
        notif_id_2 = response.json()["notification_id"]
        
        # Step 4: Check unread count (should be 2)
        response = client.get("/notifications/unread", headers=auth_header)
        assert response.json()["unread_count"] == 2
        
        # Step 5: List all notifications
        response = client.get("/notifications", headers=auth_header)
        notifications = response.json()["notifications"]
        assert len(notifications) == 2
        assert all(not n["read"] for n in notifications)
        
        # Step 6: Mark first notification as read
        client.patch(f"/notifications/{notif_id_1}/read", headers=auth_header)
        
        # Step 7: Check unread count (should be 1)
        response = client.get("/notifications/unread", headers=auth_header)
        assert response.json()["unread_count"] == 1
        
        # Step 8: List notifications (one read, one unread)
        response = client.get("/notifications", headers=auth_header)
        notifications = response.json()["notifications"]
        assert len(notifications) == 2
        read_count = sum(1 for n in notifications if n["read"])
        unread_count = sum(1 for n in notifications if not n["read"])
        assert read_count == 1
        assert unread_count == 1
