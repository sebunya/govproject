# Use Case: List Payments By Payment Status
# Prototype simulation only. No live payment processed.

from typing import List
from nilegov_stack.application.ports import PaymentRecordRepository
from nilegov_stack.domain.payment import PaymentRecord


class ListPaymentsByPaymentStatus:
    """Application Service to retrieve all payment records in a specific payment status."""

    def __init__(self, repository: PaymentRecordRepository):
        self.repository = repository

    def execute(self, status: str) -> List[PaymentRecord]:
        return self.repository.get_by_status(status)
