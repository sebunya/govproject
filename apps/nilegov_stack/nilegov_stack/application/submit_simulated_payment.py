# Use Case: Submit Simulated Payment
# Prototype simulation only. No live payment processed.

import time
from typing import Optional
from nilegov_stack.application.ports import PaymentRecordRepository
from nilegov_stack.domain.payment import PaymentRecord


class SubmitSimulatedPayment:
    """Application Service to transition a payment record to Submitted state with a transaction reference."""

    def __init__(self, repository: PaymentRecordRepository):
        self.repository = repository

    def execute(
        self,
        payment_id: str,
        transaction_reference: Optional[str] = None,
        timestamp: Optional[float] = None
    ) -> PaymentRecord:
        record = self.repository.get_by_id(payment_id)
        if not record:
            raise ValueError(f"Payment Record {payment_id} not found.")

        if not timestamp:
            timestamp = time.time()

        if not transaction_reference:
            # Generate deterministic/simple mock reference
            transaction_reference = f"SIM-PAY-NIRA-2026-{payment_id.split('-')[-1]}"

        record.submit(transaction_reference, timestamp)
        self.repository.save(record)
        return record
