# Static Schema Quality Gate & Verification Tests
# Prototype simulation only. No live Government registry access.

import os
import json
import pytest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate up to the package root apps/nilegov_stack/nilegov_stack/
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
DOCTYPE_ROOT = os.path.join(PACKAGE_ROOT, "nilegov_stack", "nilegov_stack", "doctype")

EXPECTED_DOCTYPES = {
    "nilegov_citizen_profile": "NileGov Citizen Profile",
    "nilegov_service_type": "NileGov Service Type",
    "nilegov_service_request": "NileGov Service Request",
    "nilegov_consent_record": "NileGov Consent Record",
    "nilegov_evidence_document": "NileGov Evidence Document",
    "nilegov_simulated_identity_verification": "NileGov Simulated Identity Verification",
    "nilegov_case_note": "NileGov Case Note",
    "nilegov_sla_rule": "NileGov SLA Rule",
    "nilegov_sla_event": "NileGov SLA Event",
    "nilegov_escalation_record": "NileGov Escalation Record",
    "nilegov_citizen_notification": "NileGov Citizen Notification",
    "nilegov_audit_event": "NileGov Audit Event",
    "nilegov_integration_simulation_log": "NileGov Integration Simulation Log",
    "nilegov_payment_record": "NileGov Payment Record",
    "nilegov_service_catalogue": "NileGov Service Catalogue",
    # Pass 11B-1: Reporting Snapshot DocType added
    "nilegov_reporting_snapshot": "NileGov Reporting Snapshot",
    # Pass 11B-5A: Management Review Note DocType added (Insights & Reporting module)
    "nilegov_management_review_note": "NileGov Management Review Note",
}


def test_doctype_folders_and_files_exist():
    """Verifies that all 16 DocType subdirectories and schema JSON files exist on disk."""
    assert os.path.exists(DOCTYPE_ROOT), f"DocType root directory not found at {DOCTYPE_ROOT}"

    for folder, doctype_name in EXPECTED_DOCTYPES.items():
        folder_path = os.path.join(DOCTYPE_ROOT, folder)
        assert os.path.isdir(folder_path), f"Expected directory not found: {folder_path}"

        json_path = os.path.join(folder_path, f"{folder}.json")
        assert os.path.isfile(json_path), f"Expected schema JSON not found: {json_path}"

        py_path = os.path.join(folder_path, f"{folder}.py")
        assert os.path.isfile(py_path), f"Expected controller script not found: {py_path}"


def test_doctypes_valid_json_and_prefixed():
    """Verifies that JSON files are parseable, and DocType names use NileGov prefix."""
    for folder, doctype_name in EXPECTED_DOCTYPES.items():
        json_path = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.json")

        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON file {json_path}: {e}")

        # Validate DocType properties
        assert data.get("doctype") == "DocType"
        assert data.get("name") == doctype_name
        assert data.get("name").startswith("NileGov"), f"DocType {doctype_name} must start with 'NileGov'"
        assert data.get("module") == "NileGov Stack"


def test_schema_required_fields_exist():
    """Verifies that mandatory transactional schema fields are declared in the JSON files."""
    required_fields_map = {
        "nilegov_citizen_profile": {"full_name", "nin", "location"},
        "nilegov_service_type": {"service_name", "service_code", "default_sla_hours"},
        "nilegov_service_request": {
            "service_request_id", "service_type", "citizen_profile",
            "citizen_full_name", "nin", "location", "internal_status", "citizen_visible_status"
        },
        "nilegov_consent_record": {
            "service_request", "consent_statement", "statement_version",
            "consent_given_by", "consent_given_at", "consent_channel"
        },
        "nilegov_evidence_document": {
            "service_request", "document_type", "file", "uploaded_by", "uploaded_at", "visibility"
        },
        "nilegov_simulated_identity_verification": {
            "service_request", "simulation_status", "verification_source", "response_message", "simulated_at"
        },
        "nilegov_case_note": {"service_request", "note_type", "note", "created_by_user", "created_at"},
        "nilegov_sla_rule": {"service_type", "response_hours", "resolution_hours", "escalation_threshold_hours"},
        "nilegov_sla_event": {"service_request", "event_type", "due_at", "status"},
        "nilegov_escalation_record": {"service_request", "escalation_reason", "escalated_by", "escalated_to", "escalated_at", "status"},
        "nilegov_citizen_notification": {"service_request", "notification_type", "recipient", "channel", "message", "delivery_status"},
        "nilegov_audit_event": {"event_type", "actor", "event_time", "action_summary"},
        "nilegov_integration_simulation_log": {"service_request", "integration_name", "simulation_type", "status", "simulated_at", "disclaimer"},
        "nilegov_payment_record": {"payment_record_id", "service_request", "amount", "payment_status", "verification_status", "disclaimer"},
        "nilegov_service_catalogue": {"service_catalogue_id", "service_name", "service_code", "service_category", "default_payment_provider", "active_status", "workflow_template", "disclaimer"},
        # Pass 11B-1: Reporting Snapshot required fields
        "nilegov_reporting_snapshot": {
            "reporting_snapshot_id", "snapshot_name",
            "reporting_period_start", "reporting_period_end",
            "generated_at", "generated_by", "source_dataset",
            "total_requests", "within_sla_count", "at_risk_count",
            "overdue_count", "escalated_count",
            "evidence_complete_count", "evidence_incomplete_count",
            "payment_pending_count", "payment_verified_count", "payment_failed_count",
            "notification_queued_count", "notification_simulated_sent_count",
            "notification_failed_count", "officer_workload_summary",
            "payment_value_summary", "disclaimer",
        },
    }

    for folder, required_fields in required_fields_map.items():
        json_path = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        fields = {field["fieldname"] for field in data.get("fields", [])}
        for req in required_fields:
            assert req in fields, f"Required field '{req}' missing from DocType '{folder}'"


def test_disclaimer_fields_in_simulation_records():
    """Verifies that simulation-focused DocTypes declare disclaimer or disclaimer-equivalent fields."""
    disclaimer_records = {
        "nilegov_simulated_identity_verification": "response_message",
        "nilegov_integration_simulation_log": "disclaimer",
        "nilegov_payment_record": "disclaimer",
        "nilegov_service_catalogue": "disclaimer",
        # Pass 11B-1: Reporting Snapshot must have a prototype disclaimer
        "nilegov_reporting_snapshot": "disclaimer",
    }

    for folder, fieldname in disclaimer_records.items():
        json_path = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        fields = {field["fieldname"]: field for field in data.get("fields", [])}
        assert fieldname in fields, f"Disclaimer field '{fieldname}' missing in '{folder}'"

        # Verify default disclaimer message
        default_val = fields[fieldname].get("default", "")
        required_msg = "Prototype simulation only. No live Government registry access."
        if folder == "nilegov_payment_record":
            required_msg = "Prototype simulation only. No live payment was processed."
        elif folder == "nilegov_service_catalogue":
            required_msg = "Prototype service catalogue only. Not connected to a live government service registry."
        elif folder == "nilegov_reporting_snapshot":
            required_msg = "Prototype reporting snapshot only. Metrics are calculated from fictional demo data"
        assert required_msg in default_val, (
            f"Disclaimer message mismatch in '{folder}' for field '{fieldname}'. "
            f"Expected it to contain '{required_msg}'"
        )


def test_link_fields_point_to_correct_options():
    """Verifies that Link-type fields connect to expected targets."""
    for folder, doctype_name in EXPECTED_DOCTYPES.items():
        json_path = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for field in data.get("fields", []):
            if field.get("fieldtype") == "Link":
                target = field.get("options")
                assert target, f"Link field '{field['fieldname']}' in '{doctype_name}' must declare options (linked DocType)"

                # If linking to a NileGov custom DocType, assert it maps to a valid one
                if target.startswith("NileGov"):
                    assert target in EXPECTED_DOCTYPES.values(), (
                        f"Field '{field['fieldname']}' in '{doctype_name}' links to unknown custom DocType '{target}'"
                    )


def test_permission_helper_scaffolding_exists():
    """Verifies that the interfaces/permissions.py scaffold file is present and implements hooks."""
    permissions_path = os.path.join(PACKAGE_ROOT, "nilegov_stack", "interfaces", "permissions.py")
    assert os.path.isfile(permissions_path), f"Permissions scaffold helper not found at {permissions_path}"

    with open(permissions_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "def has_permission" in content
    assert "def get_permission_query_conditions" in content


def test_role_fixtures_and_patches_exist():
    """Verifies that canonical NileGov roles are registered in hooks.py and patches.txt."""
    hooks_path = os.path.join(PACKAGE_ROOT, "nilegov_stack", "hooks.py")
    assert os.path.isfile(hooks_path)

    with open(hooks_path, "r", encoding="utf-8") as f:
        hooks_content = f.read()

    # Check fixtures registration
    assert "fixtures" in hooks_content

    # Canonical NileGov-prefixed roles (Pass 11B-2)
    canonical_roles = [
        "NileGov Citizen Officer",
        "NileGov Records Officer",
        "NileGov Payments Officer",
        "NileGov SLA Supervisor",
        "NileGov M&E Viewer",
        "NileGov MDA Admin",
        "NileGov System Auditor",
        "NileGov System Manager",
    ]
    for role in canonical_roles:
        assert role in hooks_content, (
            f"Canonical role '{role}' not found in hooks.py fixtures. "
            "Pass 11B-2 requires all NileGov-prefixed roles to be registered."
        )

    # Check query permission mappings
    assert "permission_query_conditions" in hooks_content
    assert "has_permission" in hooks_content

    # Check patches registration
    patches_path = os.path.join(PACKAGE_ROOT, "nilegov_stack", "patches.txt")
    assert os.path.isfile(patches_path)
    with open(patches_path, "r", encoding="utf-8") as f:
        patches_content = f.read()

    assert "seed_roles" in patches_content
    assert "seed_service_types_and_sla_rules" in patches_content


def test_patches_are_idempotent_in_design():
    """Validates that seeding patch files check for existing records to prevent duplication."""
    patches_dir = os.path.join(PACKAGE_ROOT, "nilegov_stack", "patches")
    assert os.path.isdir(patches_dir)

    seed_roles_path = os.path.join(patches_dir, "seed_roles.py")
    assert os.path.isfile(seed_roles_path)
    with open(seed_roles_path, "r", encoding="utf-8") as f:
        roles_code = f.read()
    assert "frappe.db.exists" in roles_code, "seed_roles.py patch must verify record existence to be idempotent"

    seed_data_path = os.path.join(patches_dir, "seed_service_types_and_sla_rules.py")
    assert os.path.isfile(seed_data_path)
    with open(seed_data_path, "r", encoding="utf-8") as f:
        data_code = f.read()
    assert "frappe.db.exists" in data_code or "frappe.get_all" in data_code, (
        "seed_service_types_and_sla_rules.py patch must verify record existence to be idempotent"
    )

    # Verify no prohibited roles are seeded
    prohibited_roles = ["NIRA Officer", "URA Officer", "UGHub Officer"]
    for role in prohibited_roles:
        assert role not in roles_code, f"Roles patch must not seed forbidden role: {role}"
        assert role not in data_code, f"Data patch must not reference forbidden role: {role}"

    # Verify default service type code
    assert "LOST_NATIONAL_ID" in data_code, "Data patch must configure default service 'LOST_NATIONAL_ID'"


def test_static_import_permission_helper():
    """Statically imports the permission helper module and asserts hooks exist."""
    import sys
    from unittest.mock import MagicMock
    if "frappe" not in sys.modules:
        sys.modules["frappe"] = MagicMock()

    from nilegov_stack.interfaces import permissions
    assert hasattr(permissions, "has_permission"), "permissions.py must expose has_permission"
    assert hasattr(permissions, "get_permission_query_conditions"), "permissions.py must expose get_permission_query_conditions"


def test_static_import_patches():
    """Statically imports patch modules and asserts they expose execute()."""
    import sys
    from unittest.mock import MagicMock
    if "frappe" not in sys.modules:
        sys.modules["frappe"] = MagicMock()

    from nilegov_stack.patches import seed_roles, seed_service_types_and_sla_rules
    assert hasattr(seed_roles, "execute"), "seed_roles.py must expose execute()"
    assert hasattr(seed_service_types_and_sla_rules, "execute"), "seed_service_types_and_sla_rules.py must expose execute()"


def test_doctypes_json_readiness():
    """Performs validation checks on each DocType JSON schema to ensure Gunicorn runtime readiness."""
    reserved_names = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx", "parent", "parentfield", "parenttype"}

    for folder, doctype_name in EXPECTED_DOCTYPES.items():
        json_path = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data.get("name") == doctype_name
        assert data.get("module") == "NileGov Stack"
        assert data.get("istable", 0) == 0, f"DocType '{doctype_name}' should not be set as a child table (istable should be 0)"

        fields = data.get("fields")
        assert isinstance(fields, list), f"Fields list missing in '{doctype_name}'"

        for field in fields:
            assert "fieldname" in field, f"Missing fieldname in field config in '{doctype_name}'"
            assert "label" in field, f"Missing label for field '{field.get('fieldname')}' in '{doctype_name}'"
            assert "fieldtype" in field, f"Missing fieldtype for field '{field.get('fieldname')}' in '{doctype_name}'"

            fieldname = field["fieldname"]
            # Check collisions with reserved names
            assert fieldname not in reserved_names, f"Fieldname '{fieldname}' in '{doctype_name}' collides with Frappe reserved name"

            # Link check
            if field["fieldtype"] == "Link":
                assert field.get("options"), f"Link field '{fieldname}' in '{doctype_name}' must specify options"

            # Select options check
            if field["fieldtype"] == "Select":
                assert field.get("options"), f"Select field '{fieldname}' in '{doctype_name}' must specify options list"

        # Check permissions array
        perms = data.get("permissions")
        assert isinstance(perms, list) and len(perms) > 0, f"Permissions list missing in '{doctype_name}'"

        for perm in perms:
            role = perm.get("role")
            assert role, f"Permission entry in '{doctype_name}' missing role"
            # Ensure no guest or all-access defaults
            assert role != "Guest", f"Broad Guest access is forbidden in '{doctype_name}'"


def test_no_generator_residue_or_credentials():
    """Confirms no temporary scripts, credentials, or untracked active files are present."""
    # Ensure generator script is deleted
    generator_path = os.path.join(PACKAGE_ROOT, "generate_doctypes.py")
    assert not os.path.exists(generator_path), f"Residue generator script still exists at {generator_path}"

    # Ensure no .env file exists in the repository root
    repo_root = os.path.dirname(PACKAGE_ROOT)
    env_path = os.path.join(repo_root, ".env")
    assert not os.path.exists(env_path), "A live .env file was detected in the repository root. Remove it immediately."


def test_link_and_table_field_targets():
    """All Link and Table field targets must exist in repo or Frappe core."""
    frappe_core_allowlist = {
        "User", "Role", "DocType", "Workspace", "Dashboard", "Print Format", "Report"
    }
    for folder, doctype_name in EXPECTED_DOCTYPES.items():
        json_path = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for field in data.get("fields", []):
            if field.get("fieldtype") in ("Link", "Table"):
                target = field.get("options")
                assert target, f"Field '{field['fieldname']}' in '{doctype_name}' must declare options"
                if target.startswith("NileGov"):
                    assert target in EXPECTED_DOCTYPES.values(), (
                        f"Field '{field['fieldname']}' in '{doctype_name}' targets unknown DocType '{target}'"
                    )
                else:
                    assert target in frappe_core_allowlist, (
                        f"Field '{field['fieldname']}' in '{doctype_name}' targets unapproved core DocType '{target}'"
                    )

def test_safe_fieldnames():
    """All custom fieldnames must match safe fieldname pattern."""
    import re
    safe_pattern = re.compile(r"^[a-z0-9_]+$")
    for folder, doctype_name in EXPECTED_DOCTYPES.items():
        json_path = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for field in data.get("fields", []):
            fname = field.get("fieldname")
            assert safe_pattern.match(fname), f"Invalid fieldname '{fname}' in '{doctype_name}'"
