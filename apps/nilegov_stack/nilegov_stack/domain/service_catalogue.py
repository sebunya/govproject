# NileGov Service Catalogue Domain Class & Constants
# Digi-Verse Uganda Limited
# Prototype service catalogue only. Not connected to a live government service registry.

import time
from typing import Optional, List


class ServiceCategory:
    IDENTITY_SERVICES = "Identity Services"
    CITIZEN_COMPLAINTS = "Citizen Complaints"
    PERMIT_APPLICATIONS = "Permit Applications"
    INSPECTION_SERVICES = "Inspection Services"
    INFORMATION_REQUESTS = "Information Requests"
    OTHER_GOVERNMENT_SERVICES = "Other Government Services"

    ALL_CATEGORIES = (
        IDENTITY_SERVICES,
        CITIZEN_COMPLAINTS,
        PERMIT_APPLICATIONS,
        INSPECTION_SERVICES,
        INFORMATION_REQUESTS,
        OTHER_GOVERNMENT_SERVICES
    )


class ActiveStatus:
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    DEMO_ONLY = "Demo Only"
    RETIRED = "Retired"

    ALL_STATUSES = (
        ACTIVE,
        INACTIVE,
        DEMO_ONLY,
        RETIRED
    )


class WorkflowTemplate:
    STANDARD = "Standard Application Workflow"
    REPLACEMENT = "Replacement Request Workflow"
    COMPLAINT = "Complaint Resolution Workflow"
    INSPECTION = "Inspection Workflow"
    INFO_REQUEST = "Information Request Workflow"

    ALL_TEMPLATES = (
        STANDARD,
        REPLACEMENT,
        COMPLAINT,
        INSPECTION,
        INFO_REQUEST
    )


class PaymentProviderOption:
    SIMULATED = "Simulated"
    PESAPAL_SANDBOX = "Pesapal Sandbox Ready"
    NOT_APPLICABLE = "Not Applicable"

    ALL_OPTIONS = (
        SIMULATED,
        PESAPAL_SANDBOX,
        NOT_APPLICABLE
    )


class ServiceCatalogueItem:
    """Domain aggregate representing a configured government service template."""

    DISCLAIMER = "Prototype service catalogue only. Not connected to a live government service registry."

    def __init__(
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
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None
    ):
        self.service_catalogue_id = service_catalogue_id
        
        if not service_name:
            raise ValueError("Service name is required.")
        self.service_name = service_name
        
        if not service_code:
            raise ValueError("Service code is required.")
        self.service_code = service_code
        
        self.responsible_mda_placeholder = responsible_mda_placeholder
        
        if service_category not in ServiceCategory.ALL_CATEGORIES:
            raise ValueError(f"Invalid service category: {service_category}")
        self.service_category = service_category
        
        self.service_description = service_description
        self.required_documents = required_documents or []
        self.fee_required = fee_required
        
        if default_fee_amount < 0.0:
            raise ValueError("Default fee amount cannot be negative.")
        self.default_fee_amount = default_fee_amount
        self.default_currency = default_currency
        self.default_payment_purpose = default_payment_purpose
        
        if default_payment_provider not in PaymentProviderOption.ALL_OPTIONS:
            raise ValueError(f"Invalid payment provider: {default_payment_provider}")
        self.default_payment_provider = default_payment_provider
        
        self.default_sla_rule = default_sla_rule
        self.responsible_department = responsible_department
        self.responsible_queue = responsible_queue
        
        if workflow_template not in WorkflowTemplate.ALL_TEMPLATES:
            raise ValueError(f"Invalid workflow template: {workflow_template}")
        self.workflow_template = workflow_template
        
        if active_status not in ActiveStatus.ALL_STATUSES:
            raise ValueError(f"Invalid active status: {active_status}")
        self.active_status = active_status
        
        self.public_visibility = public_visibility
        self.disclaimer = self.DISCLAIMER
        self.created_at = created_at or time.time()
        self.updated_at = updated_at or self.created_at

    def activate(self, timestamp: float):
        """Sets status to Active."""
        self.active_status = ActiveStatus.ACTIVE
        self.updated_at = timestamp

    def deactivate(self, timestamp: float):
        """Sets status to Inactive."""
        self.active_status = ActiveStatus.INACTIVE
        self.updated_at = timestamp

    def mark_demo_only(self, timestamp: float):
        """Sets status to Demo Only."""
        self.active_status = ActiveStatus.DEMO_ONLY
        self.updated_at = timestamp
