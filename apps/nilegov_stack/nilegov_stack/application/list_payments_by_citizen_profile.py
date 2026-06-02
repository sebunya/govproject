# Use Case: List Payments By Citizen Profile
# Prototype simulation only. No live payment processed.

from typing import List
from nilegov_stack.application.ports import PaymentRecordRepository
from nilegov_stack.domain.payment import PaymentRecord


class ListPaymentsByCitizenProfile:
    """Application Service to retrieve all payment records for a specific citizen profile."""

    def __init__(self, repository: PaymentRecordRepository):
        self.repository = repository

    def execute(self, profile_id: str) -> List[PaymentRecord]:
        return self.repository.get_by_citizen_profile(profile_id)
