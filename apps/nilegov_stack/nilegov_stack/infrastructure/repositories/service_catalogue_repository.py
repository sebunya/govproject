# InMemory Service Catalogue Repository Implementation
# Prototype service catalogue only. Not connected to a live government service registry.

from typing import Dict, Optional, List
from nilegov_stack.application.ports import ServiceCatalogueRepository
from nilegov_stack.domain.service_catalogue import ServiceCatalogueItem, ActiveStatus


class InMemoryServiceCatalogueRepository(ServiceCatalogueRepository):
    """In-memory implementation of ServiceCatalogueRepository for unit testing."""

    def __init__(self):
        self._items: Dict[str, ServiceCatalogueItem] = {}

    def save(self, item: ServiceCatalogueItem) -> None:
        self._items[item.service_catalogue_id] = item

    def get_by_id(self, item_id: str) -> Optional[ServiceCatalogueItem]:
        return self._items.get(item_id)

    def get_by_code(self, service_code: str) -> Optional[ServiceCatalogueItem]:
        for item in self._items.values():
            if item.service_code == service_code:
                return item
        return None

    def get_all(self) -> List[ServiceCatalogueItem]:
        return list(self._items.values())

    def get_active(self) -> List[ServiceCatalogueItem]:
        return [item for item in self._items.values() if item.active_status == ActiveStatus.ACTIVE]

    def get_demo(self) -> List[ServiceCatalogueItem]:
        return [item for item in self._items.values() if item.active_status == ActiveStatus.DEMO_ONLY]

    def get_by_category(self, category: str) -> List[ServiceCatalogueItem]:
        return [item for item in self._items.values() if item.service_category == category]
