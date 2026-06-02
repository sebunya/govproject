# Use Case: Calculate Payment Summary Metrics
# Prototype simulation only. No live payment processed.

from typing import Dict, Any, List
from nilegov_stack.application.ports import PaymentRecordRepository
from nilegov_stack.domain.payment import PaymentStatus, ReconciliationStatus


class CalculatePaymentSummaryMetrics:
    """Application Service to compute payment statistics and aggregate counts for reporting."""

    def __init__(self, repository: PaymentRecordRepository):
        self.repository = repository

    def execute(self) -> Dict[str, Any]:
        all_payments = self.repository.get_all()

        total_count = len(all_payments)
        total_amount_verified = 0.0

        status_counts = {s: 0 for s in PaymentStatus.ALL_STATUSES}
        recon_counts = {r: 0 for r in ReconciliationStatus.ALL_STATUSES}

        for p in all_payments:
            status_counts[p.payment_status] = status_counts.get(p.payment_status, 0) + 1
            recon_counts[p.reconciliation_status] = recon_counts.get(p.reconciliation_status, 0) + 1
            
            if p.payment_status == PaymentStatus.VERIFIED:
                total_amount_verified += p.amount

        return {
            "total_count": total_count,
            "total_amount_verified": total_amount_verified,
            "status_counts": status_counts,
            "reconciliation_counts": recon_counts
        }
