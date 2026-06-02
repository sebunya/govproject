# Service Request Repository Implementation
# Digi-Verse Uganda Limited

from typing import Dict, Optional, List
from nilegov_stack.application.ports import ServiceRequestRepository
from nilegov_stack.domain.service_request import ServiceRequest


class InMemoryServiceRequestRepository(ServiceRequestRepository):
    """In-memory implementation of the ServiceRequestRepository port.
    
    Used for local test suites and prototype demo walk-throughs.
    """
    def __init__(self):
        self._requests: Dict[str, ServiceRequest] = {}

    def save(self, service_request: ServiceRequest) -> None:
        self._requests[service_request.request_id] = service_request

    def get_by_id(self, request_id: str) -> Optional[ServiceRequest]:
        return self._requests.get(request_id)

    def get_by_reference(self, reference_no: str) -> Optional[ServiceRequest]:
        for req in self._requests.values():
            if req.reference_no == reference_no:
                return req
        return None

    def get_by_citizen_profile(self, profile_id: str) -> List[ServiceRequest]:
        results = []
        for req in self._requests.values():
            if req.citizen_profile_id == profile_id:
                results.append(req)
        return results

    def get_all(self) -> List[ServiceRequest]:
        return list(self._requests.values())
