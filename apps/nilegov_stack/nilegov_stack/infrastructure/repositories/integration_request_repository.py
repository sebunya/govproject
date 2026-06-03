"""In-memory repository for simulated interoperability requests."""

from typing import Dict, List, Optional

from nilegov_stack.domain.interoperability import IntegrationRequest


class InMemoryIntegrationRequestRepository:
    def __init__(self) -> None:
        self._items: Dict[str, IntegrationRequest] = {}

    def save(self, request: IntegrationRequest) -> IntegrationRequest:
        self._items[request.integration_request_id] = request
        return request

    def get(self, integration_request_id: str) -> Optional[IntegrationRequest]:
        return self._items.get(integration_request_id)

    def list_all(self) -> List[IntegrationRequest]:
        return list(self._items.values())

    def list_by_target_system(self, target_system: str) -> List[IntegrationRequest]:
        return [item for item in self._items.values() if item.target_system == target_system]

    def list_by_status(self, status: str) -> List[IntegrationRequest]:
        return [item for item in self._items.values() if item.status == status]

    def list_by_service_request(self, service_request_reference: str) -> List[IntegrationRequest]:
        return [
            item
            for item in self._items.values()
            if item.service_request_reference == service_request_reference
        ]
