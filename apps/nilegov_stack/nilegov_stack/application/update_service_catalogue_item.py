# Use case: Update Service Catalogue Item
# Digi-Verse Uganda Limited

import time
from typing import List, Optional, Any, Dict
from nilegov_stack.application.ports import ServiceCatalogueRepository
from nilegov_stack.domain.service_catalogue import ServiceCatalogueItem, ServiceCategory, WorkflowTemplate, ActiveStatus, PaymentProviderOption


class UpdateServiceCatalogueItem:
    """Application Service to update an existing Service Catalogue Item."""

    def __init__(self, repository: ServiceCatalogueRepository):
        self.repository = repository

    def execute(
        self,
        service_catalogue_id: str,
        updates: Dict[str, Any],
        timestamp: Optional[float] = None
    ) -> ServiceCatalogueItem:
        item = self.repository.get_by_id(service_catalogue_id)
        if not item:
            raise ValueError(f"Service Catalogue Item {service_catalogue_id} not found.")

        curr_time = timestamp or time.time()

        if "service_name" in updates:
            val = updates["service_name"]
            if not val:
                raise ValueError("Service name is required.")
            item.service_name = val

        if "service_code" in updates:
            val = updates["service_code"]
            if not val:
                raise ValueError("Service code is required.")
            item.service_code = val

        if "responsible_mda_placeholder" in updates:
            item.responsible_mda_placeholder = updates["responsible_mda_placeholder"]

        if "service_category" in updates:
            val = updates["service_category"]
            if val not in ServiceCategory.ALL_CATEGORIES:
                raise ValueError(f"Invalid service category: {val}")
            item.service_category = val

        if "service_description" in updates:
            item.service_description = updates["service_description"]

        if "required_documents" in updates:
            item.required_documents = updates["required_documents"]

        if "fee_required" in updates:
            item.fee_required = bool(updates["fee_required"])

        if "default_fee_amount" in updates:
            val = float(updates["default_fee_amount"])
            if val < 0.0:
                raise ValueError("Default fee amount cannot be negative.")
            item.default_fee_amount = val

        if "default_currency" in updates:
            item.default_currency = updates["default_currency"]

        if "default_payment_purpose" in updates:
            item.default_payment_purpose = updates["default_payment_purpose"]

        if "default_payment_provider" in updates:
            val = updates["default_payment_provider"]
            if val not in PaymentProviderOption.ALL_OPTIONS:
                raise ValueError(f"Invalid payment provider: {val}")
            item.default_payment_provider = val

        if "default_sla_rule" in updates:
            item.default_sla_rule = updates["default_sla_rule"]

        if "responsible_department" in updates:
            item.responsible_department = updates["responsible_department"]

        if "responsible_queue" in updates:
            item.responsible_queue = updates["responsible_queue"]

        if "workflow_template" in updates:
            val = updates["workflow_template"]
            if val not in WorkflowTemplate.ALL_TEMPLATES:
                raise ValueError(f"Invalid workflow template: {val}")
            item.workflow_template = val

        if "active_status" in updates:
            val = updates["active_status"]
            if val not in ActiveStatus.ALL_STATUSES:
                raise ValueError(f"Invalid active status: {val}")
            item.active_status = val

        if "public_visibility" in updates:
            item.public_visibility = updates["public_visibility"]

        item.updated_at = curr_time
        self.repository.save(item)
        return item
