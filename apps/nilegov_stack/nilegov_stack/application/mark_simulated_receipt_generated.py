# Use Case: Mark Simulated Receipt Generated
# Prototype simulation only. No live payment processed.

import time
from typing import Optional
from nilegov_stack.application.ports import PaymentRecordRepository


class MarkSimulatedReceiptGenerated:
    """Application Service to transition a payment record's receipt status to Simulated Receipt Generated."""

    def __init__(self, repository: PaymentRecordRepository):
        self.repository = repository

    def execute(
        self,
        payment_id: str,
        receipt_reference: Optional[str] = None,
        timestamp: Optional[float] = None
    ):
        record = self.repository.get_by_id(payment_id)
        if not record:
            raise ValueError(f"Payment Record {payment_id} not found.")

        if not timestamp:
            timestamp = time.time()

        if not receipt_reference:
            receipt_reference = f"SIM-RECEIPT-2026-{payment_id.split('-')[-1]}"

        record.generate_receipt(receipt_reference, timestamp)
        self.repository.save(record)
        return record
