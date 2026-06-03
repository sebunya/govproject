# Use case: Mark Notification Event as Failed
# Prototype simulation only. No live Government registry access.

import time
from typing import Optional
from nilegov_stack.application.ports import NotificationEventRepository

class MarkNotificationFailed:
    def __init__(self, notification_repo: NotificationEventRepository):
        self.notification_repo = notification_repo

    def execute(self, event_id: str, reason: str, timestamp: Optional[float] = None) -> None:
        t = timestamp if timestamp is not None else time.time()
        event = self.notification_repo.get_by_id(event_id)
        if not event:
            raise ValueError(f"Notification Event with ID {event_id} not found.")

        event.simulated_fail(t, reason)
        event.updated_at = t
        self.notification_repo.save(event)
