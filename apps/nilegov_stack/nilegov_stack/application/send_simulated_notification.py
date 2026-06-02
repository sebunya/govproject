# Use case: Send Simulated Notification
# Prototype simulation only. No live Government registry access.

import time
from typing import Optional
from nilegov_stack.application.ports import NotificationEventRepository, NotificationGateway
from nilegov_stack.domain.notification import NotificationDeliveryStatus, NotificationChannel

class SendSimulatedNotification:
    def __init__(self, notification_repo: NotificationEventRepository, gateway: NotificationGateway):
        self.notification_repo = notification_repo
        self.gateway = gateway

    def execute(self, event_id: str, timestamp: Optional[float] = None) -> None:
        t = timestamp if timestamp is not None else time.time()
        event = self.notification_repo.get_by_id(event_id)
        if not event:
            raise ValueError(f"Notification Event with ID {event_id} not found.")

        # Ignore if not active or already completed
        if event.delivery_status in (NotificationDeliveryStatus.SIMULATED_SENT, NotificationDeliveryStatus.SIMULATED_FAILED, NotificationDeliveryStatus.CANCELLED, NotificationDeliveryStatus.NOT_REQUIRED):
            return

        success = False
        try:
            # Deterministic simulation failure checks
            if not event.recipient or event.recipient == "invalid" or "@" not in event.recipient and not event.recipient.startswith("+") and not event.recipient.isdigit():
                event.simulated_fail(t, "Invalid recipient format.")
                self.notification_repo.save(event)
                return

            if event.channel == NotificationChannel.EMAIL:
                success = self.gateway.send_email(event.recipient, event.message_title or "NileGov Update", event.message)
            elif event.channel in (NotificationChannel.SMS, NotificationChannel.WHATSAPP):
                success = self.gateway.send_sms(event.recipient, event.message)
            else:
                # Default mock channel
                success = True
                
            if success:
                event.simulated_send(t)
            else:
                event.simulated_fail(t, "Gateway failed to queue notification.")
        except Exception as e:
            event.simulated_fail(t, str(e))

        event.updated_at = t
        self.notification_repo.save(event)
