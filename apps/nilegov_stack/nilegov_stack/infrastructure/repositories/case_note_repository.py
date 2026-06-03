# In-memory Case Note Repository
# Digi-Verse Uganda Limited

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from nilegov_stack.domain.case_note import CaseNote


class CaseNoteRepository(ABC):
    """Port interface for persisting and loading CaseNote aggregates."""

    @abstractmethod
    def save(self, note: CaseNote) -> None:
        """Persists a CaseNote."""
        pass

    @abstractmethod
    def get(self, case_note_id: str) -> Optional[CaseNote]:
        """Loads a CaseNote by its unique ID."""
        pass

    @abstractmethod
    def list_all(self) -> List[CaseNote]:
        """Returns all stored CaseNotes."""
        pass

    @abstractmethod
    def list_by_service_request(self, service_request_id: str) -> List[CaseNote]:
        """Returns all CaseNotes for a given service request."""
        pass

    @abstractmethod
    def list_by_note_type(self, note_type: str) -> List[CaseNote]:
        """Returns all CaseNotes of a given note type."""
        pass

    @abstractmethod
    def list_by_visibility(self, visibility: str) -> List[CaseNote]:
        """Returns all CaseNotes with a given visibility level."""
        pass


class InMemoryCaseNoteRepository(CaseNoteRepository):
    """In-memory implementation of CaseNoteRepository for testing purposes.

    Prototype simulation only. No live database connection.
    """

    def __init__(self):
        self._notes: Dict[str, CaseNote] = {}

    def save(self, note: CaseNote) -> None:
        self._notes[note.case_note_id] = note

    def get(self, case_note_id: str) -> Optional[CaseNote]:
        return self._notes.get(case_note_id)

    def list_all(self) -> List[CaseNote]:
        return list(self._notes.values())

    def list_by_service_request(self, service_request_id: str) -> List[CaseNote]:
        return [
            n for n in self._notes.values()
            if n.service_request_id == service_request_id
        ]

    def list_by_note_type(self, note_type: str) -> List[CaseNote]:
        return [n for n in self._notes.values() if n.note_type == note_type]

    def list_by_visibility(self, visibility: str) -> List[CaseNote]:
        return [n for n in self._notes.values() if n.visibility == visibility]
