# NileGov Management Review Note Controller
# Digi-Verse Uganda Limited
# Prototype management review note only. Observations and actions are based on simulated prototype data.

try:
    from frappe.model.document import Document
except ImportError:
    # Allow import outside a running Frappe bench (e.g. unit tests, compileall)
    Document = object


REQUIRED_DISCLAIMER = (
    "Prototype management review note only. Observations and actions are based on simulated prototype data."
)

_FORBIDDEN_CLAIM_KEYWORDS = [
    "official government statistics",
    "live reporting",
    "production dashboard",
    "connected to ministry",
    "real-time government",
]


class NileGovManagementReviewNote(Document):
    """
    Frappe Document controller for NileGov Management Review Note.

    Validates that:
    - review_note_id is always provided.
    - disclaimer is always present and set to the required prototype text.
    - No overclaim of official or live government reporting is introduced.
    """

    def validate(self):
        self._validate_review_note_id()
        self._validate_and_set_disclaimer()
        self._assert_no_live_gov_claim()

    def before_save(self):
        self._validate_and_set_disclaimer()

    def _validate_review_note_id(self):
        if not getattr(self, "review_note_id", None):
            try:
                import frappe
                frappe.throw("Review Note ID is required for NileGov Management Review Note.")
            except ImportError:
                raise ValueError("Review Note ID is required for NileGov Management Review Note.")

    def _validate_and_set_disclaimer(self):
        current = getattr(self, "disclaimer", None)
        if not current or not current.strip():
            self.disclaimer = REQUIRED_DISCLAIMER
        elif REQUIRED_DISCLAIMER not in current:
            self.disclaimer = REQUIRED_DISCLAIMER

    def _assert_no_live_gov_claim(self):
        fields_to_check = {
            "review_note_id": getattr(self, "review_note_id", "") or "",
            "summary": getattr(self, "summary", "") or "",
        }
        for fieldname, value in fields_to_check.items():
            for kw in _FORBIDDEN_CLAIM_KEYWORDS:
                if kw.lower() in value.lower():
                    try:
                        import frappe
                        frappe.throw(
                            f"Field '{fieldname}' contains a disallowed claim: '{kw}'. "
                            "NileGov Management Review Notes must not claim live or official statistics."
                        )
                    except ImportError:
                        raise ValueError(
                            f"Field '{fieldname}' contains a disallowed claim: '{kw}'."
                        )
