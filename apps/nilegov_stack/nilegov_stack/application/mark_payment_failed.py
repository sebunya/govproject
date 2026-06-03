# Use Case: Mark Payment Failed
# Prototype simulation only. No live payment processed.

import time
from typing import Optional
from nilegov_stack.application.ports import PaymentRecordRepository


class MarkPaymentFailed:
    """Application Service to mark a payment record as failed with a reason."""

    def __init__(self, repository: PaymentRecordRepository):
        self.repository = repository

    def execute(
        self,
        payment_id: str,
        reason: str,
        timestamp: Optional[float] = None
    ):
        record = self.repository.get_by_id(payment_id)
        if not record:
            raise ValueError(f"Payment Record {payment_id} not found.")

        if not timestamp:
            timestamp = time.time()

        record.fail(reason, timestamp)
        self.repository.save(record)
        return record
