# Use Case: List Payments By Service Request
# Prototype simulation only. No live payment processed.

from typing import List
from nilegov_stack.application.ports import PaymentRecordRepository
from nilegov_stack.domain.payment import PaymentRecord


class ListPaymentsByServiceRequest:
    """Application Service to retrieve all payment records for a specific service request."""

    def __init__(self, repository: PaymentRecordRepository):
        self.repository = repository

    def execute(self, request_id: str) -> List[PaymentRecord]:
        return self.repository.get_by_service_request(request_id)
