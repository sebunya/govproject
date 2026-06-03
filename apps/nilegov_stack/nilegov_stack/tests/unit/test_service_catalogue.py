# Unit Tests for NileGov Service Catalogue Integration
# Digi-Verse Uganda Limited
# Prototype service catalogue only. Not connected to a live government service registry.

import pytest
import time
from unittest.mock import MagicMock, patch

from nilegov_stack.domain.service_catalogue import (
    ServiceCatalogueItem,
    ServiceCategory,
    ActiveStatus,
    WorkflowTemplate,
    PaymentProviderOption
)
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.domain.payment import PaymentRecord
from nilegov_stack.domain.sla import SLARule
from nilegov_stack.domain.value_objects import NIN

from nilegov_stack.application.create_service_catalogue_item import CreateServiceCatalogueItem
from nilegov_stack.application.update_service_catalogue_item import UpdateServiceCatalogueItem
from nilegov_stack.application.list_services import ListServices
from nilegov_stack.application.manage_service_status import ManageServiceStatus
from nilegov_stack.application.retrieve_service_by_code import RetrieveServiceByCode
from nilegov_stack.application.apply_catalogue_defaults import ApplyCatalogueDefaults

from nilegov_stack.infrastructure.repositories.service_catalogue_repository import InMemoryServiceCatalogueRepository
from nilegov_stack.infrastructure.repositories.frappe_service_catalogue_repository import FrappeServiceCatalogueRepository


def test_service_catalogue_item_creation_and_validation():
    """Verifies that ServiceCatalogueItem validates inputs and enums correctly."""
    # Valid item creation
    item = ServiceCatalogueItem(
        service_catalogue_id="SVC-LOST-NID",
        service_name="Lost National ID Replacement",
        service_code="LOST_NATIONAL_ID",
        responsible_mda_placeholder="NIRA",
        service_category=ServiceCategory.IDENTITY_SERVICES,
        service_description="Replacement NID Card",
        required_documents=["Police Letter Placeholder", "Affidavit Placeholder"],
        fee_required=True,
        default_fee_amount=50000.0,
        default_payment_provider=PaymentProviderOption.SIMULATED,
        workflow_template=WorkflowTemplate.REPLACEMENT,
        active_status=ActiveStatus.ACTIVE
    )

    assert item.service_catalogue_id == "SVC-LOST-NID"
    assert item.service_name == "Lost National ID Replacement"
    assert item.service_code == "LOST_NATIONAL_ID"
    assert item.disclaimer == "Prototype service catalogue only. Not connected to a live government service registry."
    assert item.required_documents == ["Police Letter Placeholder", "Affidavit Placeholder"]
    assert item.default_fee_amount == 50000.0
    assert item.default_payment_provider == PaymentProviderOption.SIMULATED
    assert item.active_status == ActiveStatus.ACTIVE

    # Test Validation: Missing name
    with pytest.raises(ValueError, match="Service name is required"):
        ServiceCatalogueItem(
            service_catalogue_id="SVC-1",
            service_name="",
            service_code="CODE-1",
            responsible_mda_placeholder="NIRA",
            service_category=ServiceCategory.IDENTITY_SERVICES,
            service_description="Desc",
            required_documents=[],
            fee_required=False,
            default_fee_amount=0.0
        )

    # Test Validation: Missing code
    with pytest.raises(ValueError, match="Service code is required"):
        ServiceCatalogueItem(
            service_catalogue_id="SVC-1",
            service_name="Name",
            service_code="",
            responsible_mda_placeholder="NIRA",
            service_category=ServiceCategory.IDENTITY_SERVICES,
            service_description="Desc",
            required_documents=[],
            fee_required=False,
            default_fee_amount=0.0
        )

    # Test Validation: Invalid category
    with pytest.raises(ValueError, match="Invalid service category"):
        ServiceCatalogueItem(
            service_catalogue_id="SVC-1",
            service_name="Name",
            service_code="CODE-1",
            responsible_mda_placeholder="NIRA",
            service_category="Invalid Category",
            service_description="Desc",
            required_documents=[],
            fee_required=False,
            default_fee_amount=0.0
        )

    # Test Validation: Negative fee amount
    with pytest.raises(ValueError, match="Default fee amount cannot be negative"):
        ServiceCatalogueItem(
            service_catalogue_id="SVC-1",
            service_name="Name",
            service_code="CODE-1",
            responsible_mda_placeholder="NIRA",
            service_category=ServiceCategory.IDENTITY_SERVICES,
            service_description="Desc",
            required_documents=[],
            fee_required=True,
            default_fee_amount=-1000.0
        )

    # Test Validation: Invalid payment provider
    with pytest.raises(ValueError, match="Invalid payment provider"):
        ServiceCatalogueItem(
            service_catalogue_id="SVC-1",
            service_name="Name",
            service_code="CODE-1",
            responsible_mda_placeholder="NIRA",
            service_category=ServiceCategory.IDENTITY_SERVICES,
            service_description="Desc",
            required_documents=[],
            fee_required=True,
            default_fee_amount=5000.0,
            default_payment_provider="Invalid Provider"
        )

    # Test Validation: Invalid workflow template
    with pytest.raises(ValueError, match="Invalid workflow template"):
        ServiceCatalogueItem(
            service_catalogue_id="SVC-1",
            service_name="Name",
            service_code="CODE-1",
            responsible_mda_placeholder="NIRA",
            service_category=ServiceCategory.IDENTITY_SERVICES,
            service_description="Desc",
            required_documents=[],
            fee_required=False,
            default_fee_amount=0.0,
            workflow_template="Invalid Workflow"
        )

    # Test Validation: Invalid active status
    with pytest.raises(ValueError, match="Invalid active status"):
        ServiceCatalogueItem(
            service_catalogue_id="SVC-1",
            service_name="Name",
            service_code="CODE-1",
            responsible_mda_placeholder="NIRA",
            service_category=ServiceCategory.IDENTITY_SERVICES,
            service_description="Desc",
            required_documents=[],
            fee_required=False,
            default_fee_amount=0.0,
            active_status="Invalid Status"
        )


def test_service_catalogue_item_status_transitions():
    """Verifies that status transition methods update state correctly."""
    item = ServiceCatalogueItem(
        service_catalogue_id="SVC-LOST-NID",
        service_name="Lost National ID Replacement",
        service_code="LOST_NATIONAL_ID",
        responsible_mda_placeholder="NIRA",
        service_category=ServiceCategory.IDENTITY_SERVICES,
        service_description="Desc",
        required_documents=[],
        fee_required=False,
        default_fee_amount=0.0
    )

    # Default is Active
    assert item.active_status == ActiveStatus.ACTIVE

    # Deactivate
    item.deactivate(1000.0)
    assert item.active_status == ActiveStatus.INACTIVE
    assert item.updated_at == 1000.0

    # Activate
    item.activate(2000.0)
    assert item.active_status == ActiveStatus.ACTIVE
    assert item.updated_at == 2000.0

    # Mark demo only
    item.mark_demo_only(3000.0)
    assert item.active_status == ActiveStatus.DEMO_ONLY
    assert item.updated_at == 3000.0


def test_in_memory_repository():
    """Verifies that the in-memory repository saves and queries correctly."""
    repo = InMemoryServiceCatalogueRepository()

    item_active = ServiceCatalogueItem(
        service_catalogue_id="SVC-ACTIVE",
        service_name="Active Service",
        service_code="CODE-ACTIVE",
        responsible_mda_placeholder="NIRA",
        service_category=ServiceCategory.IDENTITY_SERVICES,
        service_description="Desc",
        required_documents=[],
        fee_required=False,
        default_fee_amount=0.0,
        active_status=ActiveStatus.ACTIVE
    )

    item_demo = ServiceCatalogueItem(
        service_catalogue_id="SVC-DEMO",
        service_name="Demo Service",
        service_code="CODE-DEMO",
        responsible_mda_placeholder="IG",
        service_category=ServiceCategory.CITIZEN_COMPLAINTS,
        service_description="Desc",
        required_documents=[],
        fee_required=False,
        default_fee_amount=0.0,
        active_status=ActiveStatus.DEMO_ONLY
    )

    repo.save(item_active)
    repo.save(item_demo)

    assert repo.get_by_id("SVC-ACTIVE") == item_active
    assert repo.get_by_code("CODE-DEMO") == item_demo
    assert repo.get_by_code("NON-EXISTENT") is None

    assert len(repo.get_all()) == 2
    assert repo.get_active() == [item_active]
    assert repo.get_demo() == [item_demo]
    assert repo.get_by_category(ServiceCategory.IDENTITY_SERVICES) == [item_active]
    assert repo.get_by_category(ServiceCategory.CITIZEN_COMPLAINTS) == [item_demo]


def test_create_service_catalogue_item_use_case():
    """Verifies CreateServiceCatalogueItem use case saves new items."""
    repo = InMemoryServiceCatalogueRepository()
    use_case = CreateServiceCatalogueItem(repo)

    item = use_case.execute(
        service_catalogue_id="SVC-LOST-NID",
        service_name="Lost National ID Replacement",
        service_code="LOST_NATIONAL_ID",
        responsible_mda_placeholder="NIRA",
        service_category=ServiceCategory.IDENTITY_SERVICES,
        service_description="Replacement Card",
        required_documents=["Police Letter Placeholder"],
        fee_required=True,
        default_fee_amount=50000.0,
        default_payment_provider=PaymentProviderOption.SIMULATED,
        timestamp=500.0
    )

    assert item.service_catalogue_id == "SVC-LOST-NID"
    assert repo.get_by_id("SVC-LOST-NID") == item
    assert item.created_at == 500.0
    assert item.updated_at == 500.0


def test_update_service_catalogue_item_use_case():
    """Verifies UpdateServiceCatalogueItem use case modifies existing fields."""
    repo = InMemoryServiceCatalogueRepository()
    item = ServiceCatalogueItem(
        service_catalogue_id="SVC-LOST-NID",
        service_name="Lost National ID Replacement",
        service_code="LOST_NATIONAL_ID",
        responsible_mda_placeholder="NIRA",
        service_category=ServiceCategory.IDENTITY_SERVICES,
        service_description="Desc",
        required_documents=[],
        fee_required=False,
        default_fee_amount=0.0
    )
    repo.save(item)

    use_case = UpdateServiceCatalogueItem(repo)

    # Valid updates
    updates = {
        "service_name": "New Service Name",
        "service_code": "NEW_CODE",
        "fee_required": True,
        "default_fee_amount": 15000.0,
        "default_payment_provider": PaymentProviderOption.PESAPAL_SANDBOX,
        "service_category": ServiceCategory.CITIZEN_COMPLAINTS,
        "workflow_template": WorkflowTemplate.COMPLAINT,
        "active_status": ActiveStatus.RETIRED
    }

    updated_item = use_case.execute("SVC-LOST-NID", updates, timestamp=600.0)

    assert updated_item.service_name == "New Service Name"
    assert updated_item.service_code == "NEW_CODE"
    assert updated_item.fee_required is True
    assert updated_item.default_fee_amount == 15000.0
    assert updated_item.default_payment_provider == PaymentProviderOption.PESAPAL_SANDBOX
    assert updated_item.service_category == ServiceCategory.CITIZEN_COMPLAINTS
    assert updated_item.workflow_template == WorkflowTemplate.COMPLAINT
    assert updated_item.active_status == ActiveStatus.RETIRED
    assert updated_item.updated_at == 600.0

    # Non-existent item check
    with pytest.raises(ValueError, match="not found"):
        use_case.execute("SVC-NON-EXISTENT", {})

    # Invalid category check
    with pytest.raises(ValueError, match="Invalid service category"):
        use_case.execute("SVC-LOST-NID", {"service_category": "Invalid"})

    # Invalid payment provider check
    with pytest.raises(ValueError, match="Invalid payment provider"):
        use_case.execute("SVC-LOST-NID", {"default_payment_provider": "Invalid"})


def test_list_services_use_case():
    """Verifies ListServices queries and filters catalogue items."""
    repo = InMemoryServiceCatalogueRepository()
    use_case = ListServices(repo)

    item1 = ServiceCatalogueItem("SVC-1", "S1", "C1", "M1", ServiceCategory.IDENTITY_SERVICES, "D", [], False, 0.0, active_status=ActiveStatus.ACTIVE)
    item2 = ServiceCatalogueItem("SVC-2", "S2", "C2", "M2", ServiceCategory.CITIZEN_COMPLAINTS, "D", [], False, 0.0, active_status=ActiveStatus.DEMO_ONLY)

    repo.save(item1)
    repo.save(item2)

    assert use_case.execute() == [item1, item2]
    assert use_case.execute(filter_by="active") == [item1]
    assert use_case.execute(filter_by="demo") == [item2]
    assert use_case.execute(filter_by="category", value=ServiceCategory.IDENTITY_SERVICES) == [item1]

    with pytest.raises(ValueError, match="Category value is required"):
        use_case.execute(filter_by="category")


def test_manage_service_status_use_case():
    """Verifies ManageServiceStatus transitions and saves status."""
    repo = InMemoryServiceCatalogueRepository()
    item = ServiceCatalogueItem("SVC-1", "S1", "C1", "M1", ServiceCategory.IDENTITY_SERVICES, "D", [], False, 0.0)
    repo.save(item)

    use_case = ManageServiceStatus(repo)

    use_case.execute("SVC-1", "deactivate", timestamp=100.0)
    assert item.active_status == ActiveStatus.INACTIVE

    use_case.execute("SVC-1", "activate", timestamp=200.0)
    assert item.active_status == ActiveStatus.ACTIVE

    use_case.execute("SVC-1", "mark_demo_only", timestamp=300.0)
    assert item.active_status == ActiveStatus.DEMO_ONLY

    with pytest.raises(ValueError, match="Invalid status transition action"):
        use_case.execute("SVC-1", "invalid_action")


def test_retrieve_service_by_code_use_case():
    """Verifies RetrieveServiceByCode queries correctly."""
    repo = InMemoryServiceCatalogueRepository()
    item = ServiceCatalogueItem("SVC-1", "S1", "C1", "M1", ServiceCategory.IDENTITY_SERVICES, "D", [], False, 0.0)
    repo.save(item)

    use_case = RetrieveServiceByCode(repo)
    assert use_case.execute("C1") == item
    assert use_case.execute("NON-EXISTENT") is None

    with pytest.raises(ValueError, match="Service code is required"):
        use_case.execute("")


def test_apply_catalogue_defaults_use_case():
    """Verifies ApplyCatalogueDefaults synchronizes defaults to service requests and payment records."""
    repo = InMemoryServiceCatalogueRepository()
    sla_repo = MagicMock()
    use_case = ApplyCatalogueDefaults(repo, sla_repo)

    # Configure active catalogue item
    item = ServiceCatalogueItem(
        service_catalogue_id="SVC-LOST-NID",
        service_name="Lost National ID Replacement",
        service_code="LOST_NATIONAL_ID",
        responsible_mda_placeholder="NIRA",
        service_category=ServiceCategory.IDENTITY_SERVICES,
        service_description="Desc",
        required_documents=["Police Letter Placeholder", "Affidavit Placeholder"],
        fee_required=True,
        default_fee_amount=50000.0,
        default_payment_purpose="National ID Replacement Fee",
        default_payment_provider=PaymentProviderOption.PESAPAL_SANDBOX,
        default_sla_rule="SLA-LOST-NID",
        responsible_department="National ID Replacement Desk",
        responsible_queue="National ID Replacement Desk"
    )
    repo.save(item)

    # Configure mock SLA rule
    mock_rule = SLARule(
        rule_id="SLA-LOST-NID",
        service_type="LOST_NATIONAL_ID",
        response_hours=4,
        resolution_hours=48,
        escalation_threshold_hours=2,
        escalation_queue="Supervisor Queue",
        escalation_role="supervisor_role"
    )
    sla_repo.get_by_id.return_value = mock_rule

    # 1. Apply defaults to ServiceRequest
    req = ServiceRequest(
        request_id="req-1",
        reference_no="REF-001",
        citizen_nin=NIN("CF900000000000"),
        citizen_name="Demo User",
        phone_number="+256700000001",
        location="Kampala",
        description="Lost",
        email="demo@example.com",
        citizen_profile_id="CP-001"
    )

    use_case.execute_request_defaults(req, "LOST_NATIONAL_ID", timestamp=100.0)

    assert req.service_catalogue_item_id == "SVC-LOST-NID"
    assert req.assigned_department == "National ID Replacement Desk"
    assert req.queue_name == "National ID Replacement Desk"
    assert req.payment_status == "Pending"
    assert req.payment_amount == 50000.0
    assert req.sla_rule_id == "SLA-LOST-NID"
    assert req.sla_deadline is not None

    # 2. Apply defaults to PaymentRecord
    pay = PaymentRecord(
        payment_record_id="PAY-1",
        service_request_id="req-1",
        amount=0.0
    )

    use_case.execute_payment_defaults(pay, "LOST_NATIONAL_ID")

    assert pay.amount == 50000.0
    assert pay.payment_purpose == "National ID Replacement Fee"
    assert pay.provider == "Pesapal Sandbox"
    assert pay.provider_mode == "sandbox"

    # Test simulated default payment provider
    item.default_payment_provider = PaymentProviderOption.SIMULATED
    repo.save(item)
    pay2 = PaymentRecord(payment_record_id="PAY-2", service_request_id="req-1", amount=0.0)
    use_case.execute_payment_defaults(pay2, "LOST_NATIONAL_ID")
    assert pay2.amount == 50000.0
    assert pay2.provider == "Simulated"

    # Test fee not required
    item.fee_required = False
    repo.save(item)
    use_case.execute_request_defaults(req, "LOST_NATIONAL_ID", timestamp=100.0)
    assert req.payment_status == "Not Required"
    assert req.payment_amount == 0.0

    pay3 = PaymentRecord(payment_record_id="PAY-3", service_request_id="req-1", amount=5000.0)
    use_case.execute_payment_defaults(pay3, "LOST_NATIONAL_ID")
    assert pay3.amount == 0.0
    assert pay3.payment_purpose == "Not Applicable"
    assert pay3.payment_status == "Not Required"
    assert pay3.verification_status == "Not Applicable"

    # 3. Check evidence checklist requirements
    # Missing both
    res1 = use_case.check_evidence_requirements("LOST_NATIONAL_ID", [])
    assert res1["complete"] is False
    assert res1["missing"] == ["Police Letter Placeholder", "Affidavit Placeholder"]

    # Partial completeness
    res2 = use_case.check_evidence_requirements("LOST_NATIONAL_ID", ["Police Letter Placeholder"])
    assert res2["complete"] is False
    assert res2["missing"] == ["Affidavit Placeholder"]

    # Full completeness
    res3 = use_case.check_evidence_requirements("LOST_NATIONAL_ID", ["Police Letter Placeholder", "Affidavit Placeholder"])
    assert res3["complete"] is True
    assert res3["missing"] == []


@patch("nilegov_stack.infrastructure.repositories.frappe_service_catalogue_repository.frappe")
def test_frappe_service_catalogue_repository(mock_frappe):
    """Verifies that FrappeServiceCatalogueRepository maps DocType properties correctly."""
    # Setup mocks
    mock_frappe.db.exists.return_value = True
    mock_doc = MagicMock()
    mock_doc.service_catalogue_id = "SVC-LOST-NID"
    mock_doc.name = "SVC-LOST-NID"
    mock_doc.service_name = "Lost National ID Replacement"
    mock_doc.service_code = "LOST_NATIONAL_ID"
    mock_doc.responsible_mda_placeholder = "NIRA"
    mock_doc.service_category = "Identity Services"
    mock_doc.service_description = "Desc"
    mock_doc.required_documents = "Police Letter Placeholder, Affidavit Placeholder"
    mock_doc.fee_required = 1
    mock_doc.default_fee_amount = 50000.0
    mock_doc.default_currency = "UGX"
    mock_doc.default_payment_purpose = "National ID Replacement Fee"
    mock_doc.default_payment_provider = "Simulated"
    mock_doc.default_sla_rule = "SLA-LOST-NID"
    mock_doc.responsible_department = "NIRA Dept"
    mock_doc.responsible_queue = "NIRA Queue"
    mock_doc.workflow_template = "Standard Application Workflow"
    mock_doc.active_status = "Active"
    mock_doc.public_visibility = "Demo Visible"
    mock_doc.creation = "2026-06-02 12:00:00"
    mock_doc.modified = "2026-06-02 12:00:00"

    mock_frappe.get_doc.return_value = mock_doc
    mock_frappe.utils.get_timestamp.return_value = 1772539200.0

    repo = FrappeServiceCatalogueRepository()
    item = repo.get_by_id("SVC-LOST-NID")

    assert item is not None
    assert item.service_catalogue_id == "SVC-LOST-NID"
    assert item.service_name == "Lost National ID Replacement"
    assert item.required_documents == ["Police Letter Placeholder", "Affidavit Placeholder"]
    assert item.fee_required is True
    assert item.default_fee_amount == 50000.0
    assert item.default_payment_provider == PaymentProviderOption.SIMULATED

    # Test save mapping
    new_item = ServiceCatalogueItem(
        service_catalogue_id="SVC-NEW",
        service_name="New Service",
        service_code="CODE-NEW",
        responsible_mda_placeholder="NIRA",
        service_category=ServiceCategory.IDENTITY_SERVICES,
        service_description="Desc",
        required_documents=["Doc1", "Doc2"],
        fee_required=True,
        default_fee_amount=1000.0,
        default_payment_provider=PaymentProviderOption.SIMULATED
    )

    new_doc_mock = MagicMock()
    mock_frappe.new_doc.return_value = new_doc_mock
    mock_frappe.db.exists.return_value = False

    repo.save(new_item)

    mock_frappe.new_doc.assert_called_with("NileGov Service Catalogue")
    assert new_doc_mock.service_catalogue_id == "SVC-NEW"
    assert new_doc_mock.service_name == "New Service"
    assert new_doc_mock.service_code == "CODE-NEW"
    assert new_doc_mock.required_documents == "Doc1, Doc2"
    assert new_doc_mock.fee_required == 1
    assert new_doc_mock.default_fee_amount == 1000.0
    assert new_doc_mock.default_payment_provider == "Simulated"
    new_doc_mock.save.assert_called_once()
