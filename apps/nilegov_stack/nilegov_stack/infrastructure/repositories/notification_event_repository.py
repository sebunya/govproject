# InMemory Notification Event Repository Implementation
# Prototype simulation only. No live Government registry access.

from typing import Dict, Optional, List
from nilegov_stack.application.ports import NotificationEventRepository
from nilegov_stack.domain.notification import NotificationEvent

class InMemoryNotificationEventRepository(NotificationEventRepository):
    """In-memory implementation of the NotificationEventRepository port."""
    
    def __init__(self):
        self._events: Dict[str, NotificationEvent] = {}

    def save(self, event: NotificationEvent) -> None:
        self._events[event.notification_event_id] = event

    def get_by_id(self, event_id: str) -> Optional[NotificationEvent]:
        return self._events.get(event_id)

    def get_by_service_request(self, request_id: str) -> List[NotificationEvent]:
        return [
            evt for evt in self._events.values()
            if evt.service_request_id == request_id
        ]

    def get_by_citizen_profile(self, profile_id: str) -> List[NotificationEvent]:
        return [
            evt for evt in self._events.values()
            if evt.citizen_profile_id == profile_id
        ]

    def get_by_channel(self, channel: str) -> List[NotificationEvent]:
        return [
            evt for evt in self._events.values()
            if evt.channel == channel
        ]

    def get_by_delivery_status(self, status: str) -> List[NotificationEvent]:
        return [
            evt for evt in self._events.values()
            if evt.delivery_status == status
        ]

    def get_all(self) -> List[NotificationEvent]:
        return list(self._events.values())
