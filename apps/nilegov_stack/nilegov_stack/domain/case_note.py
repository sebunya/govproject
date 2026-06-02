# Case Note Domain Model
# Digi-Verse Uganda Limited
# Prototype case note only. Not an official government record until runtime deployment and approval.

from typing import Optional
import time


CASE_NOTE_DISCLAIMER = (
    "Prototype case note only. "
    "Not an official government record until runtime deployment and approval."
)

ALLOWED_NOTE_TYPES = {
    "Officer Note",
    "Records Review Note",
    "Payment Review Note",
    "Supervisor Note",
    "Citizen Contact Note",
    "Escalation Note",
    "Closure Note",
}

ALLOWED_VISIBILITY = {
    "Internal Only",
    "Supervisor Visible",
    "Auditor Visible",
    "Citizen Visible Summary",
}

# Visibility levels that must never expose internal audit / security details to citizens.
CITIZEN_SAFE_VISIBILITY = {"Citizen Visible Summary"}

# Note types that must never be citizen-visible (internal-operational notes).
INTERNALLY_RESTRICTED_NOTE_TYPES = {
    "Records Review Note",
    "Payment Review Note",
    "Escalation Note",
}


class CaseNote:
    """
    Aggregate representing a structured internal case note attached to a Service Request.

    Rules:
    - note_text is required.
    - service_request_id is required.
    - created_by_role is required.
    - note_type must be from ALLOWED_NOTE_TYPES.
    - visibility must be from ALLOWED_VISIBILITY.
    - citizen-visible notes must not be of a restricted note type.
    """

    def __init__(
        self,
        case_note_id: str,
        service_request_id: str,
        note_type: str,
        note_text: str,
        created_by_role: str,
        created_by_user: str,
        visibility: str = "Internal Only",
        created_at: Optional[float] = None,
        disclaimer: str = CASE_NOTE_DISCLAIMER,
    ):
        # Required field validation
        if not service_request_id or not service_request_id.strip():
            raise ValueError("service_request_id is required for a CaseNote.")
        if not note_text or not note_text.strip():
            raise ValueError("note_text is required for a CaseNote.")
        if not created_by_role or not created_by_role.strip():
            raise ValueError("created_by_role is required for a CaseNote.")
        if not created_by_user or not created_by_user.strip():
            raise ValueError("created_by_user is required for a CaseNote.")

        # Enum-like validation
        if note_type not in ALLOWED_NOTE_TYPES:
            raise ValueError(
                f"Invalid note_type '{note_type}'. "
                f"Allowed values: {sorted(ALLOWED_NOTE_TYPES)}"
            )
        if visibility not in ALLOWED_VISIBILITY:
            raise ValueError(
                f"Invalid visibility '{visibility}'. "
                f"Allowed values: {sorted(ALLOWED_VISIBILITY)}"
            )

        # Citizen-visible safety rule
        if visibility in CITIZEN_SAFE_VISIBILITY and note_type in INTERNALLY_RESTRICTED_NOTE_TYPES:
            raise ValueError(
                f"Note type '{note_type}' must not be set to citizen-visible visibility. "
                "Internal review notes must remain 'Internal Only', 'Supervisor Visible', "
                "or 'Auditor Visible'."
            )

        self.case_note_id = case_note_id
        self.service_request_id = service_request_id
        self.note_type = note_type
        self.note_text = note_text.strip()
        self.created_by_role = created_by_role
        self.created_by_user = created_by_user
        self.visibility = visibility
        self.created_at = created_at if created_at is not None else time.time()
        self.disclaimer = disclaimer

    def is_citizen_visible(self) -> bool:
        """Returns True only if this note can be surfaced in citizen-facing views."""
        return self.visibility in CITIZEN_SAFE_VISIBILITY

    def safe_citizen_summary(self) -> Optional[str]:
        """
        Returns a stripped summary suitable for citizen-facing display,
        or None if this note is not citizen-visible.

        Does not expose internal review details, officer identities,
        or security/audit specifics.
        """
        if not self.is_citizen_visible():
            return None
        return (
            f"[{self.note_type}] A case update has been recorded. "
            f"Please contact the service desk for further details. "
            f"({self.disclaimer})"
        )

    def to_dict(self) -> dict:
        return {
            "case_note_id": self.case_note_id,
            "service_request_id": self.service_request_id,
            "note_type": self.note_type,
            "note_text": self.note_text,
            "created_by_role": self.created_by_role,
            "created_by_user": self.created_by_user,
            "visibility": self.visibility,
            "created_at": self.created_at,
            "disclaimer": self.disclaimer,
        }
