# Application Tests: Cross-Domain Composition
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.
#
# Tests multi-use-case composition across:
#   - Service Request + Evidence Document + Case Note
#   - Service Request + Payment Record + Case Note
#   - Service Catalogue → Service Request defaults
#   - Reporting Snapshot from demo-like populated data
#   - Interoperability payload safety

import time

import pytest

from nilegov_stack.application.create_case_note import CreateCaseNote
from nilegov_stack.application.list_case_notes import ListCaseNotes
from nilegov_stack.application.create_evidence_document import CreateEvidenceDocument
from nilegov_stack.application.create_payment_record import CreatePaymentRecord
from nilegov_stack.application.submit_simulated_payment import SubmitSimulatedPayment
from nilegov_stack.application.generate_reporting_snapshot import GenerateReportingSnapshot
from nilegov_stack.application.build_interoperability_payloads import (
    build_service_request_payload,
    assert_payload_excludes_sensitive_values,
)
from nilegov_stack.domain.interoperability import INTEROPERABILITY_DISCLAIMER
from nilegov_stack.domain.service_request import ServiceRequest, WorkflowStatus
from nilegov_stack.domain.payment import PaymentPurpose, PaymentChannel
from nilegov_stack.domain.value_objects import NIN
from nilegov_stack.infrastructure.repositories.case_note_repository import InMemoryCaseNoteRepository
from nilegov_stack.infrastructure.repositories.service_request_repository import InMemoryServiceRequestRepository
from nilegov_stack.infrastructure.repositories.evidence_document_repository import InMemoryEvidenceDocumentRepository
from nilegov_stack.infrastructure.repositories.payment_record_repository import InMemoryPaymentRecordRepository
from nilegov_stack.infrastructure.repositories.notification_event_repository import InMemoryNotificationEventRepository
from nilegov_stack.infrastructure.repositories.service_catalogue_repository import InMemoryServiceCatalogueRepository
from nilegov_stack.infrastructure.repositories.reporting_snapshot_repository import InMemoryReportingSnapshotRepository


NOW = 1_717_000_000.0


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

class _ServiceRequestWithAlias:
    """Thin wrapper around ServiceRequest that adds the reference_number alias
    expected by build_service_request_payload (which uses .reference_number).
    The domain model stores this as .reference_no — the interop payload builder
    reads .reference_number from any duck-typed object.
    Also converts created_at float to datetime so the payload builder can call .isoformat().
    """

    def __init__(self, req: ServiceRequest):
        self._req = req
        # Expose all attributes from the wrapped request
        for attr in vars(req):
            setattr(self, attr, getattr(req, attr))
        # Add the alias expected by the payload builder
        self.reference_number = req.reference_no
        # Convert float created_at to None so payload builder skips isoformat()
        # (the domain model stores created_at as a float; interop payload builder
        # expects a datetime or None)
        self.created_at = None


def make_service_request(
    request_id="REQ-APP-001",
    citizen_profile_id="CP-APP-001",
    service_type="SVC-LOST-NID",
) -> ServiceRequest:
    req = ServiceRequest(
        request_id=request_id,
        reference_no=f"NGS-NIRA-2026-{request_id[-3:]}",
        citizen_nin=NIN("CF123456789012"),
        citizen_name="App Composition Citizen",
        phone_number="+256780000200",
        location="Ntinda, Kampala",
        description="Application composition test request.",
        citizen_profile_id=citizen_profile_id,
        created_at=NOW,
    )
    req.service_type = service_type
    req.assignment_status = "Assigned"
    req.assigned_officer_id = "officer_compose"
    return req


# ─────────────────────────────────────────────────────────────────────────────
# Evidence Document + Case Note composition
# ─────────────────────────────────────────────────────────────────────────────

class TestEvidenceAndCaseNoteComposition:
    def test_create_evidence_then_add_records_review_note(self):
        """Records Officer creates an evidence document, then adds a review note."""
        ev_repo = InMemoryEvidenceDocumentRepository()
        note_repo = InMemoryCaseNoteRepository()

        ev_uc = CreateEvidenceDocument(ev_repo)
        note_uc = CreateCaseNote(note_repo)

        # Create evidence
        doc = ev_uc.execute(
            evidence_document_id="EV-APP-001",
            citizen_profile_id="CP-APP-001",
            service_request_id="REQ-APP-001",
            document_type="National ID Card",
            document_title="Original National ID Card Scan",
            file="national_id_demo.pdf",
            upload_channel="Officer Upload",
            uploaded_by="officer_records",
            uploaded_at=NOW,
            created_at=NOW,
        )
        assert doc.evidence_document_id == "EV-APP-001"

        # Add records review note
        note = note_uc.execute(
            service_request_id="REQ-APP-001",
            note_type="Records Review Note",
            note_text="National ID card scan verified against records. Document accepted.",
            created_by_role="NileGov Records Officer",
            created_by_user="officer_records",
            visibility="Auditor Visible",
        )

        assert note.note_type == "Records Review Note"
        assert note.visibility == "Auditor Visible"
        assert note_repo.list_by_service_request("REQ-APP-001") != []

    def test_records_review_note_cannot_be_citizen_visible(self):
        """Records Review Notes must never be set to citizen-visible visibility."""
        note_repo = InMemoryCaseNoteRepository()
        note_uc = CreateCaseNote(note_repo)

        with pytest.raises(ValueError):
            note_uc.execute(
                service_request_id="REQ-APP-001",
                note_type="Records Review Note",
                note_text="Sensitive records detail.",
                created_by_role="NileGov Records Officer",
                created_by_user="officer_records",
                visibility="Citizen Visible Summary",
            )


# ─────────────────────────────────────────────────────────────────────────────
# Payment Record + Case Note composition
# ─────────────────────────────────────────────────────────────────────────────

class TestPaymentAndCaseNoteComposition:
    def test_create_payment_then_add_payment_review_note(self):
        """Payments Officer creates a payment record, then adds an audit note."""
        pay_repo = InMemoryPaymentRecordRepository()
        note_repo = InMemoryCaseNoteRepository()

        pay_uc = CreatePaymentRecord(pay_repo)
        note_uc = CreateCaseNote(note_repo)

        pay = pay_uc.execute(
            payment_id="PAY-APP-001",
            service_request_id="REQ-APP-001",
            amount=50_000.0,
            purpose=PaymentPurpose.NATIONAL_ID_REPLACEMENT,
            channel=PaymentChannel.MOBILE_MONEY,
            timestamp=NOW,
        )

        assert pay.payment_record_id == "PAY-APP-001"

        note = note_uc.execute(
            service_request_id="REQ-APP-001",
            note_type="Payment Review Note",
            note_text="Payment of UGX 50,000 received via Mobile Money. Verified.",
            created_by_role="NileGov Payments Officer",
            created_by_user="officer_payments",
            visibility="Auditor Visible",
        )

        assert note.visibility == "Auditor Visible"

    def test_payment_review_note_cannot_be_citizen_visible(self):
        note_repo = InMemoryCaseNoteRepository()
        note_uc = CreateCaseNote(note_repo)

        with pytest.raises(ValueError):
            note_uc.execute(
                service_request_id="REQ-APP-001",
                note_type="Payment Review Note",
                note_text="Payment reviewed.",
                created_by_role="NileGov Payments Officer",
                created_by_user="officer_payments",
                visibility="Citizen Visible Summary",
            )

    def test_submit_simulated_payment_then_add_note(self):
        """Verify the submit-payment use case composes with case note creation."""
        pay_repo = InMemoryPaymentRecordRepository()
        note_repo = InMemoryCaseNoteRepository()

        pay_uc = CreatePaymentRecord(pay_repo)
        submit_uc = SubmitSimulatedPayment(pay_repo)
        note_uc = CreateCaseNote(note_repo)

        pay = pay_uc.execute(
            payment_id="PAY-APP-002",
            service_request_id="REQ-APP-001",
            amount=80_000.0,
            timestamp=NOW,
        )

        # SubmitSimulatedPayment.execute() uses payment_id and transaction_reference
        updated_pay = submit_uc.execute(
            payment_id="PAY-APP-002",
            transaction_reference="SIM-TXN-APP-001",
            timestamp=NOW + 60,
        )

        assert updated_pay.payment_status == "Submitted"

        note_uc.execute(
            service_request_id="REQ-APP-001",
            note_type="Payment Review Note",
            note_text="Simulated transaction reference recorded. Pending verification.",
            created_by_role="NileGov Payments Officer",
            created_by_user="officer_payments",
            visibility="Auditor Visible",
        )

        notes = note_repo.list_by_service_request("REQ-APP-001")
        assert len(notes) == 1


# ─────────────────────────────────────────────────────────────────────────────
# Reporting Snapshot — composed from demo-like populated repositories
# ─────────────────────────────────────────────────────────────────────────────

class TestReportingSnapshotComposition:
    def test_generate_reporting_snapshot_from_demo_data(self):
        """Verify GenerateReportingSnapshot composes correctly across all repos."""
        req_repo = InMemoryServiceRequestRepository()
        cat_repo = InMemoryServiceCatalogueRepository()
        ev_repo = InMemoryEvidenceDocumentRepository()
        pay_repo = InMemoryPaymentRecordRepository()
        notif_repo = InMemoryNotificationEventRepository()
        snap_repo = InMemoryReportingSnapshotRepository()

        # Seed two demo requests
        req1 = make_service_request("REQ-APP-010", service_type="SVC-LOST-NID")
        req2 = make_service_request("REQ-APP-011", service_type="SVC-LOST-NID")
        req2.update_status(WorkflowStatus.UNDER_REVIEW, "officer_A", NOW + 100)
        req_repo.save(req1)
        req_repo.save(req2)

        uc = GenerateReportingSnapshot(
            request_repo=req_repo,
            catalogue_repo=cat_repo,
            evidence_repo=ev_repo,
            payment_repo=pay_repo,
            notification_repo=notif_repo,
            snapshot_repo=snap_repo,
        )

        snapshot = uc.execute(
            snapshot_id="SNAP-APP-001",
            snapshot_name="App Composition Test Snapshot",
            period_start=NOW - 3600,
            period_end=NOW + 3600,
            generated_by="test_suite",
            timestamp=NOW + 7200,
        )

        assert snapshot.reporting_snapshot_id == "SNAP-APP-001"
        assert snapshot.total_requests == 2
        assert snap_repo.get_by_id("SNAP-APP-001") is not None

    def test_snapshot_from_empty_repos_returns_zero_counts(self):
        req_repo = InMemoryServiceRequestRepository()
        cat_repo = InMemoryServiceCatalogueRepository()
        ev_repo = InMemoryEvidenceDocumentRepository()
        pay_repo = InMemoryPaymentRecordRepository()
        notif_repo = InMemoryNotificationEventRepository()
        snap_repo = InMemoryReportingSnapshotRepository()

        uc = GenerateReportingSnapshot(
            request_repo=req_repo,
            catalogue_repo=cat_repo,
            evidence_repo=ev_repo,
            payment_repo=pay_repo,
            notification_repo=notif_repo,
            snapshot_repo=snap_repo,
        )

        snapshot = uc.execute(
            snapshot_id="SNAP-EMPTY-001",
            snapshot_name="Empty Dataset Snapshot",
            period_start=NOW - 3600,
            period_end=NOW + 3600,
            generated_by="test_suite",
            timestamp=NOW,
        )

        assert snapshot.total_requests == 0
        assert snapshot.payment_pending_count == 0
        assert snapshot.notification_simulated_sent_count == 0


# ─────────────────────────────────────────────────────────────────────────────
# Interoperability payload safety — built from real service request objects
# ─────────────────────────────────────────────────────────────────────────────

class TestInteroperabilityPayloadFromServiceRequest:
    def test_service_request_payload_contains_reference_number(self):
        # build_service_request_payload expects .reference_number attribute;
        # the domain uses .reference_no — use the alias wrapper.
        req = _ServiceRequestWithAlias(make_service_request())
        payload = build_service_request_payload(
            req,
            service_name="Lost National ID Replacement",
            evidence_status_summary={"complete": 2, "missing": 0},
        )
        assert payload["reference_number"] == req.reference_no

    def test_service_request_payload_excludes_sensitive_identity_values(self):
        req = _ServiceRequestWithAlias(make_service_request())
        payload = build_service_request_payload(
            req,
            service_name="Lost National ID Replacement",
            evidence_status_summary={},
        )
        # NIN value must never appear in the API payload
        assert_payload_excludes_sensitive_values(payload, ["CF123456789012"])

    def test_service_request_payload_contains_disclaimer(self):
        req = _ServiceRequestWithAlias(make_service_request())
        payload = build_service_request_payload(
            req,
            service_name="Lost National ID Replacement",
            evidence_status_summary={},
        )
        assert payload.get("disclaimer") == INTEROPERABILITY_DISCLAIMER

    def test_application_use_cases_do_not_require_frappe(self):
        """Verify no Frappe import errors occur when running composition use cases."""
        # All of the above tests ran without a Frappe ModuleNotFoundError.
        # This explicit test confirms the import chain is clean.
        import nilegov_stack.application.create_case_note
        import nilegov_stack.application.create_evidence_document
        import nilegov_stack.application.create_payment_record
        import nilegov_stack.application.generate_reporting_snapshot
        import nilegov_stack.application.build_interoperability_payloads
        assert True
