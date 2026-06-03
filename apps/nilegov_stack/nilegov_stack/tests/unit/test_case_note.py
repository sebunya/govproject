# Unit Tests: Case Note Domain, Repository, and Application Use Cases
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.

import time

import pytest

from nilegov_stack.domain.case_note import (
    ALLOWED_NOTE_TYPES,
    ALLOWED_VISIBILITY,
    CASE_NOTE_DISCLAIMER,
    CITIZEN_SAFE_VISIBILITY,
    INTERNALLY_RESTRICTED_NOTE_TYPES,
    CaseNote,
)
from nilegov_stack.infrastructure.repositories.case_note_repository import (
    InMemoryCaseNoteRepository,
)
from nilegov_stack.application.create_case_note import CreateCaseNote
from nilegov_stack.application.list_case_notes import ListCaseNotes


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_note(
    case_note_id="CN-001",
    service_request_id="NGS-NIRA-2026-0001",
    note_type="Officer Note",
    note_text="Case progressing normally.",
    created_by_role="NileGov Citizen Officer",
    created_by_user="officer_demo",
    visibility="Internal Only",
    created_at=None,
) -> CaseNote:
    return CaseNote(
        case_note_id=case_note_id,
        service_request_id=service_request_id,
        note_type=note_type,
        note_text=note_text,
        created_by_role=created_by_role,
        created_by_user=created_by_user,
        visibility=visibility,
        created_at=created_at or time.time(),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Domain model – creation and defaults
# ─────────────────────────────────────────────────────────────────────────────

class TestCaseNoteCreation:
    def test_creates_with_required_fields(self):
        note = make_note()
        assert note.case_note_id == "CN-001"
        assert note.service_request_id == "NGS-NIRA-2026-0001"
        assert note.note_type == "Officer Note"
        assert note.note_text == "Case progressing normally."
        assert note.created_by_role == "NileGov Citizen Officer"
        assert note.created_by_user == "officer_demo"
        assert note.visibility == "Internal Only"

    def test_disclaimer_is_always_set(self):
        note = make_note()
        assert note.disclaimer == CASE_NOTE_DISCLAIMER
        assert "Prototype" in note.disclaimer
        assert "official government record" not in note.disclaimer.lower() or "not an official" in note.disclaimer.lower()

    def test_disclaimer_present_in_dict_output(self):
        note = make_note()
        d = note.to_dict()
        assert "disclaimer" in d
        assert d["disclaimer"] == CASE_NOTE_DISCLAIMER

    def test_created_at_defaults_to_now_if_not_provided(self):
        before = time.time()
        note = CaseNote(
            case_note_id="CN-T",
            service_request_id="REQ-001",
            note_type="Officer Note",
            note_text="Auto-timestamp test.",
            created_by_role="NileGov Citizen Officer",
            created_by_user="officer_demo",
        )
        after = time.time()
        assert before <= note.created_at <= after

    def test_explicit_created_at_is_preserved(self):
        ts = 1_700_000_000.0
        note = make_note(created_at=ts)
        assert note.created_at == ts

    def test_note_text_is_stripped(self):
        note = make_note(note_text="  Trailing spaces.  ")
        assert note.note_text == "Trailing spaces."


# ─────────────────────────────────────────────────────────────────────────────
# Domain model – validation rules
# ─────────────────────────────────────────────────────────────────────────────

class TestCaseNoteValidation:
    def test_empty_service_request_id_raises(self):
        with pytest.raises(ValueError, match="service_request_id"):
            make_note(service_request_id="")

    def test_whitespace_service_request_id_raises(self):
        with pytest.raises(ValueError, match="service_request_id"):
            make_note(service_request_id="   ")

    def test_empty_note_text_raises(self):
        with pytest.raises(ValueError, match="note_text"):
            make_note(note_text="")

    def test_whitespace_note_text_raises(self):
        with pytest.raises(ValueError, match="note_text"):
            make_note(note_text="   ")

    def test_empty_created_by_role_raises(self):
        with pytest.raises(ValueError, match="created_by_role"):
            make_note(created_by_role="")

    def test_empty_created_by_user_raises(self):
        with pytest.raises(ValueError, match="created_by_user"):
            make_note(created_by_user="")

    def test_invalid_note_type_raises(self):
        with pytest.raises(ValueError, match="note_type"):
            make_note(note_type="Unofficial Comment")

    def test_invalid_visibility_raises(self):
        with pytest.raises(ValueError, match="visibility"):
            make_note(visibility="Public")

    def test_all_allowed_note_types_accepted(self):
        for nt in ALLOWED_NOTE_TYPES:
            note = make_note(note_type=nt)
            assert note.note_type == nt

    def test_all_allowed_visibility_values_accepted(self):
        for vis in ALLOWED_VISIBILITY:
            # Skip citizen-visible + restricted type combos
            note_type = "Officer Note"
            note = make_note(note_type=note_type, visibility=vis)
            assert note.visibility == vis


# ─────────────────────────────────────────────────────────────────────────────
# Domain model – citizen-visible safety rules
# ─────────────────────────────────────────────────────────────────────────────

class TestCaseNoteCitizenSafety:
    def test_restricted_note_type_cannot_be_citizen_visible(self):
        """Records Review, Payment Review, and Escalation notes must never be citizen-visible."""
        for restricted_type in INTERNALLY_RESTRICTED_NOTE_TYPES:
            with pytest.raises(ValueError):
                CaseNote(
                    case_note_id="CN-X",
                    service_request_id="REQ-001",
                    note_type=restricted_type,
                    note_text="Internal review detail.",
                    created_by_role="NileGov Records Officer",
                    created_by_user="officer_demo",
                    visibility="Citizen Visible Summary",
                )

    def test_officer_note_can_be_citizen_visible(self):
        note = make_note(note_type="Officer Note", visibility="Citizen Visible Summary")
        assert note.is_citizen_visible() is True

    def test_internal_only_note_is_not_citizen_visible(self):
        note = make_note(visibility="Internal Only")
        assert note.is_citizen_visible() is False

    def test_supervisor_visible_note_is_not_citizen_visible(self):
        note = make_note(visibility="Supervisor Visible")
        assert note.is_citizen_visible() is False

    def test_auditor_visible_note_is_not_citizen_visible(self):
        note = make_note(visibility="Auditor Visible")
        assert note.is_citizen_visible() is False

    def test_safe_citizen_summary_returns_none_for_internal_notes(self):
        note = make_note(visibility="Internal Only")
        assert note.safe_citizen_summary() is None

    def test_safe_citizen_summary_does_not_expose_officer_identity(self):
        note = make_note(
            visibility="Citizen Visible Summary",
            note_text="Officer reviewed case documents. Identity confirmed by John Doe, ID #12345.",
            created_by_user="officer_john_doe",
        )
        summary = note.safe_citizen_summary()
        assert summary is not None
        assert "officer_john_doe" not in summary
        assert "John Doe" not in summary
        assert "12345" not in summary

    def test_safe_citizen_summary_contains_disclaimer(self):
        note = make_note(note_type="Officer Note", visibility="Citizen Visible Summary")
        summary = note.safe_citizen_summary()
        assert "Prototype" in summary


# ─────────────────────────────────────────────────────────────────────────────
# Repository – InMemoryCaseNoteRepository
# ─────────────────────────────────────────────────────────────────────────────

class TestInMemoryCaseNoteRepository:
    def test_save_and_retrieve(self):
        repo = InMemoryCaseNoteRepository()
        note = make_note()
        repo.save(note)
        retrieved = repo.get("CN-001")
        assert retrieved is not None
        assert retrieved.case_note_id == "CN-001"

    def test_get_nonexistent_returns_none(self):
        repo = InMemoryCaseNoteRepository()
        assert repo.get("NONEXISTENT") is None

    def test_list_all_returns_all_notes(self):
        repo = InMemoryCaseNoteRepository()
        repo.save(make_note(case_note_id="CN-001"))
        repo.save(make_note(case_note_id="CN-002"))
        all_notes = repo.list_all()
        assert len(all_notes) == 2

    def test_list_by_service_request(self):
        repo = InMemoryCaseNoteRepository()
        repo.save(make_note(case_note_id="CN-001", service_request_id="REQ-A"))
        repo.save(make_note(case_note_id="CN-002", service_request_id="REQ-B"))
        repo.save(make_note(case_note_id="CN-003", service_request_id="REQ-A"))
        results = repo.list_by_service_request("REQ-A")
        assert len(results) == 2
        assert all(n.service_request_id == "REQ-A" for n in results)

    def test_list_by_note_type(self):
        repo = InMemoryCaseNoteRepository()
        repo.save(make_note(case_note_id="CN-001", note_type="Officer Note"))
        repo.save(make_note(case_note_id="CN-002", note_type="Supervisor Note"))
        repo.save(make_note(case_note_id="CN-003", note_type="Officer Note"))
        results = repo.list_by_note_type("Officer Note")
        assert len(results) == 2

    def test_list_by_visibility(self):
        repo = InMemoryCaseNoteRepository()
        repo.save(make_note(case_note_id="CN-001", visibility="Internal Only"))
        repo.save(make_note(case_note_id="CN-002", visibility="Supervisor Visible"))
        results = repo.list_by_visibility("Supervisor Visible")
        assert len(results) == 1

    def test_save_overwrites_existing_id(self):
        repo = InMemoryCaseNoteRepository()
        note1 = make_note(case_note_id="CN-001", note_text="First version.")
        note2 = CaseNote(
            case_note_id="CN-001",
            service_request_id="NGS-NIRA-2026-0001",
            note_type="Supervisor Note",
            note_text="Updated version.",
            created_by_role="NileGov SLA Supervisor",
            created_by_user="supervisor_demo",
        )
        repo.save(note1)
        repo.save(note2)
        retrieved = repo.get("CN-001")
        assert retrieved.note_text == "Updated version."


# ─────────────────────────────────────────────────────────────────────────────
# Application use cases – CreateCaseNote
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateCaseNote:
    def test_creates_and_saves_note(self):
        repo = InMemoryCaseNoteRepository()
        uc = CreateCaseNote(repo)
        note = uc.execute(
            service_request_id="NGS-NIRA-2026-0001",
            note_type="Officer Note",
            note_text="Documents reviewed. Proceeding to payment step.",
            created_by_role="NileGov Citizen Officer",
            created_by_user="officer_demo",
        )
        assert note is not None
        assert note.service_request_id == "NGS-NIRA-2026-0001"
        assert repo.get(note.case_note_id) is not None

    def test_auto_generates_case_note_id(self):
        repo = InMemoryCaseNoteRepository()
        uc = CreateCaseNote(repo)
        note = uc.execute(
            service_request_id="REQ-001",
            note_type="Officer Note",
            note_text="Auto-ID test.",
            created_by_role="NileGov Citizen Officer",
            created_by_user="officer_demo",
        )
        assert note.case_note_id.startswith("CN-")
        assert len(note.case_note_id) > 3

    def test_uses_explicit_id_when_provided(self):
        repo = InMemoryCaseNoteRepository()
        uc = CreateCaseNote(repo)
        note = uc.execute(
            service_request_id="REQ-001",
            note_type="Supervisor Note",
            note_text="Supervisor directive issued.",
            created_by_role="NileGov SLA Supervisor",
            created_by_user="supervisor_demo",
            case_note_id="MANUAL-ID-001",
        )
        assert note.case_note_id == "MANUAL-ID-001"

    def test_invalid_note_type_raises(self):
        repo = InMemoryCaseNoteRepository()
        uc = CreateCaseNote(repo)
        with pytest.raises(ValueError):
            uc.execute(
                service_request_id="REQ-001",
                note_type="Made Up Note",
                note_text="Should fail.",
                created_by_role="NileGov Citizen Officer",
                created_by_user="officer_demo",
            )

    def test_disclaimer_set_on_created_note(self):
        repo = InMemoryCaseNoteRepository()
        uc = CreateCaseNote(repo)
        note = uc.execute(
            service_request_id="REQ-001",
            note_type="Closure Note",
            note_text="Case closed successfully.",
            created_by_role="NileGov Citizen Officer",
            created_by_user="officer_demo",
        )
        assert note.disclaimer == CASE_NOTE_DISCLAIMER


# ─────────────────────────────────────────────────────────────────────────────
# Application use cases – ListCaseNotes
# ─────────────────────────────────────────────────────────────────────────────

class TestListCaseNotes:
    def _populated_repo(self) -> InMemoryCaseNoteRepository:
        repo = InMemoryCaseNoteRepository()
        repo.save(make_note("CN-001", service_request_id="REQ-A", note_type="Officer Note", visibility="Internal Only"))
        repo.save(make_note("CN-002", service_request_id="REQ-A", note_type="Supervisor Note", visibility="Supervisor Visible"))
        repo.save(make_note("CN-003", service_request_id="REQ-B", note_type="Officer Note", visibility="Citizen Visible Summary"))
        repo.save(make_note("CN-004", service_request_id="REQ-A", note_type="Closure Note", visibility="Citizen Visible Summary"))
        return repo

    def test_by_service_request_filters_correctly(self):
        lister = ListCaseNotes(self._populated_repo())
        results = lister.by_service_request("REQ-A")
        assert len(results) == 3
        assert all(n.service_request_id == "REQ-A" for n in results)

    def test_by_note_type_filters_correctly(self):
        lister = ListCaseNotes(self._populated_repo())
        results = lister.by_note_type("Officer Note")
        assert len(results) == 2

    def test_by_visibility_filters_correctly(self):
        lister = ListCaseNotes(self._populated_repo())
        results = lister.by_visibility("Citizen Visible Summary")
        assert len(results) == 2

    def test_all_notes_returns_full_list(self):
        lister = ListCaseNotes(self._populated_repo())
        assert len(lister.all_notes()) == 4

    def test_citizen_safe_summaries_only_returns_visible_notes(self):
        lister = ListCaseNotes(self._populated_repo())
        # REQ-A has CN-001 (Internal Only), CN-002 (Supervisor Visible), CN-004 (Citizen Visible Summary)
        summaries = lister.citizen_safe_summaries("REQ-A")
        assert len(summaries) == 1
        assert all(isinstance(s, str) for s in summaries)

    def test_citizen_safe_summaries_empty_when_no_visible_notes(self):
        repo = InMemoryCaseNoteRepository()
        repo.save(make_note("CN-001", service_request_id="REQ-PRIVATE", visibility="Internal Only"))
        lister = ListCaseNotes(repo)
        assert lister.citizen_safe_summaries("REQ-PRIVATE") == []

    def test_by_service_request_empty_for_nonexistent(self):
        lister = ListCaseNotes(self._populated_repo())
        assert lister.by_service_request("NONEXISTENT-REQ") == []

    def test_no_frappe_import_in_use_case(self):
        """Verify the use case modules do not import frappe at module level."""
        import nilegov_stack.application.create_case_note as cc
        import nilegov_stack.application.list_case_notes as lc
        assert "frappe" not in dir(cc)
        assert "frappe" not in dir(lc)
