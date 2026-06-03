# Use case: List Notifications by Citizen Profile
# Prototype simulation only. No live Government registry access.

from typing import List
from nilegov_stack.application.ports import NotificationEventRepository
from nilegov_stack.domain.notification import NotificationEvent

class ListNotificationsByCitizenProfile:
    def __init__(self, notification_repo: NotificationEventRepository):
        self.notification_repo = notification_repo

    def execute(self, profile_id: str) -> List[NotificationEvent]:
        return self.notification_repo.get_by_citizen_profile(profile_id)
