# Use case: Manage Service Status
# Digi-Verse Uganda Limited

import time
from typing import Optional
from nilegov_stack.application.ports import ServiceCatalogueRepository
from nilegov_stack.domain.service_catalogue import ServiceCatalogueItem


class ManageServiceStatus:
    """Application Service to transition the active status of a Service Catalogue item."""

    def __init__(self, repository: ServiceCatalogueRepository):
        self.repository = repository

    def execute(
        self,
        service_catalogue_id: str,
        action: str,
        timestamp: Optional[float] = None
    ) -> ServiceCatalogueItem:
        item = self.repository.get_by_id(service_catalogue_id)
        if not item:
            raise ValueError(f"Service Catalogue Item {service_catalogue_id} not found.")

        curr_time = timestamp or time.time()

        if action == "activate":
            item.activate(curr_time)
        elif action == "deactivate":
            item.deactivate(curr_time)
        elif action == "mark_demo_only":
            item.mark_demo_only(curr_time)
        else:
            raise ValueError(f"Invalid status transition action: {action}")

        self.repository.save(item)
        return item
