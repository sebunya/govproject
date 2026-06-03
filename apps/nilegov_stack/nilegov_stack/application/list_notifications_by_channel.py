# Use case: List Notifications by Channel
# Prototype simulation only. No live Government registry access.

from typing import List
from nilegov_stack.application.ports import NotificationEventRepository
from nilegov_stack.domain.notification import NotificationEvent

class ListNotificationsByChannel:
    def __init__(self, notification_repo: NotificationEventRepository):
        self.notification_repo = notification_repo

    def execute(self, channel: str) -> List[NotificationEvent]:
        return self.notification_repo.get_by_channel(channel)
