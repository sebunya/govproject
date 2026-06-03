# InMemory Payment Record Repository Implementation
# Prototype simulation only. No live payment processed.

from typing import Dict, Optional, List
from nilegov_stack.application.ports import PaymentRecordRepository
from nilegov_stack.domain.payment import PaymentRecord


class InMemoryPaymentRecordRepository(PaymentRecordRepository):
    """In-memory implementation of the PaymentRecordRepository port for local tests."""

    def __init__(self):
        self._payments: Dict[str, PaymentRecord] = {}

    def save(self, payment_record: PaymentRecord) -> None:
        self._payments[payment_record.payment_record_id] = payment_record

    def get_by_id(self, payment_id: str) -> Optional[PaymentRecord]:
        return self._payments.get(payment_id)

    def get_by_service_request(self, request_id: str) -> List[PaymentRecord]:
        return [p for p in self._payments.values() if p.service_request_id == request_id]

    def get_by_citizen_profile(self, profile_id: str) -> List[PaymentRecord]:
        return [p for p in self._payments.values() if p.citizen_profile_id == profile_id]

    def get_by_status(self, status: str) -> List[PaymentRecord]:
        return [p for p in self._payments.values() if p.payment_status == status]

    def get_by_reconciliation_status(self, status: str) -> List[PaymentRecord]:
        return [p for p in self._payments.values() if p.reconciliation_status == status]

    def get_all(self) -> List[PaymentRecord]:
        return list(self._payments.values())
