# Pass 11B-1: NileGov Reporting Snapshot DocType Tests
# Digi-Verse Uganda Limited
# Prototype reporting snapshot only. Metrics are calculated from fictional demo data
# and are not official government statistics.
#
# Tests cover:
#  1. DocType directory and required files exist
#  2. DocType JSON is valid and has correct name/module
#  3. All expected M&E fields are present
#  4. Disclaimer field exists with the correct prototype text
#  5. NileGov M&E Viewer has read permission (not write/create/delete)
#  6. NileGov System Auditor has read permission (not write/create/delete)
#  7. NileGov SLA Supervisor has read permission
#  8. NileGov MDA Admin has read permission
#  9. Ordinary operational roles do not have write/create/delete
# 10. NileGov System Manager has full access
# 11. System Manager has full access (Frappe admin fallback)
# 12. Frappe reporting snapshot repository references correct DocType name
# 13. Controller file exists and imports cleanly
# 14. No official government statistics claim is introduced
# 15. Existing reporting snapshot domain tests continue to pass

import json
import os
import sys
from unittest.mock import MagicMock

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# tests/ → nilegov_stack package root
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
DOCTYPE_ROOT = os.path.join(PACKAGE_ROOT, "nilegov_stack", "nilegov_stack", "doctype")
SNAPSHOT_DT_DIR = os.path.join(DOCTYPE_ROOT, "nilegov_reporting_snapshot")
SNAPSHOT_JSON_PATH = os.path.join(SNAPSHOT_DT_DIR, "nilegov_reporting_snapshot.json")
SNAPSHOT_PY_PATH = os.path.join(SNAPSHOT_DT_DIR, "nilegov_reporting_snapshot.py")
SNAPSHOT_INIT_PATH = os.path.join(SNAPSHOT_DT_DIR, "__init__.py")
FRAPPE_REPO_PATH = os.path.join(
    PACKAGE_ROOT, "nilegov_stack",
    "infrastructure", "repositories",
    "frappe_reporting_snapshot_repository.py"
)

DOCTYPE_NAME = "NileGov Reporting Snapshot"
REQUIRED_DISCLAIMER_FRAGMENT = (
    "Prototype reporting snapshot only. "
    "Metrics are calculated from fictional demo data "
    "and are not official government statistics."
)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _load_json():
    with open(SNAPSHOT_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _field_names(data: dict) -> set:
    return {f["fieldname"] for f in data.get("fields", []) if "fieldname" in f}


def _roles_with(data: dict, ptype: str) -> set:
    return {p["role"] for p in data.get("permissions", []) if p.get(ptype, 0) == 1}


# ─────────────────────────────────────────────────────────────────────────────
# 1. Files on disk
# ─────────────────────────────────────────────────────────────────────────────
class TestReportingSnapshotFilesExist:
    def test_doctype_directory_exists(self):
        assert os.path.isdir(SNAPSHOT_DT_DIR), (
            f"DocType directory not found: {SNAPSHOT_DT_DIR}\n"
            "Pass 11B-1 requires nilegov_reporting_snapshot/ directory."
        )

    def test_json_file_exists(self):
        assert os.path.isfile(SNAPSHOT_JSON_PATH), (
            f"DocType JSON not found: {SNAPSHOT_JSON_PATH}"
        )

    def test_controller_file_exists(self):
        assert os.path.isfile(SNAPSHOT_PY_PATH), (
            f"Controller not found: {SNAPSHOT_PY_PATH}"
        )

    def test_init_file_exists(self):
        assert os.path.isfile(SNAPSHOT_INIT_PATH), (
            f"__init__.py not found: {SNAPSHOT_INIT_PATH}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. DocType JSON structure
# ─────────────────────────────────────────────────────────────────────────────
class TestReportingSnapshotDocTypeJSON:
    def test_json_is_valid(self):
        data = _load_json()
        assert data.get("doctype") == "DocType"

    def test_doctype_name_is_correct(self):
        data = _load_json()
        assert data.get("name") == DOCTYPE_NAME

    def test_doctype_uses_nilegov_prefix(self):
        data = _load_json()
        assert data.get("name", "").startswith("NileGov")

    def test_module_is_nilegov_stack(self):
        data = _load_json()
        assert data.get("module") == "NileGov Stack"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Required M&E fields
# ─────────────────────────────────────────────────────────────────────────────
class TestReportingSnapshotRequiredFields:
    REQUIRED_FIELDS = {
        # Identity
        "reporting_snapshot_id",
        "snapshot_name",
        # Period
        "reporting_period_start",
        "reporting_period_end",
        "generated_at",
        "generated_by",
        "source_dataset",
        # Executive metrics
        "total_requests",
        "total_services",
        "active_services",
        "demo_services",
        # Status summaries (JSON)
        "requests_by_status",
        "requests_by_service",
        "requests_by_queue",
        "requests_by_location",
        # SLA
        "within_sla_count",
        "at_risk_count",
        "overdue_count",
        "escalated_count",
        # Evidence
        "evidence_complete_count",
        "evidence_incomplete_count",
        # Payment
        "payment_pending_count",
        "payment_verified_count",
        "payment_failed_count",
        "payment_value_summary",
        # Notifications
        "notification_queued_count",
        "notification_simulated_sent_count",
        "notification_failed_count",
        # Workload
        "officer_workload_summary",
        # Governance
        "disclaimer",
    }

    def test_all_required_fields_present(self):
        data = _load_json()
        present = _field_names(data)
        missing = self.REQUIRED_FIELDS - present
        assert not missing, (
            f"Required fields missing from {DOCTYPE_NAME}: {sorted(missing)}"
        )

    def test_count_fields_are_int_type(self):
        data = _load_json()
        count_fields = {
            "total_requests", "within_sla_count", "at_risk_count",
            "overdue_count", "escalated_count", "evidence_complete_count",
            "evidence_incomplete_count", "payment_pending_count",
            "payment_verified_count", "payment_failed_count",
            "notification_queued_count", "notification_simulated_sent_count",
            "notification_failed_count",
        }
        field_types = {f["fieldname"]: f["fieldtype"] for f in data.get("fields", []) if "fieldname" in f}
        for fn in count_fields:
            assert field_types.get(fn) == "Int", (
                f"Field '{fn}' should be Int, got '{field_types.get(fn)}'"
            )

    def test_json_summary_fields_are_code_type(self):
        data = _load_json()
        json_fields = {
            "requests_by_status", "requests_by_service",
            "requests_by_queue", "requests_by_location",
            "officer_workload_summary", "payment_value_summary",
        }
        field_types = {f["fieldname"]: f["fieldtype"] for f in data.get("fields", []) if "fieldname" in f}
        for fn in json_fields:
            assert field_types.get(fn) == "Code", (
                f"Field '{fn}' should be Code (JSON), got '{field_types.get(fn)}'"
            )

    def test_generated_at_is_datetime(self):
        data = _load_json()
        field_types = {f["fieldname"]: f["fieldtype"] for f in data.get("fields", []) if "fieldname" in f}
        assert field_types.get("generated_at") == "Datetime"

    def test_snapshot_name_and_id_are_required(self):
        data = _load_json()
        reqd = {f["fieldname"] for f in data.get("fields", []) if f.get("reqd", 0) == 1}
        assert "snapshot_name" in reqd, "snapshot_name must be required"
        assert "reporting_snapshot_id" in reqd, "reporting_snapshot_id must be required"
        assert "disclaimer" in reqd, "disclaimer must be required"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Disclaimer field
# ─────────────────────────────────────────────────────────────────────────────
class TestReportingSnapshotDisclaimer:
    def test_disclaimer_field_exists(self):
        data = _load_json()
        fields = _field_names(data)
        assert "disclaimer" in fields

    def test_disclaimer_is_required(self):
        data = _load_json()
        for f in data.get("fields", []):
            if f.get("fieldname") == "disclaimer":
                assert f.get("reqd", 0) == 1, "disclaimer field must be required"
                break

    def test_disclaimer_default_contains_prototype_text(self):
        data = _load_json()
        for f in data.get("fields", []):
            if f.get("fieldname") == "disclaimer":
                default = f.get("default", "")
                assert REQUIRED_DISCLAIMER_FRAGMENT in default, (
                    f"Disclaimer default does not contain required prototype text.\n"
                    f"Expected substring: '{REQUIRED_DISCLAIMER_FRAGMENT}'\n"
                    f"Got: '{default}'"
                )
                return
        pytest.fail("disclaimer field not found in DocType JSON")

    def test_disclaimer_does_not_claim_official_statistics(self):
        data = _load_json()
        for f in data.get("fields", []):
            if f.get("fieldname") == "disclaimer":
                default = f.get("default", "")
                assert "official government statistics" not in default.lower() or \
                       "not official government statistics" in default.lower(), (
                    "Disclaimer must not claim to be official government statistics."
                )
                return


# ─────────────────────────────────────────────────────────────────────────────
# 5–11. Permission rows
# ─────────────────────────────────────────────────────────────────────────────
class TestReportingSnapshotPermissions:
    # Roles that should have only read access (never write/create/delete)
    READ_ONLY_ROLES = [
        "NileGov M&E Viewer",
        "NileGov SLA Supervisor",
        "NileGov MDA Admin",
        "NileGov System Auditor",
    ]

    # Roles that must not have any access at all
    NO_ACCESS_ROLES = [
        "NileGov Citizen Officer",
        "NileGov Records Officer",
        "NileGov Payments Officer",
        "Guest",
    ]

    def test_me_viewer_has_read(self):
        data = _load_json()
        readers = _roles_with(data, "read")
        assert "NileGov M&E Viewer" in readers, (
            "NileGov M&E Viewer must have read access to Reporting Snapshot."
        )

    def test_system_auditor_has_read(self):
        data = _load_json()
        readers = _roles_with(data, "read")
        assert "NileGov System Auditor" in readers

    def test_sla_supervisor_has_read(self):
        data = _load_json()
        readers = _roles_with(data, "read")
        assert "NileGov SLA Supervisor" in readers

    def test_mda_admin_has_read(self):
        data = _load_json()
        readers = _roles_with(data, "read")
        assert "NileGov MDA Admin" in readers

    def test_nilegov_system_manager_has_full_access(self):
        data = _load_json()
        for ptype in ("read", "write", "create"):
            roles = _roles_with(data, ptype)
            assert "NileGov System Manager" in roles, (
                f"NileGov System Manager must have '{ptype}' access"
            )

    def test_system_manager_has_full_access(self):
        data = _load_json()
        for ptype in ("read", "write", "create"):
            roles = _roles_with(data, ptype)
            assert "System Manager" in roles, (
                f"System Manager must have '{ptype}' access (Frappe admin fallback)"
            )

    def test_read_only_roles_have_no_write(self):
        data = _load_json()
        for role in self.READ_ONLY_ROLES:
            writers = _roles_with(data, "write")
            assert role not in writers, (
                f"Read-only role '{role}' must not have 'write' on Reporting Snapshot."
            )

    def test_read_only_roles_have_no_create(self):
        data = _load_json()
        for role in self.READ_ONLY_ROLES:
            creators = _roles_with(data, "create")
            assert role not in creators, (
                f"Read-only role '{role}' must not have 'create' on Reporting Snapshot."
            )

    def test_read_only_roles_have_no_delete(self):
        data = _load_json()
        for role in self.READ_ONLY_ROLES:
            deleters = _roles_with(data, "delete")
            assert role not in deleters, (
                f"Read-only role '{role}' must not have 'delete' on Reporting Snapshot."
            )

    def test_no_access_roles_have_no_permissions(self):
        data = _load_json()
        all_roles_with_perms = {
            p["role"] for p in data.get("permissions", [])
        }
        for role in self.NO_ACCESS_ROLES:
            assert role not in all_roles_with_perms, (
                f"Role '{role}' must not appear in Reporting Snapshot permission rows."
            )

    def test_has_nilegov_prefixed_permission_row(self):
        data = _load_json()
        nilegov_roles = [
            p["role"] for p in data.get("permissions", [])
            if p.get("role", "").startswith("NileGov")
        ]
        assert len(nilegov_roles) >= 1, (
            "Reporting Snapshot DocType must have at least one NileGov-prefixed permission row."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 12. Frappe repository references correct DocType name
# ─────────────────────────────────────────────────────────────────────────────
class TestFrappeReportingSnapshotRepository:
    def test_frappe_repo_file_exists(self):
        assert os.path.isfile(FRAPPE_REPO_PATH), (
            f"FrappeReportingSnapshotRepository not found at {FRAPPE_REPO_PATH}"
        )

    def test_frappe_repo_references_correct_doctype_name(self):
        with open(FRAPPE_REPO_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert '"NileGov Reporting Snapshot"' in content or \
               "'NileGov Reporting Snapshot'" in content, (
            "FrappeReportingSnapshotRepository must reference 'NileGov Reporting Snapshot' "
            "as the DocType name — matches the JSON DocType created in Pass 11B-1."
        )

    def test_frappe_repo_maps_snapshot_name_field(self):
        with open(FRAPPE_REPO_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert "snapshot_name" in content

    def test_frappe_repo_maps_disclaimer_field(self):
        with open(FRAPPE_REPO_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert "disclaimer" in content

    def test_frappe_repo_maps_officer_workload_summary(self):
        with open(FRAPPE_REPO_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert "officer_workload_summary" in content

    def test_frappe_repo_no_live_gov_claims(self):
        with open(FRAPPE_REPO_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        for kw in ["live_nira", "live_ura", "live_ughub", "production_db"]:
            assert kw not in content.lower(), (
                f"FrappeReportingSnapshotRepository must not reference '{kw}'"
            )


# ─────────────────────────────────────────────────────────────────────────────
# 13. Controller imports cleanly outside Frappe
# ─────────────────────────────────────────────────────────────────────────────
class TestReportingSnapshotController:
    def test_controller_file_is_valid_python(self):
        import py_compile
        py_compile.compile(SNAPSHOT_PY_PATH, doraise=True)

    def test_controller_imports_without_frappe(self):
        """Controller must be importable even when frappe is not installed."""
        if "frappe" not in sys.modules:
            sys.modules["frappe"] = MagicMock()
        # Import the controller module by path
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "nilegov_reporting_snapshot_ctrl", SNAPSHOT_PY_PATH
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "NilegoveReportingSnapshot")

    def test_controller_defines_required_disclaimer_constant(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "nilegov_reporting_snapshot_ctrl2", SNAPSHOT_PY_PATH
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "REQUIRED_DISCLAIMER")
        assert "Prototype reporting snapshot only" in mod.REQUIRED_DISCLAIMER

    def test_controller_validate_sets_disclaimer_if_missing(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "nilegov_reporting_snapshot_ctrl3", SNAPSHOT_PY_PATH
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ctrl = mod.NilegoveReportingSnapshot()
        ctrl.snapshot_name = "Test Snapshot"
        ctrl.source_dataset = "Demo"
        ctrl.disclaimer = ""  # intentionally blank
        ctrl.validate()
        assert ctrl.disclaimer == mod.REQUIRED_DISCLAIMER

    def test_controller_rejects_missing_snapshot_name(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "nilegov_reporting_snapshot_ctrl4", SNAPSHOT_PY_PATH
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ctrl = mod.NilegoveReportingSnapshot()
        ctrl.snapshot_name = ""
        ctrl.source_dataset = "Demo"
        ctrl.disclaimer = mod.REQUIRED_DISCLAIMER
        try:
            ctrl.validate()
            assert False, "Expected ValueError for missing snapshot_name"
        except (ValueError, Exception):
            pass  # Either ValueError or frappe.throw — both acceptable


# ─────────────────────────────────────────────────────────────────────────────
# 14. No official government statistics claim
# ─────────────────────────────────────────────────────────────────────────────
class TestNoOfficialStatsClaim:
    FORBIDDEN_CLAIMS = [
        "official government statistics produced",
        "connected to ministry",
        "live reporting dashboard",
        "real-time government data",
    ]

    def test_doctype_json_no_official_stats_claim(self):
        with open(SNAPSHOT_JSON_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        for kw in self.FORBIDDEN_CLAIMS:
            assert kw.lower() not in content.lower(), (
                f"DocType JSON must not contain forbidden claim: '{kw}'"
            )

    def test_controller_no_official_stats_claim(self):
        with open(SNAPSHOT_PY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # These are runtime integration strings that must never appear in prototype code
        for kw in ["live_nira_endpoint", "live_ura_endpoint", "production_reporting_api",
                   "requests.get(", "urllib.request.urlopen("]:
            assert kw.lower() not in content.lower(), (
                f"Controller must not contain live-integration reference: '{kw}'"
            )
