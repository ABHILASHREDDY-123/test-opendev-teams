"""Integration tests for Notification Service."""

import pytest
import httpx
import time

NOTIFICATION_SERVICE_URL = "http://localhost:8004"


@pytest.mark.usefixtures("start_services")
class TestNotificationService:
    """Notification Service integration tests."""

    def test_health_check(self, http_client):
        """Test notification service health check."""
        response = http_client.get(f"{NOTIFICATION_SERVICE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_receive_webhook(self, http_client):
        """Test receiving order event webhook."""
        payload = {
            "order_id": "order-123",
            "user_email": "user@example.com",
            "status": "confirmed",
            "timestamp": "2024-01-01T12:00:00Z"
        }

        response = http_client.post(
            f"{NOTIFICATION_SERVICE_URL}/notifications/webhook",
            json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert "notification_id" in data
        assert data["status"] == "received"

    def test_list_notifications_requires_auth(self, http_client):
        """Test that listing notifications requires authentication."""
        response = http_client.get(f"{NOTIFICATION_SERVICE_URL}/notifications")
        assert response.status_code == 401

    def test_list_notifications_for_user(self, http_client, test_token):
        """Test listing notifications for a user."""
        # Receive a webhook
        payload = {
            "order_id": "order-456",
            "user_email": "test@example.com",
            "status": "pending",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        http_client.post(
            f"{NOTIFICATION_SERVICE_URL}/notifications/webhook",
            json=payload
        )

        # List notifications
        response = http_client.get(
            f"{NOTIFICATION_SERVICE_URL}/notifications",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) >= 1
        assert any(n["order_id"] == "order-456" for n in data["notifications"])

    def test_get_unread_count(self, http_client, test_token):
        """Test getting unread notification count."""
        # Receive webhooks
        for i in range(3):
            payload = {
                "order_id": f"order-{i}",
                "user_email": "test@example.com",
                "status": "pending",
                "timestamp": "2024-01-01T12:00:00Z"
            }
            http_client.post(
                f"{NOTIFICATION_SERVICE_URL}/notifications/webhook",
                json=payload
            )

        # Get unread count
        response = http_client.get(
            f"{NOTIFICATION_SERVICE_URL}/notifications/unread",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] >= 3

    def test_mark_notification_as_read(self, http_client, test_token):
        """Test marking a notification as read."""
        # Receive a webhook
        payload = {
            "order_id": "order-789",
            "user_email": "test@example.com",
            "status": "shipped",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        webhook_response = http_client.post(
            f"{NOTIFICATION_SERVICE_URL}/notifications/webhook",
            json=payload
        )
        notification_id = webhook_response.json()["notification_id"]

        # Mark as read
        response = http_client.patch(
            f"{NOTIFICATION_SERVICE_URL}/notifications/{notification_id}/read",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["read"] is True

    def test_mark_notification_as_read_decreases_unread_count(self, http_client, test_token):
        """Test that marking notification as read decreases unread count."""
        # Receive a webhook
        payload = {
            "order_id": "order-999",
            "user_email": "test@example.com",
            "status": "delivered",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        webhook_response = http_client.post(
            f"{NOTIFICATION_SERVICE_URL}/notifications/webhook",
            json=payload
        )
        notification_id = webhook_response.json()["notification_id"]

        # Get initial unread count
        response = http_client.get(
            f"{NOTIFICATION_SERVICE_URL}/notifications/unread",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        initial_count = response.json()["unread_count"]

        # Mark as read
        http_client.patch(
            f"{NOTIFICATION_SERVICE_URL}/notifications/{notification_id}/read",
            headers={"Authorization": f"Bearer {test_token}"}
        )

        # Get new unread count
        response = http_client.get(
            f"{NOTIFICATION_SERVICE_URL}/notifications/unread",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        new_count = response.json()["unread_count"]

        assert new_count == initial_count - 1
