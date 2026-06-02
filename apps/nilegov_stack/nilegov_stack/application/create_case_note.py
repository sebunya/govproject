# Use Case: Create Case Note
# Digi-Verse Uganda Limited
# Prototype simulation only. Not an official government record.

import time
import uuid
from typing import Optional

from nilegov_stack.domain.case_note import (
    CaseNote,
    CASE_NOTE_DISCLAIMER,
    ALLOWED_NOTE_TYPES,
    ALLOWED_VISIBILITY,
)
from nilegov_stack.infrastructure.repositories.case_note_repository import CaseNoteRepository


class CreateCaseNote:
    """Application use case: creates and persists a structured CaseNote.

    No Frappe runtime required. Uses the CaseNoteRepository port.
    """

    def __init__(self, repository: CaseNoteRepository):
        self.repository = repository

    def execute(
        self,
        service_request_id: str,
        note_type: str,
        note_text: str,
        created_by_role: str,
        created_by_user: str,
        visibility: str = "Internal Only",
        case_note_id: Optional[str] = None,
        created_at: Optional[float] = None,
    ) -> CaseNote:
        """Creates a validated CaseNote and saves it to the repository.

        Args:
            service_request_id: The linked service request.
            note_type: One of the allowed note types.
            note_text: The substantive note content. Required.
            created_by_role: The role of the note author.
            created_by_user: The user identifier of the note author.
            visibility: One of the allowed visibility levels.
            case_note_id: Optional explicit ID; auto-generated if not provided.
            created_at: Optional timestamp; defaults to now.

        Returns:
            The saved CaseNote aggregate.

        Raises:
            ValueError: If any field is invalid per domain rules.
        """
        note_id = case_note_id or f"CN-{uuid.uuid4().hex[:12].upper()}"
        timestamp = created_at if created_at is not None else time.time()

        note = CaseNote(
            case_note_id=note_id,
            service_request_id=service_request_id,
            note_type=note_type,
            note_text=note_text,
            created_by_role=created_by_role,
            created_by_user=created_by_user,
            visibility=visibility,
            created_at=timestamp,
            disclaimer=CASE_NOTE_DISCLAIMER,
        )

        self.repository.save(note)
        return note
