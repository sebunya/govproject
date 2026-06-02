# Use case: Apply Service Catalogue Defaults
# Digi-Verse Uganda Limited

from typing import Optional, Dict, Any, List
from nilegov_stack.application.ports import ServiceCatalogueRepository, SLARuleRepository
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.domain.payment import PaymentRecord, PaymentPurpose
from nilegov_stack.domain.service_catalogue import ServiceCatalogueItem, PaymentProviderOption


class ApplyCatalogueDefaults:
    """Application Service to apply defaults from Service Catalogue to request/payment aggregates."""

    def __init__(self, catalogue_repo: ServiceCatalogueRepository, sla_rule_repo: Optional[SLARuleRepository] = None):
        self.catalogue_repo = catalogue_repo
        self.sla_rule_repo = sla_rule_repo

    def execute_request_defaults(self, service_request: ServiceRequest, service_code: str, timestamp: float) -> None:
        item = self.catalogue_repo.get_by_code(service_code)
        if not item:
            return

        service_request.service_catalogue_item_id = item.service_catalogue_id

        # Update responsible queue/department defaults
        if item.responsible_department:
            service_request.assigned_department = item.responsible_department
        if item.responsible_queue:
            service_request.queue_name = item.responsible_queue

        # Apply default SLA rules if defined and repo available
        if item.default_sla_rule and self.sla_rule_repo:
            rule = self.sla_rule_repo.get_by_id(item.default_sla_rule)
            if rule:
                service_request.assign_sla_rule(rule, timestamp)

        # Sync payment status requirements
        if item.fee_required:
            service_request.payment_status = "Pending"
            service_request.payment_amount = item.default_fee_amount
        else:
            service_request.payment_status = "Not Required"
            service_request.payment_amount = 0.0

    def execute_payment_defaults(self, payment_record: PaymentRecord, service_code: str) -> None:
        item = self.catalogue_repo.get_by_code(service_code)
        if not item:
            return

        if item.fee_required:
            payment_record.amount = item.default_fee_amount
            payment_record.payment_purpose = item.default_payment_purpose
            
            # Map payment provider options
            if item.default_payment_provider == PaymentProviderOption.PESAPAL_SANDBOX:
                payment_record.provider = "Pesapal Sandbox"
                payment_record.provider_mode = "sandbox"
            elif item.default_payment_provider == PaymentProviderOption.SIMULATED:
                payment_record.provider = "Simulated"
        else:
            payment_record.amount = 0.0
            payment_record.payment_purpose = "Not Applicable"
            payment_record.payment_status = "Not Required"
            payment_record.verification_status = "Not Applicable"

    def check_evidence_requirements(self, service_code: str, submitted_documents: List[str]) -> Dict[str, Any]:
        """Validates if all required documents for a service are met."""
        item = self.catalogue_repo.get_by_code(service_code)
        if not item:
            return {"complete": True, "missing": []}

        required = item.required_documents or []
        missing = [doc for doc in required if doc not in submitted_documents]

        return {
            "complete": len(missing) == 0,
            "required": required,
            "missing": missing
        }
