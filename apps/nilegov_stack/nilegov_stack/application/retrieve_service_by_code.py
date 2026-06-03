# Use case: Retrieve Service By Code
# Digi-Verse Uganda Limited

from typing import Optional
from nilegov_stack.application.ports import ServiceCatalogueRepository
from nilegov_stack.domain.service_catalogue import ServiceCatalogueItem


class RetrieveServiceByCode:
    """Application Service to fetch a Service Catalogue item by its unique service code."""

    def __init__(self, repository: ServiceCatalogueRepository):
        self.repository = repository

    def execute(self, service_code: str) -> Optional[ServiceCatalogueItem]:
        if not service_code:
            raise ValueError("Service code is required.")
        return self.repository.get_by_code(service_code)
