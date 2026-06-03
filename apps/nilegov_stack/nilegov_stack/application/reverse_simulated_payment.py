# Use Case: Reverse Simulated Payment
# Prototype simulation only. No live payment processed.

import time
from typing import Optional
from nilegov_stack.application.ports import PaymentRecordRepository


class ReverseSimulatedPayment:
    """Application Service to reverse a verified payment record."""

    def __init__(self, repository: PaymentRecordRepository):
        self.repository = repository

    def execute(
        self,
        payment_id: str,
        timestamp: Optional[float] = None
    ):
        record = self.repository.get_by_id(payment_id)
        if not record:
            raise ValueError(f"Payment Record {payment_id} not found.")

        if not timestamp:
            timestamp = time.time()

        record.reverse(timestamp)
        self.repository.save(record)
        return record
