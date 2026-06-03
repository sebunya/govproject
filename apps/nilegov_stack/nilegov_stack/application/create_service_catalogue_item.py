# Use case: Create Service Catalogue Item
# Digi-Verse Uganda Limited

import time
from typing import List, Optional
from nilegov_stack.application.ports import ServiceCatalogueRepository
from nilegov_stack.domain.service_catalogue import ServiceCatalogueItem, WorkflowTemplate, ActiveStatus


class CreateServiceCatalogueItem:
    """Application Service to create a new Service Catalogue Item."""

    def __init__(self, repository: ServiceCatalogueRepository):
        self.repository = repository

    def execute(
        self,
        service_catalogue_id: str,
        service_name: str,
        service_code: str,
        responsible_mda_placeholder: str,
        service_category: str,
        service_description: str,
        required_documents: List[str],
        fee_required: bool,
        default_fee_amount: float,
        default_currency: str = "UGX",
        default_payment_purpose: str = "Not Applicable",
        default_payment_provider: str = "Not Applicable",
        default_sla_rule: Optional[str] = None,
        responsible_department: Optional[str] = None,
        responsible_queue: Optional[str] = None,
        workflow_template: str = WorkflowTemplate.STANDARD,
        active_status: str = ActiveStatus.ACTIVE,
        public_visibility: str = "Demo Visible",
        timestamp: Optional[float] = None
    ) -> ServiceCatalogueItem:
        curr_time = timestamp or time.time()
        
        item = ServiceCatalogueItem(
            service_catalogue_id=service_catalogue_id,
            service_name=service_name,
            service_code=service_code,
            responsible_mda_placeholder=responsible_mda_placeholder,
            service_category=service_category,
            service_description=service_description,
            required_documents=required_documents,
            fee_required=fee_required,
            default_fee_amount=default_fee_amount,
            default_currency=default_currency,
            default_payment_purpose=default_payment_purpose,
            default_payment_provider=default_payment_provider,
            default_sla_rule=default_sla_rule,
            responsible_department=responsible_department,
            responsible_queue=responsible_queue,
            workflow_template=workflow_template,
            active_status=active_status,
            public_visibility=public_visibility,
            created_at=curr_time,
            updated_at=curr_time
        )
        
        self.repository.save(item)
        return item
