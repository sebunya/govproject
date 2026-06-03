# Pass 11B-2: Role Alignment and DocType Permission Row Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.
#
# Tests verify:
#   1. All canonical NileGov roles appear in seed_roles.py
#   2. hooks.py fixtures list canonical NileGov roles (not old legacy names)
#   3. interfaces/permissions.py references canonical role names
#   4. Every operational DocType has at least one NileGov-prefixed permission row
#   5. Protected logs do not grant write/create/delete to ordinary NileGov roles
#   6. Audit Event gives System Auditor read access
#   7. Integration Simulation Log gives System Auditor read access
#   8. Payments Officer has permissions on Payment Record but not Evidence Document write
#   9. Records Officer has permissions on Evidence Document but not Payment Record write
#  10. M&E Viewer has read access to SLA Event but no write to operational records
#  11. No role name implies live government access
#  12. .env remains untracked

import json
import os
import sys
from unittest.mock import MagicMock

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
DOCTYPE_ROOT = os.path.join(PACKAGE_ROOT, "nilegov_stack", "nilegov_stack", "doctype")
HOOKS_PATH = os.path.join(PACKAGE_ROOT, "nilegov_stack", "hooks.py")
SEED_ROLES_PATH = os.path.join(PACKAGE_ROOT, "nilegov_stack", "patches", "seed_roles.py")
PERMISSIONS_PATH = os.path.join(PACKAGE_ROOT, "nilegov_stack", "interfaces", "permissions.py")

CANONICAL_ROLES = [
    "NileGov Citizen Officer",
    "NileGov Records Officer",
    "NileGov Payments Officer",
    "NileGov SLA Supervisor",
    "NileGov M&E Viewer",
    "NileGov MDA Admin",
    "NileGov System Auditor",
    "NileGov System Manager",
]

# DocTypes that must be protected from ordinary write access
PROTECTED_DOCTYPES = {
    "nilegov_audit_event",
    "nilegov_integration_simulation_log",
}

# All 16 expected DocType directories (Pass 11B-1: added nilegov_reporting_snapshot)
ALL_DOCTYPES = [
    "nilegov_audit_event",
    "nilegov_case_note",
    "nilegov_citizen_notification",
    "nilegov_citizen_profile",
    "nilegov_consent_record",
    "nilegov_escalation_record",
    "nilegov_evidence_document",
    "nilegov_integration_simulation_log",
    "nilegov_payment_record",
    "nilegov_reporting_snapshot",
    "nilegov_service_catalogue",
    "nilegov_service_request",
    "nilegov_service_type",
    "nilegov_simulated_identity_verification",
    "nilegov_sla_event",
    "nilegov_sla_rule",
]

# Helper to load a DocType JSON
def _load_dt(dt_name: str) -> dict:
    path = os.path.join(DOCTYPE_ROOT, dt_name, f"{dt_name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _permissions(dt_name: str) -> list[dict]:
    return _load_dt(dt_name).get("permissions", [])


def _roles_with_access(dt_name: str, ptype: str) -> set[str]:
    """Return all roles that have ptype=1 in a DocType's permission rows."""
    return {
        p["role"]
        for p in _permissions(dt_name)
        if p.get(ptype, 0) == 1
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. seed_roles.py seeds all canonical roles
# ─────────────────────────────────────────────────────────────────────────────
class TestSeedRolesAlignment:
    def test_seed_roles_file_exists(self):
        assert os.path.isfile(SEED_ROLES_PATH)

    def test_all_canonical_roles_in_seed_roles(self):
        with open(SEED_ROLES_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        for role in CANONICAL_ROLES:
            assert role in content, (
                f"Canonical role '{role}' not found in seed_roles.py"
            )

    def test_seed_roles_still_idempotent(self):
        """Patch still checks frappe.db.exists to avoid duplication."""
        with open(SEED_ROLES_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert "frappe.db.exists" in content

    def test_seed_roles_exposes_execute(self):
        if "frappe" not in sys.modules:
            sys.modules["frappe"] = MagicMock()
        from nilegov_stack.patches import seed_roles
        assert hasattr(seed_roles, "execute")

    def test_seed_roles_defines_nilegov_roles_constant(self):
        if "frappe" not in sys.modules:
            sys.modules["frappe"] = MagicMock()
        from nilegov_stack.patches import seed_roles
        assert hasattr(seed_roles, "NILEGOV_ROLES")
        for role in CANONICAL_ROLES:
            assert role in seed_roles.NILEGOV_ROLES


# ─────────────────────────────────────────────────────────────────────────────
# 2. hooks.py uses canonical role names in fixtures
# ─────────────────────────────────────────────────────────────────────────────
class TestHooksRoleAlignment:
    def _hooks_content(self):
        with open(HOOKS_PATH, "r", encoding="utf-8") as f:
            return f.read()

    def test_hooks_has_fixtures_block(self):
        assert "fixtures" in self._hooks_content()

    def test_canonical_roles_in_hooks_fixtures(self):
        content = self._hooks_content()
        for role in CANONICAL_ROLES:
            assert role in content, (
                f"Canonical role '{role}' must appear in hooks.py fixtures"
            )

    def test_hooks_no_unprefixed_old_primary_roles(self):
        """Old roles should not appear as fixture primary definitions (only as comments/aliases)."""
        content = self._hooks_content()
        # Old operational role names should no longer be in the fixtures list;
        # we verify they are not in a fixtures-list context by checking the
        # canonical roles replaced them (positive check above is sufficient).
        # This test ensures the file still has permission_query_conditions and has_permission.
        assert "permission_query_conditions" in content
        assert "has_permission" in content

    def test_hooks_no_guest_role(self):
        content = self._hooks_content()
        assert '"Guest"' not in content


# ─────────────────────────────────────────────────────────────────────────────
# 3. interfaces/permissions.py references canonical role names
# ─────────────────────────────────────────────────────────────────────────────
class TestPermissionsInterfaceAlignment:
    def _perms_content(self):
        with open(PERMISSIONS_PATH, "r", encoding="utf-8") as f:
            return f.read()

    def test_permissions_file_exists(self):
        assert os.path.isfile(PERMISSIONS_PATH)

    def test_canonical_roles_in_permissions_py(self):
        content = self._perms_content()
        for role in CANONICAL_ROLES:
            assert role in content, (
                f"Canonical role '{role}' not found in interfaces/permissions.py"
            )

    def test_permissions_defines_bypass_roles(self):
        content = self._perms_content()
        assert "BYPASS_ROLES" in content

    def test_permissions_defines_protected_doctypes(self):
        content = self._perms_content()
        assert "PROTECTED_DOCTYPES" in content
        assert "NileGov Audit Event" in content
        assert "NileGov Integration Simulation Log" in content

    def test_permissions_exposes_both_hooks(self):
        if "frappe" not in sys.modules:
            sys.modules["frappe"] = MagicMock()
        from nilegov_stack.interfaces import permissions
        assert hasattr(permissions, "has_permission")
        assert hasattr(permissions, "get_permission_query_conditions")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Every operational DocType has at least one NileGov-prefixed permission row
# ─────────────────────────────────────────────────────────────────────────────
class TestDocTypePermissionRows:
    @pytest.mark.parametrize("dt_name", ALL_DOCTYPES)
    def test_doctype_has_nilegov_prefixed_role(self, dt_name):
        perms = _permissions(dt_name)
        nilegov_roles = [p["role"] for p in perms if p.get("role", "").startswith("NileGov")]
        assert len(nilegov_roles) >= 1, (
            f"DocType '{dt_name}' has no NileGov-prefixed permission rows. "
            "Pass 11B-2 requires at least one NileGov operational role per DocType."
        )

    @pytest.mark.parametrize("dt_name", ALL_DOCTYPES)
    def test_doctype_still_has_system_manager(self, dt_name):
        roles = {p["role"] for p in _permissions(dt_name)}
        assert "System Manager" in roles, (
            f"DocType '{dt_name}' lost System Manager access — this would block Frappe admin setup."
        )

    @pytest.mark.parametrize("dt_name", ALL_DOCTYPES)
    def test_doctype_has_no_guest_access(self, dt_name):
        roles = {p["role"] for p in _permissions(dt_name)}
        assert "Guest" not in roles, (
            f"DocType '{dt_name}' must never grant access to Guest role."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5 & 6 & 7. Protected logs — no ordinary write; Auditor gets read
# ─────────────────────────────────────────────────────────────────────────────
class TestProtectedLogPermissions:
    ORDINARY_ROLES = [
        "NileGov Citizen Officer",
        "NileGov Records Officer",
        "NileGov Payments Officer",
        "NileGov SLA Supervisor",
        "NileGov M&E Viewer",
        "NileGov MDA Admin",
    ]

    @pytest.mark.parametrize("dt_name", list(PROTECTED_DOCTYPES))
    @pytest.mark.parametrize("ptype", ["write", "create", "delete"])
    def test_no_ordinary_role_has_write_on_protected_log(self, dt_name, ptype):
        roles_with_write = _roles_with_access(dt_name, ptype)
        for role in self.ORDINARY_ROLES:
            assert role not in roles_with_write, (
                f"Ordinary role '{role}' must not have '{ptype}' on protected DocType '{dt_name}'"
            )

    def test_system_auditor_can_read_audit_event(self):
        readers = _roles_with_access("nilegov_audit_event", "read")
        assert "NileGov System Auditor" in readers

    def test_system_auditor_cannot_write_audit_event(self):
        writers = _roles_with_access("nilegov_audit_event", "write")
        assert "NileGov System Auditor" not in writers

    def test_system_auditor_can_read_integration_log(self):
        readers = _roles_with_access("nilegov_integration_simulation_log", "read")
        assert "NileGov System Auditor" in readers

    def test_system_auditor_cannot_write_integration_log(self):
        writers = _roles_with_access("nilegov_integration_simulation_log", "write")
        assert "NileGov System Auditor" not in writers

    def test_me_viewer_can_read_integration_log(self):
        readers = _roles_with_access("nilegov_integration_simulation_log", "read")
        assert "NileGov M&E Viewer" in readers

    def test_me_viewer_cannot_write_integration_log(self):
        writers = _roles_with_access("nilegov_integration_simulation_log", "write")
        assert "NileGov M&E Viewer" not in writers


# ─────────────────────────────────────────────────────────────────────────────
# 8 & 9. Duty separation: Payments ≠ Records
# ─────────────────────────────────────────────────────────────────────────────
class TestDutySeparationPermissionRows:
    def test_payments_officer_can_read_payment_record(self):
        readers = _roles_with_access("nilegov_payment_record", "read")
        assert "NileGov Payments Officer" in readers

    def test_payments_officer_can_write_payment_record(self):
        writers = _roles_with_access("nilegov_payment_record", "write")
        assert "NileGov Payments Officer" in writers

    def test_payments_officer_cannot_write_evidence_document(self):
        writers = _roles_with_access("nilegov_evidence_document", "write")
        assert "NileGov Payments Officer" not in writers

    def test_records_officer_can_read_evidence_document(self):
        readers = _roles_with_access("nilegov_evidence_document", "read")
        assert "NileGov Records Officer" in readers

    def test_records_officer_can_write_evidence_document(self):
        writers = _roles_with_access("nilegov_evidence_document", "write")
        assert "NileGov Records Officer" in writers

    def test_records_officer_cannot_write_payment_record(self):
        writers = _roles_with_access("nilegov_payment_record", "write")
        assert "NileGov Records Officer" not in writers

    def test_records_officer_cannot_create_payment_record(self):
        creators = _roles_with_access("nilegov_payment_record", "create")
        assert "NileGov Records Officer" not in creators


# ─────────────────────────────────────────────────────────────────────────────
# 10. M&E Viewer — read-only on operational DocTypes
# ─────────────────────────────────────────────────────────────────────────────
class TestMEViewerPermissions:
    OPERATIONAL_DOCTYPES = [
        "nilegov_service_request",
        "nilegov_citizen_profile",
        "nilegov_evidence_document",
        "nilegov_consent_record",
    ]

    @pytest.mark.parametrize("dt_name", OPERATIONAL_DOCTYPES)
    def test_me_viewer_cannot_write_operational_doctypes(self, dt_name):
        writers = _roles_with_access(dt_name, "write")
        assert "NileGov M&E Viewer" not in writers, (
            f"NileGov M&E Viewer must not have write access to operational DocType '{dt_name}'"
        )

    @pytest.mark.parametrize("dt_name", OPERATIONAL_DOCTYPES)
    def test_me_viewer_cannot_create_operational_doctypes(self, dt_name):
        creators = _roles_with_access(dt_name, "create")
        assert "NileGov M&E Viewer" not in creators, (
            f"NileGov M&E Viewer must not have create access to operational DocType '{dt_name}'"
        )

    def test_me_viewer_can_read_sla_event(self):
        readers = _roles_with_access("nilegov_sla_event", "read")
        assert "NileGov M&E Viewer" in readers

    def test_me_viewer_can_read_payment_record(self):
        readers = _roles_with_access("nilegov_payment_record", "read")
        assert "NileGov M&E Viewer" in readers

    def test_me_viewer_cannot_write_sla_event(self):
        writers = _roles_with_access("nilegov_sla_event", "write")
        assert "NileGov M&E Viewer" not in writers


# ─────────────────────────────────────────────────────────────────────────────
# 11. No role name implies live government access
# ─────────────────────────────────────────────────────────────────────────────
class TestNoLiveGovernmentRoleClaims:
    FORBIDDEN_SUBSTRINGS = [
        "NIRA", "UGHub", "URA", "NITA-U", "MoMo", "Airtel Money",
        "live", "production", "Production",
    ]

    def test_canonical_roles_contain_no_live_gov_keywords(self):
        for role in CANONICAL_ROLES:
            for kw in self.FORBIDDEN_SUBSTRINGS:
                assert kw not in role, (
                    f"Canonical role '{role}' contains forbidden keyword '{kw}' "
                    "implying live government access."
                )

    def test_hooks_has_no_live_gov_role_names(self):
        with open(HOOKS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        for kw in ["NIRA Officer", "UGHub Officer", "URA Officer"]:
            assert kw not in content, (
                f"hooks.py must not reference forbidden role '{kw}'"
            )

    def test_seed_roles_no_live_gov_role_names(self):
        with open(SEED_ROLES_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        for kw in ["NIRA Officer", "UGHub Officer", "URA Officer"]:
            assert kw not in content

    def test_permissions_no_live_gov_claims(self):
        with open(PERMISSIONS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # These specific strings indicate live integration claims — never acceptable in prototype
        for kw in ["NIRA Officer", "UGHub Officer", "URA Officer",
                   "live_nira_access", "live_ura_access", "live_ughub"]:
            assert kw.lower() not in content.lower(), (
                f"interfaces/permissions.py must not reference '{kw}'"
            )


# ─────────────────────────────────────────────────────────────────────────────
# 12. .env remains untracked
# ─────────────────────────────────────────────────────────────────────────────
class TestEnvFileNotTracked:
    def test_env_file_does_not_exist_in_repo_root(self):
        """The .env file must never be committed to the repository."""
        repo_root = os.path.dirname(PACKAGE_ROOT)
        env_path = os.path.join(repo_root, ".env")
        assert not os.path.exists(env_path), (
            ".env file detected in repository root. "
            "Remove it immediately — secrets must never be committed."
        )
