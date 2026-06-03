# Application Tests: Service Request + Case Note Composition
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.

import time

import pytest

from nilegov_stack.application.create_case_note import CreateCaseNote
from nilegov_stack.application.list_case_notes import ListCaseNotes
from nilegov_stack.domain.case_note import CASE_NOTE_DISCLAIMER
from nilegov_stack.infrastructure.repositories.case_note_repository import (
    InMemoryCaseNoteRepository,
)
from nilegov_stack.infrastructure.repositories.service_request_repository import (
    InMemoryServiceRequestRepository,
)
from nilegov_stack.domain.service_request import ServiceRequest, WorkflowStatus
from nilegov_stack.domain.value_objects import NIN


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

NOW = 1_717_000_000.0


def make_service_request(request_id="REQ-COMPOSE-001") -> ServiceRequest:
    return ServiceRequest(
        request_id=request_id,
        reference_no=f"NGS-NIRA-2026-{request_id[-3:]}",
        citizen_nin=NIN("CF123456789012"),
        citizen_name="Compose Test Citizen",
        phone_number="+256780000099",
        location="Ntinda, Kampala",
        description="Test service request for application composition.",
        citizen_profile_id="CP-COMPOSE-001",
        created_at=NOW,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Create a service request, then add a case note — tests composition of
# ServiceRequestRepository + CaseNoteRepository in a single flow.
# ─────────────────────────────────────────────────────────────────────────────

class TestServiceRequestAndCaseNoteComposition:
    def test_create_request_and_add_officer_note(self):
        req_repo = InMemoryServiceRequestRepository()
        note_repo = InMemoryCaseNoteRepository()
        create_note = CreateCaseNote(note_repo)

        # Create a service request
        req = make_service_request()
        req_repo.save(req)

        # Add an officer note to it
        note = create_note.execute(
            service_request_id=req.request_id,
            note_type="Officer Note",
            note_text="Citizen documents reviewed. Proceeding to payment.",
            created_by_role="NileGov Citizen Officer",
            created_by_user="officer_demo",
        )

        # Verify the note is linked to the right request
        assert note.service_request_id == req.request_id
        assert note_repo.get(note.case_note_id) is not None

        # Verify the request is still intact
        retrieved_req = req_repo.get_by_id(req.request_id)
        assert retrieved_req is not None
        assert retrieved_req.status == WorkflowStatus.SUBMITTED

    def test_create_request_then_transition_and_add_closure_note(self):
        req_repo = InMemoryServiceRequestRepository()
        note_repo = InMemoryCaseNoteRepository()
        create_note = CreateCaseNote(note_repo)
        list_notes = ListCaseNotes(note_repo)

        req = make_service_request()
        req_repo.save(req)

        # Advance through full workflow
        req.update_status(WorkflowStatus.UNDER_REVIEW, "officer_demo", NOW + 10)
        req.update_status(WorkflowStatus.PAYMENT_PENDING, "officer_demo", NOW + 20)
        req.update_status(WorkflowStatus.PAYMENT_VERIFIED, "officer_demo", NOW + 30)
        req.update_status(WorkflowStatus.APPROVED, "officer_demo", NOW + 40)
        req.update_status(WorkflowStatus.READY_FOR_COLLECTION, "officer_demo", NOW + 50)
        req.update_status(WorkflowStatus.CLOSED, "officer_demo", NOW + 60)
        req_repo.save(req)

        # Add closure note
        create_note.execute(
            service_request_id=req.request_id,
            note_type="Closure Note",
            note_text="Case successfully resolved. National ID ready for collection.",
            created_by_role="NileGov Citizen Officer",
            created_by_user="officer_demo",
        )

        notes = list_notes.by_service_request(req.request_id)
        assert len(notes) == 1
        assert notes[0].note_type == "Closure Note"

    def test_multiple_officers_add_notes_to_same_request(self):
        req_repo = InMemoryServiceRequestRepository()
        note_repo = InMemoryCaseNoteRepository()
        create_note = CreateCaseNote(note_repo)

        req = make_service_request()
        req_repo.save(req)

        create_note.execute(
            service_request_id=req.request_id,
            note_type="Officer Note",
            note_text="Initial review completed.",
            created_by_role="NileGov Citizen Officer",
            created_by_user="officer_A",
        )
        create_note.execute(
            service_request_id=req.request_id,
            note_type="Records Review Note",
            note_text="Identity documents verified against records.",
            created_by_role="NileGov Records Officer",
            created_by_user="officer_B",
        )
        create_note.execute(
            service_request_id=req.request_id,
            note_type="Payment Review Note",
            note_text="Payment of UGX 50,000 verified.",
            created_by_role="NileGov Payments Officer",
            created_by_user="officer_C",
            visibility="Auditor Visible",
        )

        lister = ListCaseNotes(note_repo)
        all_notes = lister.by_service_request(req.request_id)
        assert len(all_notes) == 3

    def test_citizen_safe_summaries_filter_correctly(self):
        """Citizen-facing summaries should not expose internal review notes."""
        req_repo = InMemoryServiceRequestRepository()
        note_repo = InMemoryCaseNoteRepository()
        create_note = CreateCaseNote(note_repo)
        list_notes = ListCaseNotes(note_repo)

        req = make_service_request()
        req_repo.save(req)

        # Internal note — should NOT appear in citizen summaries
        create_note.execute(
            service_request_id=req.request_id,
            note_type="Officer Note",
            note_text="Officer note about security concern. INTERNAL ONLY.",
            created_by_role="NileGov Citizen Officer",
            created_by_user="officer_A",
            visibility="Internal Only",
        )
        # Citizen-visible note
        create_note.execute(
            service_request_id=req.request_id,
            note_type="Officer Note",
            note_text="Your application is under review.",
            created_by_role="NileGov Citizen Officer",
            created_by_user="officer_A",
            visibility="Citizen Visible Summary",
        )

        summaries = list_notes.citizen_safe_summaries(req.request_id)
        assert len(summaries) == 1
        assert "INTERNAL ONLY" not in summaries[0]
        assert "officer_A" not in summaries[0]

    def test_no_frappe_runtime_required(self):
        """Verify that none of the application-level imports require Frappe."""
        import sys
        # If frappe were imported at module level, it would appear as a module in sys.modules
        # after imports above. The test assertions are that we completed the entire flow above
        # without raising a ModuleNotFoundError for 'frappe'.
        import nilegov_stack.application.create_case_note
        import nilegov_stack.application.list_case_notes
        import nilegov_stack.infrastructure.repositories.case_note_repository
        # If we reach here, no Frappe import error was raised
        assert True
