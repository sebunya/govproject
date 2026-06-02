# Use case: List Services
# Digi-Verse Uganda Limited

from typing import List, Optional
from nilegov_stack.application.ports import ServiceCatalogueRepository
from nilegov_stack.domain.service_catalogue import ServiceCatalogueItem


class ListServices:
    """Application Service to query and filter Service Catalogue items."""

    def __init__(self, repository: ServiceCatalogueRepository):
        self.repository = repository

    def execute(self, filter_by: Optional[str] = None, value: Optional[str] = None) -> List[ServiceCatalogueItem]:
        if filter_by == "active":
            return self.repository.get_active()
        elif filter_by == "demo":
            return self.repository.get_demo()
        elif filter_by == "category":
            if not value:
                raise ValueError("Category value is required for filtering by category.")
            return self.repository.get_by_category(value)
        return self.repository.get_all()
