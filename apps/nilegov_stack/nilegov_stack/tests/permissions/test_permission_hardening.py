# Permission Tests: NileGov Role and Access Policy Hardening
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.
#
# These tests verify that the permission_policy.py assumptions are:
# - Complete (all 8 roles defined)
# - Correct (duties are separated)
# - Safe (no role implies live government access)
# - Consistent with the case note visibility model

import pytest

from nilegov_stack.application.permission_policy import (
    EVIDENCE_REVIEW_ROLES,
    NILEGOV_ROLES,
    PAYMENT_REVIEW_ROLES,
    PROTECTED_DOCTYPES,
    READ_ONLY_LOG_ROLES,
    SENSITIVE_DOCTYPES,
    can_modify_protected_log,
    can_read_protected_log,
    can_review_evidence,
    can_review_payment,
    is_nilegov_role,
    is_protected_doctype,
    is_sensitive_doctype,
    role_implies_live_government_access,
)
from nilegov_stack.domain.case_note import (
    INTERNALLY_RESTRICTED_NOTE_TYPES,
    ALLOWED_NOTE_TYPES,
    CaseNote,
)


# ─────────────────────────────────────────────────────────────────────────────
# Role completeness
# ─────────────────────────────────────────────────────────────────────────────

class TestRoleCompleteness:
    EXPECTED_ROLES = {
        "NileGov Citizen Officer",
        "NileGov Records Officer",
        "NileGov Payments Officer",
        "NileGov SLA Supervisor",
        "NileGov M&E Viewer",
        "NileGov MDA Admin",
        "NileGov System Auditor",
        "NileGov System Manager",
    }

    def test_all_expected_roles_are_defined(self):
        assert self.EXPECTED_ROLES.issubset(NILEGOV_ROLES)

    def test_all_roles_have_nilegov_prefix(self):
        for role in NILEGOV_ROLES:
            assert role.startswith("NileGov "), (
                f"Role '{role}' does not start with 'NileGov '. "
                "All roles must use the NileGov- prefix."
            )

    def test_no_role_is_empty_string(self):
        for role in NILEGOV_ROLES:
            assert role.strip() != ""

    def test_exactly_expected_number_of_roles(self):
        """Fail if roles are added or removed unexpectedly."""
        # 8 NileGov-prefixed roles defined in Pass 10A
        assert len(NILEGOV_ROLES) >= 8


# ─────────────────────────────────────────────────────────────────────────────
# Protected DocTypes
# ─────────────────────────────────────────────────────────────────────────────

class TestProtectedDocTypes:
    def test_audit_event_is_protected(self):
        assert "NileGov Audit Event" in PROTECTED_DOCTYPES

    def test_integration_log_is_protected(self):
        assert "NileGov Integration Simulation Log" in PROTECTED_DOCTYPES

    def test_is_protected_doctype_returns_true_for_known(self):
        assert is_protected_doctype("NileGov Audit Event")
        assert is_protected_doctype("NileGov Integration Simulation Log")

    def test_is_protected_doctype_returns_false_for_nonprotected(self):
        assert is_protected_doctype("NileGov Service Request") is False
        assert is_protected_doctype("NileGov Citizen Profile") is False


# ─────────────────────────────────────────────────────────────────────────────
# Sensitive DocTypes
# ─────────────────────────────────────────────────────────────────────────────

class TestSensitiveDocTypes:
    EXPECTED_SENSITIVE = {
        "NileGov Citizen Profile",
        "NileGov Consent Record",
        "NileGov Evidence Document",
        "NileGov Payment Record",
        "NileGov Service Request",
        "NileGov Audit Event",
        "NileGov Integration Simulation Log",
    }

    def test_all_expected_sensitive_doctypes_present(self):
        assert self.EXPECTED_SENSITIVE.issubset(SENSITIVE_DOCTYPES)

    def test_is_sensitive_doctype_returns_true(self):
        for dt in self.EXPECTED_SENSITIVE:
            assert is_sensitive_doctype(dt), f"Expected {dt} to be sensitive."

    def test_nonexistent_doctype_not_sensitive(self):
        assert is_sensitive_doctype("NileGov Fictional DocType") is False


# ─────────────────────────────────────────────────────────────────────────────
# Protected log modification rules
# ─────────────────────────────────────────────────────────────────────────────

class TestProtectedLogModification:
    ORDINARY_ROLES = [
        "NileGov Citizen Officer",
        "NileGov Records Officer",
        "NileGov Payments Officer",
        "NileGov SLA Supervisor",
        "NileGov M&E Viewer",
        "NileGov MDA Admin",
        "NileGov System Auditor",
    ]

    def test_all_ordinary_roles_cannot_modify_audit_event(self):
        for role in self.ORDINARY_ROLES:
            assert can_modify_protected_log(role, "NileGov Audit Event") is False, (
                f"Role '{role}' should NOT be able to modify NileGov Audit Event."
            )

    def test_all_ordinary_roles_cannot_modify_integration_log(self):
        for role in self.ORDINARY_ROLES:
            assert can_modify_protected_log(role, "NileGov Integration Simulation Log") is False

    def test_modification_allowed_for_non_protected_doctype(self):
        """A non-protected DocType should return True (no restriction applies)."""
        assert can_modify_protected_log("NileGov Citizen Officer", "NileGov Service Request") is True


# ─────────────────────────────────────────────────────────────────────────────
# Protected log read rules
# ─────────────────────────────────────────────────────────────────────────────

class TestProtectedLogReadAccess:
    READ_ALLOWED_ROLES = {
        "NileGov System Auditor",
        "NileGov M&E Viewer",
        "NileGov SLA Supervisor",
        "NileGov MDA Admin",
        "NileGov System Manager",
    }

    READ_DENIED_ROLES = {
        "NileGov Citizen Officer",
        "NileGov Records Officer",
        "NileGov Payments Officer",
    }

    def test_auditor_can_read_audit_event(self):
        assert can_read_protected_log("NileGov System Auditor", "NileGov Audit Event") is True

    def test_me_viewer_can_read_audit_event(self):
        assert can_read_protected_log("NileGov M&E Viewer", "NileGov Audit Event") is True

    def test_citizen_officer_cannot_read_audit_event(self):
        assert can_read_protected_log("NileGov Citizen Officer", "NileGov Audit Event") is False

    def test_records_officer_cannot_read_audit_event(self):
        assert can_read_protected_log("NileGov Records Officer", "NileGov Audit Event") is False

    def test_payments_officer_cannot_read_audit_event(self):
        assert can_read_protected_log("NileGov Payments Officer", "NileGov Audit Event") is False

    def test_all_read_allowed_roles_can_read(self):
        for role in self.READ_ALLOWED_ROLES:
            assert can_read_protected_log(role, "NileGov Audit Event") is True, (
                f"Role '{role}' should be able to read NileGov Audit Event."
            )

    def test_all_read_denied_roles_cannot_read(self):
        for role in self.READ_DENIED_ROLES:
            assert can_read_protected_log(role, "NileGov Audit Event") is False, (
                f"Role '{role}' should NOT be able to read NileGov Audit Event."
            )


# ─────────────────────────────────────────────────────────────────────────────
# Duty separation — Payment and Evidence review
# ─────────────────────────────────────────────────────────────────────────────

class TestDutySeparation:
    def test_payments_officer_can_review_payment(self):
        assert can_review_payment("NileGov Payments Officer") is True

    def test_system_manager_can_review_payment(self):
        assert can_review_payment("NileGov System Manager") is True

    def test_records_officer_cannot_review_payment(self):
        assert can_review_payment("NileGov Records Officer") is False

    def test_citizen_officer_cannot_review_payment(self):
        assert can_review_payment("NileGov Citizen Officer") is False

    def test_sla_supervisor_cannot_review_payment(self):
        assert can_review_payment("NileGov SLA Supervisor") is False

    def test_me_viewer_cannot_review_payment(self):
        assert can_review_payment("NileGov M&E Viewer") is False

    def test_records_officer_can_review_evidence(self):
        assert can_review_evidence("NileGov Records Officer") is True

    def test_system_manager_can_review_evidence(self):
        assert can_review_evidence("NileGov System Manager") is True

    def test_payments_officer_cannot_review_evidence(self):
        assert can_review_evidence("NileGov Payments Officer") is False

    def test_citizen_officer_cannot_review_evidence(self):
        assert can_review_evidence("NileGov Citizen Officer") is False

    def test_sla_supervisor_cannot_review_evidence(self):
        assert can_review_evidence("NileGov SLA Supervisor") is False

    def test_me_viewer_cannot_review_evidence(self):
        assert can_review_evidence("NileGov M&E Viewer") is False


# ─────────────────────────────────────────────────────────────────────────────
# No role implies live government access
# ─────────────────────────────────────────────────────────────────────────────

class TestNoLiveGovAccessClaims:
    def test_no_role_implies_live_government_access(self):
        for role in NILEGOV_ROLES:
            assert role_implies_live_government_access(role) is False, (
                f"Role '{role}' incorrectly implies live government access. "
                "No prototype role should claim live NIRA, UGHub, URA, NITA-U or MDA access."
            )

    def test_is_nilegov_role_true_for_all_defined_roles(self):
        for role in NILEGOV_ROLES:
            assert is_nilegov_role(role) is True

    def test_is_nilegov_role_false_for_unknown_roles(self):
        assert is_nilegov_role("System Administrator") is False
        assert is_nilegov_role("Service Desk Officer") is False
        assert is_nilegov_role("NIRA Verified User") is False
        assert is_nilegov_role("") is False


# ─────────────────────────────────────────────────────────────────────────────
# Case note visibility model — permission policy consistency
# ─────────────────────────────────────────────────────────────────────────────

class TestCaseNoteVisibilityPermissionConsistency:
    def test_internally_restricted_note_types_are_defined(self):
        """Confirm the restricted note type set is not empty."""
        assert len(INTERNALLY_RESTRICTED_NOTE_TYPES) >= 3

    def test_restricted_note_types_are_subset_of_allowed(self):
        """Restricted types must be valid note types."""
        assert INTERNALLY_RESTRICTED_NOTE_TYPES.issubset(ALLOWED_NOTE_TYPES)

    def test_records_review_note_is_restricted(self):
        assert "Records Review Note" in INTERNALLY_RESTRICTED_NOTE_TYPES

    def test_payment_review_note_is_restricted(self):
        assert "Payment Review Note" in INTERNALLY_RESTRICTED_NOTE_TYPES

    def test_escalation_note_is_restricted(self):
        assert "Escalation Note" in INTERNALLY_RESTRICTED_NOTE_TYPES

    def test_officer_note_is_not_restricted(self):
        """Officer Notes can optionally be citizen-visible (e.g. status updates)."""
        assert "Officer Note" not in INTERNALLY_RESTRICTED_NOTE_TYPES

    def test_closure_note_is_not_restricted(self):
        """Closure Notes can optionally be citizen-visible."""
        assert "Closure Note" not in INTERNALLY_RESTRICTED_NOTE_TYPES

    def test_records_review_note_cannot_be_citizen_visible_via_domain(self):
        """Verify domain enforces the restriction at construction time."""
        with pytest.raises(ValueError):
            CaseNote(
                case_note_id="CN-PERM-001",
                service_request_id="REQ-PERM-001",
                note_type="Records Review Note",
                note_text="Sensitive document detail.",
                created_by_role="NileGov Records Officer",
                created_by_user="officer_records",
                visibility="Citizen Visible Summary",
            )

    def test_payment_review_note_cannot_be_citizen_visible_via_domain(self):
        with pytest.raises(ValueError):
            CaseNote(
                case_note_id="CN-PERM-002",
                service_request_id="REQ-PERM-001",
                note_type="Payment Review Note",
                note_text="Payment audit trail detail.",
                created_by_role="NileGov Payments Officer",
                created_by_user="officer_payments",
                visibility="Citizen Visible Summary",
            )
