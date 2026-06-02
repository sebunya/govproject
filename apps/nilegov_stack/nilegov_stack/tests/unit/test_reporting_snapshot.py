# Unit Tests for NileGov M&E Reporting Foundation
# Digi-Verse Uganda Limited
# Prototype reporting snapshot only. Metrics are calculated from fictional demo data and are not official government statistics.

import pytest
import time
from unittest.mock import MagicMock, patch

from nilegov_stack.domain.reporting_snapshot import ReportingSnapshot
from nilegov_stack.domain.service_request import ServiceRequest
from nilegov_stack.domain.service_catalogue import ServiceCatalogueItem
from nilegov_stack.domain.evidence import EvidenceDocument
from nilegov_stack.domain.payment import PaymentRecord
from nilegov_stack.domain.notification import NotificationEvent
from nilegov_stack.domain.value_objects import NIN

from nilegov_stack.application.generate_reporting_snapshot import GenerateReportingSnapshot

from nilegov_stack.infrastructure.repositories.service_request_repository import InMemoryServiceRequestRepository
from nilegov_stack.infrastructure.repositories.service_catalogue_repository import InMemoryServiceCatalogueRepository
from nilegov_stack.infrastructure.repositories.evidence_document_repository import InMemoryEvidenceDocumentRepository
from nilegov_stack.infrastructure.repositories.payment_record_repository import InMemoryPaymentRecordRepository
from nilegov_stack.infrastructure.repositories.notification_event_repository import InMemoryNotificationEventRepository
from nilegov_stack.infrastructure.repositories.reporting_snapshot_repository import InMemoryReportingSnapshotRepository
from nilegov_stack.infrastructure.repositories.frappe_reporting_snapshot_repository import FrappeReportingSnapshotRepository


def test_reporting_snapshot_creation_and_validation():
    """Verifies ReportingSnapshot aggregate validation constraints."""
    # Valid snapshot
    snap = ReportingSnapshot(
        reporting_snapshot_id="SNAP-001",
        snapshot_name="Daily Snapshot",
        reporting_period_start=100.0,
        reporting_period_end=200.0,
        generated_at=200.0,
        generated_by="officer_demo",
        source_dataset="Demo Data",
        total_requests=10,
        total_services=3,
        active_services=2,
        demo_services=1,
        requests_by_status={},
        requests_by_service={},
        requests_by_queue={},
        requests_by_location={},
        within_sla_count=8,
        at_risk_count=1,
        overdue_count=1,
        escalated_count=1,
        evidence_complete_count=9,
        evidence_incomplete_count=1,
        evidence_rejected_count=0,
        evidence_requiring_replacement_count=0
    )

    assert snap.reporting_snapshot_id == "SNAP-001"
    assert snap.snapshot_name == "Daily Snapshot"
    assert snap.disclaimer == "Prototype reporting snapshot only. Metrics are calculated from fictional demo data and are not official government statistics."

    # Invalid: empty name
    with pytest.raises(ValueError, match="Snapshot name is required"):
        ReportingSnapshot(
            reporting_snapshot_id="SNAP-001",
            snapshot_name="",
            reporting_period_start=100.0,
            reporting_period_end=200.0,
            generated_at=200.0,
            generated_by="officer",
            source_dataset="Demo",
            total_requests=10,
            total_services=3,
            active_services=2,
            demo_services=1,
            requests_by_status={},
            requests_by_service={},
            requests_by_queue={},
            requests_by_location={},
            within_sla_count=8,
            at_risk_count=1,
            overdue_count=1,
            escalated_count=1,
            evidence_complete_count=9,
            evidence_incomplete_count=1
        )

    # Invalid: period start > end
    with pytest.raises(ValueError, match="Reporting period start must be before end"):
        ReportingSnapshot(
            reporting_snapshot_id="SNAP-001",
            snapshot_name="Name",
            reporting_period_start=300.0,
            reporting_period_end=200.0,
            generated_at=200.0,
            generated_by="officer",
            source_dataset="Demo",
            total_requests=10,
            total_services=3,
            active_services=2,
            demo_services=1,
            requests_by_status={},
            requests_by_service={},
            requests_by_queue={},
            requests_by_location={},
            within_sla_count=8,
            at_risk_count=1,
            overdue_count=1,
            escalated_count=1,
            evidence_complete_count=9,
            evidence_incomplete_count=1
        )

    # Invalid: negative total requests
    with pytest.raises(ValueError, match="Total requests cannot be negative"):
        ReportingSnapshot(
            reporting_snapshot_id="SNAP-001",
            snapshot_name="Name",
            reporting_period_start=100.0,
            reporting_period_end=200.0,
            generated_at=200.0,
            generated_by="officer",
            source_dataset="Demo",
            total_requests=-5,
            total_services=3,
            active_services=2,
            demo_services=1,
            requests_by_status={},
            requests_by_service={},
            requests_by_queue={},
            requests_by_location={},
            within_sla_count=8,
            at_risk_count=1,
            overdue_count=1,
            escalated_count=1,
            evidence_complete_count=9,
            evidence_incomplete_count=1
        )


def test_generate_reporting_snapshot_empty_dataset():
    """Verifies that compiling an empty dataset produces safe zero metrics."""
    req_repo = InMemoryServiceRequestRepository()
    cat_repo = InMemoryServiceCatalogueRepository()
    ev_repo = InMemoryEvidenceDocumentRepository()
    pay_repo = InMemoryPaymentRecordRepository()
    notif_repo = InMemoryNotificationEventRepository()
    snap_repo = InMemoryReportingSnapshotRepository()

    use_case = GenerateReportingSnapshot(
        req_repo, cat_repo, ev_repo, pay_repo, notif_repo, snap_repo
    )

    snap = use_case.execute(
        snapshot_id="SNAP-EMPTY",
        snapshot_name="Empty Snapshot",
        period_start=1000.0,
        period_end=2000.0,
        generated_by="officer_demo",
        timestamp=1500.0
    )

    assert snap.reporting_snapshot_id == "SNAP-EMPTY"
    assert snap.total_requests == 0
    assert snap.total_services == 0
    assert snap.active_services == 0
    assert snap.demo_services == 0
    assert snap.within_sla_count == 0
    assert snap.at_risk_count == 0
    assert snap.overdue_count == 0
    assert snap.escalated_count == 0
    assert snap.evidence_complete_count == 0
    assert snap.evidence_incomplete_count == 0
    assert snap.evidence_rejected_count == 0
    assert snap.evidence_requiring_replacement_count == 0
    assert snap.payment_pending_count == 0
    assert snap.payment_verified_count == 0
    assert snap.payment_failed_count == 0
    assert snap.notification_draft_count == 0
    assert snap.notification_queued_count == 0
    assert snap.notification_simulated_sent_count == 0
    assert snap.notification_failed_count == 0
    assert snap.notification_cancelled_count == 0
    assert snap.notification_not_required_count == 0
    assert snap.officer_workload_summary == {}
    assert snap.payment_value_summary["total_simulated_payment_value"] == 0.0


def test_generate_reporting_snapshot_success():
    """Verifies that all metrics groups are aggregated correctly from repositories."""
    req_repo = InMemoryServiceRequestRepository()
    cat_repo = InMemoryServiceCatalogueRepository()
    ev_repo = InMemoryEvidenceDocumentRepository()
    pay_repo = InMemoryPaymentRecordRepository()
    notif_repo = InMemoryNotificationEventRepository()
    snap_repo = InMemoryReportingSnapshotRepository()

    # 1. Seed Service Catalogue
    cat_item = ServiceCatalogueItem(
        service_catalogue_id="SVC-LOST-NID",
        service_name="Lost NID",
        service_code="LOST_NATIONAL_ID",
        responsible_mda_placeholder="NIRA",
        service_category="Identity Services",
        service_description="Desc",
        required_documents=["Police Letter", "Affidavit"],
        fee_required=True,
        default_fee_amount=50000.0,
        active_status="Active"
    )
    cat_repo.save(cat_item)

    # 2. Seed Service Request (Within SLA, with verified payment, complete evidence)
    req1 = ServiceRequest(
        request_id="req-1",
        reference_no="NGS-NIRA-2026-0001",
        citizen_nin=NIN("CF900000000000"),
        citizen_name="Demo User A",
        phone_number="+256700000001",
        location="Ntinda",
        description="Lost ID",
        citizen_profile_id="CP-001"
    )
    req1.service_type = "LOST_NATIONAL_ID"
    req1.status = "Under Review"
    req1.queue_name = "Verification Desk"
    req1.assigned_officer_id = "officer_demo"
    req1.sla_state = "Within SLA"
    req_repo.save(req1)

    # 3. Seed Service Request (Overdue, payment pending, incomplete evidence)
    req2 = ServiceRequest(
        request_id="req-2",
        reference_no="NGS-NIRA-2026-0002",
        citizen_nin=NIN("CF900000000001"),
        citizen_name="Demo User B",
        phone_number="+256700000002",
        location="Bukoto",
        description="Lost ID",
        citizen_profile_id="CP-002"
    )
    req2.service_type = "LOST_NATIONAL_ID"
    req2.status = "Payment Pending"
    req2.queue_name = "Payment Review Desk"
    req2.assigned_officer_id = "officer_review"
    req2.sla_state = "Overdue"
    req2.assignment_status = "Supervisor Review"  # Triggers escalated metric
    req_repo.save(req2)

    # 4. Seed Evidences (complete for req1, incomplete/rejected for req2)
    ev1 = EvidenceDocument(
        evidence_document_id="EVI-1",
        citizen_profile_id="CP-001",
        service_request_id="req-1",
        document_type="Police Letter",
        document_title="Title",
        file="file.pdf",
        upload_channel="Web Form",
        uploaded_by="Administrator",
        uploaded_at=1700000000.0
    )
    ev1.verification_status = "Accepted"
    ev_repo.save(ev1)

    ev2 = EvidenceDocument(
        evidence_document_id="EVI-2",
        citizen_profile_id="CP-001",
        service_request_id="req-1",
        document_type="Affidavit",
        document_title="Title",
        file="file.pdf",
        upload_channel="Web Form",
        uploaded_by="Administrator",
        uploaded_at=1700000000.0
    )
    ev2.verification_status = "Accepted"
    ev_repo.save(ev2)

    ev3 = EvidenceDocument(
        evidence_document_id="EVI-3",
        citizen_profile_id="CP-002",
        service_request_id="req-2",
        document_type="Police Letter",
        document_title="Title",
        file="file.pdf",
        upload_channel="Web Form",
        uploaded_by="Administrator",
        uploaded_at=1700000000.0
    )
    ev3.verification_status = "Rejected"
    ev_repo.save(ev3)

    ev4 = EvidenceDocument(
        evidence_document_id="EVI-4",
        citizen_profile_id="CP-002",
        service_request_id="req-2",
        document_type="Other",
        document_title="Title",
        file="file.pdf",
        upload_channel="Web Form",
        uploaded_by="Administrator",
        uploaded_at=1700000000.0
    )
    ev4.verification_status = "Requires Replacement"
    ev_repo.save(ev4)

    # 5. Seed Payments
    pay1 = PaymentRecord("PAY-1", "req-1", 50000.0)
    pay1.payment_status = "Verified"
    pay_repo.save(pay1)

    # Note: InMemoryPaymentRecordRepository mock data requires request mapping
    pay2 = PaymentRecord("PAY-2", "req-2", 50000.0)
    pay2.payment_status = "Pending"
    pay_repo.save(pay2)

    pay3 = PaymentRecord("PAY-3", "req-3", 25000.0)
    pay3.payment_status = "Failed"
    pay_repo.save(pay3)

    # 6. Seed Notifications
    notif1 = NotificationEvent(
        notification_event_id="NOT-1",
        service_request_id="req-1",
        recipient="+256700000001",
        channel="SMS",
        message="Msg",
        delivery_status="Simulated Sent",
        citizen_profile_id="CP-001",
        message_type="Request Received"
    )
    notif_repo.save(notif1)

    notif2 = NotificationEvent(
        notification_event_id="NOT-2",
        service_request_id="req-2",
        recipient="+256700000002",
        channel="Email",
        message="Msg",
        delivery_status="Queued",
        citizen_profile_id="CP-002",
        message_type="SLA Overdue"
    )
    notif_repo.save(notif2)

    # Compile snapshot
    use_case = GenerateReportingSnapshot(
        req_repo, cat_repo, ev_repo, pay_repo, notif_repo, snap_repo
    )

    snap = use_case.execute(
        snapshot_id="SNAP-DAILY-001",
        snapshot_name="Daily Report",
        period_start=100.0,
        period_end=500.0,
        generated_by="officer_demo",
        timestamp=300.0
    )

    # Assertions
    assert snap.total_requests == 2
    assert snap.total_services == 1
    assert snap.active_services == 1

    # Breakdown assertions
    assert snap.requests_by_status["Under Review"] == 1
    assert snap.requests_by_status["Payment Pending"] == 1
    assert snap.requests_by_service["LOST_NATIONAL_ID"] == 2
    assert snap.requests_by_queue["Verification Desk"] == 1
    assert snap.requests_by_location["Ntinda"] == 1
    assert snap.requests_by_location["Bukoto"] == 1

    # SLA assertions
    assert snap.within_sla_count == 1
    assert snap.overdue_count == 1
    assert snap.escalated_count == 1  # req2 is supervisor review assignment

    # Evidence assertions
    assert snap.evidence_complete_count == 1  # req-1 has both accepted docs
    assert snap.evidence_incomplete_count == 1  # req-2 lacks accepted Affidavit
    assert snap.evidence_rejected_count == 1  # ev3 is Rejected
    assert snap.evidence_requiring_replacement_count == 1  # ev4 is Requires Replacement

    # Payment assertions
    assert snap.payment_pending_count == 1
    assert snap.payment_verified_count == 1
    assert snap.payment_failed_count == 1
    assert snap.payment_value_summary["total_simulated_payment_value"] == 50000.0

    # Notification assertions
    assert snap.notification_queued_count == 1
    assert snap.notification_simulated_sent_count == 1

    # Workload assertions
    assert snap.officer_workload_summary["officer_demo"] == 1
    assert snap.officer_workload_summary["officer_review"] == 1


@patch("nilegov_stack.infrastructure.repositories.frappe_reporting_snapshot_repository.frappe")
def test_frappe_reporting_snapshot_repository(mock_frappe):
    """Verifies that FrappeReportingSnapshotRepository handles serialization mapping when simulated database exists."""
    # Mock database table exists check
    mock_frappe.db.table_exists.return_value = True
    mock_frappe.db.exists.return_value = True

    mock_doc = MagicMock()
    mock_doc.reporting_snapshot_id = "SNAP-1"
    mock_doc.snapshot_name = "Name"
    mock_doc.reporting_period_start = 100.0
    mock_doc.reporting_period_end = 200.0
    mock_doc.generated_at = 150.0
    mock_doc.generated_by = "officer"
    mock_doc.source_dataset = "Demo"
    mock_doc.total_requests = 10
    mock_doc.total_services = 5
    mock_doc.active_services = 4
    mock_doc.demo_services = 1
    mock_doc.requests_by_status = '{"Under Review": 10}'
    mock_doc.requests_by_service = '{"LOST_NATIONAL_ID": 10}'
    mock_doc.requests_by_queue = '{"Verification Desk": 10}'
    mock_doc.requests_by_location = '{"Ntinda": 10}'
    mock_doc.within_sla_count = 10
    mock_doc.at_risk_count = 0
    mock_doc.overdue_count = 0
    mock_doc.escalated_count = 0
    mock_doc.evidence_complete_count = 10
    mock_doc.evidence_incomplete_count = 0
    mock_doc.evidence_rejected_count = 0
    mock_doc.evidence_requiring_replacement_count = 0
    mock_doc.payment_pending_count = 0
    mock_doc.payment_verified_count = 10
    mock_doc.payment_failed_count = 0
    mock_doc.notification_draft_count = 0
    mock_doc.notification_queued_count = 0
    mock_doc.notification_simulated_sent_count = 10
    mock_doc.notification_failed_count = 0
    mock_doc.notification_cancelled_count = 0
    mock_doc.notification_not_required_count = 0
    mock_doc.officer_workload_summary = '{"officer_demo": 10}'
    mock_doc.payment_value_summary = '{"total_simulated_payment_value": 50000.0}'
    mock_doc.disclaimer = "Prototype reporting snapshot only."
    mock_doc.creation = "2026-06-02 12:00:00"
    mock_doc.modified = "2026-06-02 12:00:00"

    mock_frappe.get_doc.return_value = mock_doc

    repo = FrappeReportingSnapshotRepository()
    snap = repo.get_by_id("SNAP-1")

    assert snap is not None
    assert snap.reporting_snapshot_id == "SNAP-1"
    assert snap.requests_by_status == {"Under Review": 10}
    assert snap.payment_value_summary == {"total_simulated_payment_value": 50000.0}
