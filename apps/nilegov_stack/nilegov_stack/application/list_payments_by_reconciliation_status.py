# Use Case: List Payments By Reconciliation Status
# Prototype simulation only. No live payment processed.

from typing import List
from nilegov_stack.application.ports import PaymentRecordRepository
from nilegov_stack.domain.payment import PaymentRecord


class ListPaymentsByReconciliationStatus:
    """Application Service to retrieve all payment records in a specific reconciliation status."""

    def __init__(self, repository: PaymentRecordRepository):
        self.repository = repository

    def execute(self, status: str) -> List[PaymentRecord]:
        return self.repository.get_by_reconciliation_status(status)
