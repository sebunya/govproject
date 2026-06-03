# Use Case: List Case Notes
# Digi-Verse Uganda Limited
# Prototype simulation only. Not official government records.

from typing import List, Optional

from nilegov_stack.domain.case_note import CaseNote
from nilegov_stack.infrastructure.repositories.case_note_repository import CaseNoteRepository


class ListCaseNotes:
    """Application use case: queries CaseNotes from the repository.

    Supports listing by service request, note type, visibility, or all notes.
    Provides a citizen-safe summary filter.
    """

    def __init__(self, repository: CaseNoteRepository):
        self.repository = repository

    def by_service_request(self, service_request_id: str) -> List[CaseNote]:
        """Returns all notes attached to a specific service request."""
        return self.repository.list_by_service_request(service_request_id)

    def by_note_type(self, note_type: str) -> List[CaseNote]:
        """Returns all notes of a specific type."""
        return self.repository.list_by_note_type(note_type)

    def by_visibility(self, visibility: str) -> List[CaseNote]:
        """Returns all notes with a specific visibility level."""
        return self.repository.list_by_visibility(visibility)

    def all_notes(self) -> List[CaseNote]:
        """Returns all stored notes."""
        return self.repository.list_all()

    def citizen_safe_summaries(self, service_request_id: str) -> List[str]:
        """Returns citizen-safe note summaries for a given service request.

        Only returns notes with 'Citizen Visible Summary' visibility.
        Each summary is stripped of internal officer/audit details.
        Returns an empty list if no citizen-visible notes exist.
        """
        notes = self.repository.list_by_service_request(service_request_id)
        summaries = []
        for note in notes:
            summary = note.safe_citizen_summary()
            if summary is not None:
                summaries.append(summary)
        return summaries
