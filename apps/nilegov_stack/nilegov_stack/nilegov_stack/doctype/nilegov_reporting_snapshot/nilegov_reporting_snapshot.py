# NileGov Reporting Snapshot Controller
# Digi-Verse Uganda Limited
# Prototype reporting snapshot only. Metrics are calculated from fictional demo data
# and are not official government statistics.

try:
    from frappe.model.document import Document
except ImportError:
    # Allow import outside a running Frappe bench (e.g. unit tests, compileall)
    Document = object


REQUIRED_DISCLAIMER = (
    "Prototype reporting snapshot only. Metrics are calculated from fictional demo data "
    "and are not official government statistics."
)

# Keywords that would indicate an overclaim of live/official status
_FORBIDDEN_CLAIM_KEYWORDS = [
    "official government statistics",
    "live reporting",
    "production dashboard",
    "connected to ministry",
    "real-time government",
]


class NileGovReportingSnapshot(Document):
    """
    Frappe Document controller for NileGov Reporting Snapshot.

    Validates that:
    - snapshot_name is always provided.
    - disclaimer is always present and set to the required prototype text.
    - No overclaim of official or live government reporting is introduced.

    Prototype simulation only. No live Government registry access.
    """

    def validate(self):
        self._validate_snapshot_name()
        self._validate_and_set_disclaimer()
        self._assert_no_live_gov_claim()

    def before_save(self):
        self._validate_and_set_disclaimer()

    # ──────────────────────────────────────────────────────────────────────────
    # Internal validation helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _validate_snapshot_name(self):
        if not getattr(self, "snapshot_name", None):
            try:
                import frappe
                frappe.throw("Snapshot Name is required for NileGov Reporting Snapshot.")
            except ImportError:
                raise ValueError("Snapshot Name is required for NileGov Reporting Snapshot.")

    def _validate_and_set_disclaimer(self):
        """
        Ensures the disclaimer field is always set to the required prototype text.
        If it is missing or blank, it is defaulted automatically.
        If it has been replaced with a non-prototype claim, it is reset.
        """
        current = getattr(self, "disclaimer", None)
        if not current or not current.strip():
            self.disclaimer = REQUIRED_DISCLAIMER
        elif REQUIRED_DISCLAIMER not in current:
            # Disclaimer text was altered — reset to canonical form
            self.disclaimer = REQUIRED_DISCLAIMER

    def _assert_no_live_gov_claim(self):
        """
        Guards against any text fields containing forbidden live-gov claim keywords.
        Applies to snapshot_name and source_dataset only (user-editable text fields).
        """
        fields_to_check = {
            "snapshot_name": getattr(self, "snapshot_name", "") or "",
            "source_dataset": getattr(self, "source_dataset", "") or "",
        }
        for fieldname, value in fields_to_check.items():
            for kw in _FORBIDDEN_CLAIM_KEYWORDS:
                if kw.lower() in value.lower():
                    try:
                        import frappe
                        frappe.throw(
                            f"Field '{fieldname}' contains a disallowed claim: '{kw}'. "
                            "NileGov Reporting Snapshots must not claim live or official statistics."
                        )
                    except ImportError:
                        raise ValueError(
                            f"Field '{fieldname}' contains a disallowed claim: '{kw}'."
                        )
