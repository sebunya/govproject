# Pass 11B-3: NileGov Workspace Navigation and Search Fields Tests
# Digi-Verse Uganda Limited
# Prototype — no live government data.
#
# Tests:
#  1.  Workspace JSON file exists
#  2.  Workspace links all 16 NileGov DocTypes
#  3.  Workspace shortcuts cover all 16 DocTypes
#  4.  Workspace has shortcut for Reporting Snapshot
#  5.  Workspace has shortcut/link for Audit Event
#  6.  Workspace has shortcut/link for Integration Simulation Log
#  7.  All shortcut link_to values match known DocType names (no broken links)
#  8.  All link link_to values match known DocType names
#  9.  No workspace label claims live integration
# 10.  Workspace has 8 canonical NileGov role access entries
# 11.  Workspace has 8 section labels (A–H) via Card Break type
# 12.  Key DocTypes have search_fields
# 13.  Search fields reference only existing field names in each DocType
# 14.  Key DocTypes have in_list_view fields
# 15.  in_standard_filter fields reference existing fields
# 16.  title_field is set and refers to an existing field
# 17.  sort_field is set and refers to an existing field
# 18.  DocType JSONs remain valid after search/list changes

import json
import os
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
DOCTYPE_ROOT = os.path.join(PACKAGE_ROOT, "nilegov_stack", "nilegov_stack", "doctype")
WS_PATH = os.path.join(
    PACKAGE_ROOT, "nilegov_stack", "nilegov_stack",
    "workspace", "nilegov_case_operations", "nilegov_case_operations.json"
)

ALL_NILEGOV_DOCTYPES = {
    "NileGov Audit Event",
    "NileGov Case Note",
    "NileGov Citizen Notification",
    "NileGov Citizen Profile",
    "NileGov Consent Record",
    "NileGov Escalation Record",
    "NileGov Evidence Document",
    "NileGov Integration Simulation Log",
    "NileGov Payment Record",
    "NileGov Reporting Snapshot",
    "NileGov Service Catalogue",
    "NileGov Service Request",
    "NileGov Service Type",
    "NileGov Simulated Identity Verification",
    "NileGov SLA Event",
    "NileGov SLA Rule",
}

CANONICAL_ROLES = {
    "NileGov Citizen Officer",
    "NileGov Records Officer",
    "NileGov Payments Officer",
    "NileGov SLA Supervisor",
    "NileGov M&E Viewer",
    "NileGov MDA Admin",
    "NileGov System Auditor",
    "NileGov System Manager",
}

# Forbidden substrings in workspace labels/link_to (live claims)
FORBIDDEN_LABEL_KEYWORDS = [
    "live nira",
    "live ura",
    "live ughub",
    "production payment",
    "official government statistics produced",
    "active ministry system",
]

# DocTypes that require search_fields in this pass
REQUIRE_SEARCH_FIELDS = {
    "nilegov_service_request",
    "nilegov_citizen_profile",
    "nilegov_evidence_document",
    "nilegov_payment_record",
    "nilegov_case_note",
    "nilegov_citizen_notification",
    "nilegov_sla_event",
    "nilegov_escalation_record",
    "nilegov_service_catalogue",
    "nilegov_reporting_snapshot",
    "nilegov_integration_simulation_log",
    "nilegov_audit_event",
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _load_ws():
    with open(WS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_dt(folder):
    jp = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.json")
    with open(jp, "r", encoding="utf-8") as f:
        return json.load(f)


def _field_names(dt_data):
    return {fld["fieldname"] for fld in dt_data.get("fields", []) if "fieldname" in fld}


# ─────────────────────────────────────────────────────────────────────────────
# 1. Workspace file exists
# ─────────────────────────────────────────────────────────────────────────────
class TestWorkspaceFileExists:
    def test_workspace_json_exists(self):
        assert os.path.isfile(WS_PATH), f"Workspace JSON not found: {WS_PATH}"

    def test_workspace_json_is_valid(self):
        data = _load_ws()
        assert data.get("doctype") == "Workspace"
        assert data.get("name") == "NileGov Case Operations"


# ─────────────────────────────────────────────────────────────────────────────
# 2–3. Links and shortcuts cover all 16 DocTypes
# ─────────────────────────────────────────────────────────────────────────────
class TestWorkspaceCoversAllDocTypes:
    def _all_referenced_doctypes(self):
        data = _load_ws()
        refs = set()
        for lnk in data.get("links", []):
            lt = lnk.get("link_to", "")
            if lt:
                refs.add(lt)
        for sh in data.get("shortcuts", []):
            lt = sh.get("link_to", "")
            if lt:
                refs.add(lt)
        return refs

    def test_workspace_links_cover_all_16_doctypes(self):
        refs = self._all_referenced_doctypes()
        missing = ALL_NILEGOV_DOCTYPES - refs
        assert not missing, (
            f"Workspace does not reference these DocTypes via links/shortcuts: {sorted(missing)}"
        )

    def test_workspace_has_service_request(self):
        refs = self._all_referenced_doctypes()
        assert "NileGov Service Request" in refs

    def test_workspace_has_citizen_profile(self):
        refs = self._all_referenced_doctypes()
        assert "NileGov Citizen Profile" in refs

    def test_workspace_has_evidence_document(self):
        refs = self._all_referenced_doctypes()
        assert "NileGov Evidence Document" in refs

    def test_workspace_has_payment_record(self):
        refs = self._all_referenced_doctypes()
        assert "NileGov Payment Record" in refs

    def test_workspace_has_reporting_snapshot(self):
        refs = self._all_referenced_doctypes()
        assert "NileGov Reporting Snapshot" in refs, (
            "Workspace must include NileGov Reporting Snapshot (Pass 11B-1 deliverable)."
        )

    def test_workspace_has_audit_event(self):
        refs = self._all_referenced_doctypes()
        assert "NileGov Audit Event" in refs, (
            "Workspace must include NileGov Audit Event for System Auditor navigation."
        )

    def test_workspace_has_integration_simulation_log(self):
        refs = self._all_referenced_doctypes()
        assert "NileGov Integration Simulation Log" in refs

    def test_workspace_has_sla_rule(self):
        refs = self._all_referenced_doctypes()
        assert "NileGov SLA Rule" in refs

    def test_workspace_has_escalation_record(self):
        refs = self._all_referenced_doctypes()
        assert "NileGov Escalation Record" in refs


# ─────────────────────────────────────────────────────────────────────────────
# 4. No broken DocType names
# ─────────────────────────────────────────────────────────────────────────────
class TestWorkspaceNoUnknownDocTypes:
    def test_all_link_to_values_are_known_doctypes(self):
        data = _load_ws()
        for lnk in data.get("links", []):
            lt = lnk.get("link_to", "")
            if lt:
                assert lt in ALL_NILEGOV_DOCTYPES, (
                    f"Workspace link references unknown DocType: '{lt}'"
                )

    def test_all_shortcut_link_to_values_are_known_doctypes(self):
        data = _load_ws()
        for sh in data.get("shortcuts", []):
            lt = sh.get("link_to", "")
            if lt:
                assert lt in ALL_NILEGOV_DOCTYPES, (
                    f"Workspace shortcut references unknown DocType: '{lt}'"
                )


# ─────────────────────────────────────────────────────────────────────────────
# 5. No live integration labels
# ─────────────────────────────────────────────────────────────────────────────
class TestWorkspaceNoLiveLabels:
    def test_no_live_claims_in_labels(self):
        data = _load_ws()
        all_labels = []
        for lnk in data.get("links", []):
            all_labels.append(lnk.get("label", ""))
        for sh in data.get("shortcuts", []):
            all_labels.append(sh.get("label", ""))
        for label in all_labels:
            for kw in FORBIDDEN_LABEL_KEYWORDS:
                assert kw.lower() not in label.lower(), (
                    f"Workspace label '{label}' contains forbidden claim: '{kw}'"
                )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Role access
# ─────────────────────────────────────────────────────────────────────────────
class TestWorkspaceRoleAccess:
    def test_workspace_has_all_canonical_nilegov_roles(self):
        data = _load_ws()
        ws_roles = {r["role"] for r in data.get("roles", [])}
        missing = CANONICAL_ROLES - ws_roles
        assert not missing, (
            f"Workspace missing canonical NileGov roles: {sorted(missing)}"
        )

    def test_workspace_has_system_manager_fallback(self):
        data = _load_ws()
        ws_roles = {r["role"] for r in data.get("roles", [])}
        assert "System Manager" in ws_roles


# ─────────────────────────────────────────────────────────────────────────────
# 7. Section labels (A–H card breaks)
# ─────────────────────────────────────────────────────────────────────────────
class TestWorkspaceSectionLabels:
    EXPECTED_SECTIONS = {
        "A. Frontline Case Operations",
        "B. Evidence and Records",
        "C. Payments and Receipts",
        "D. SLA and Escalations",
        "E. Service Configuration",
        "F. Communications",
        "G. M&E and Reporting",
        "H. Audit and Interoperability",
    }

    def test_workspace_has_all_section_labels(self):
        data = _load_ws()
        section_labels = {
            lnk["label"]
            for lnk in data.get("links", [])
            if lnk.get("type") == "Card Break"
        }
        missing = self.EXPECTED_SECTIONS - section_labels
        assert not missing, (
            f"Workspace missing section labels: {sorted(missing)}"
        )

    def test_workspace_has_8_sections(self):
        data = _load_ws()
        card_breaks = [
            lnk for lnk in data.get("links", [])
            if lnk.get("type") == "Card Break"
        ]
        assert len(card_breaks) == 8, (
            f"Expected 8 Card Break sections, got {len(card_breaks)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 8. Shortcut count
# ─────────────────────────────────────────────────────────────────────────────
class TestWorkspaceShortcuts:
    def test_workspace_has_at_least_16_shortcuts(self):
        """One shortcut per DocType minimum."""
        data = _load_ws()
        assert len(data.get("shortcuts", [])) >= 16, (
            f"Expected at least 16 shortcuts (one per DocType), "
            f"got {len(data.get('shortcuts', []))}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 9. Search fields — presence
# ─────────────────────────────────────────────────────────────────────────────
class TestDoctypeSearchFields:
    @pytest.mark.parametrize("folder", sorted(REQUIRE_SEARCH_FIELDS))
    def test_has_search_fields(self, folder):
        data = _load_dt(folder)
        sf = data.get("search_fields", "")
        assert sf, (
            f"DocType '{folder}' must have search_fields set (Pass 11B-3 requirement)."
        )

    @pytest.mark.parametrize("folder", sorted(REQUIRE_SEARCH_FIELDS))
    def test_search_fields_reference_existing_fieldnames(self, folder):
        data = _load_dt(folder)
        sf = data.get("search_fields", "")
        if not sf:
            return
        existing = _field_names(data)
        bad = [s.strip() for s in sf.split(",") if s.strip() and s.strip() not in existing]
        assert not bad, (
            f"DocType '{folder}' search_fields references non-existent fields: {bad}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 10. title_field
# ─────────────────────────────────────────────────────────────────────────────
class TestDoctypeTitleField:
    @pytest.mark.parametrize("folder", sorted(REQUIRE_SEARCH_FIELDS))
    def test_title_field_is_set(self, folder):
        data = _load_dt(folder)
        tf = data.get("title_field", "")
        assert tf, f"DocType '{folder}' should have title_field set."

    @pytest.mark.parametrize("folder", sorted(REQUIRE_SEARCH_FIELDS))
    def test_title_field_references_existing_field(self, folder):
        data = _load_dt(folder)
        tf = data.get("title_field", "")
        if not tf:
            return
        existing = _field_names(data)
        assert tf in existing, (
            f"DocType '{folder}' title_field '{tf}' does not exist in fields."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 11. sort_field
# ─────────────────────────────────────────────────────────────────────────────
class TestDoctypeSortField:
    @pytest.mark.parametrize("folder", sorted(REQUIRE_SEARCH_FIELDS))
    def test_sort_field_references_existing_or_system_field(self, folder):
        data = _load_dt(folder)
        sf = data.get("sort_field", "")
        if not sf:
            return
        existing = _field_names(data)
        # System fields (Frappe default columns)
        system_fields = {"modified", "creation", "name", "owner", "modified_by"}
        assert sf in existing or sf in system_fields, (
            f"DocType '{folder}' sort_field '{sf}' not in declared fields or system fields."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 12. in_list_view fields
# ─────────────────────────────────────────────────────────────────────────────
class TestDoctypeListView:
    @pytest.mark.parametrize("folder", sorted(REQUIRE_SEARCH_FIELDS))
    def test_has_in_list_view_fields(self, folder):
        data = _load_dt(folder)
        lv = [
            fld["fieldname"]
            for fld in data.get("fields", [])
            if fld.get("in_list_view", 0) == 1
        ]
        assert len(lv) >= 1, (
            f"DocType '{folder}' should have at least one in_list_view field."
        )

    @pytest.mark.parametrize("folder", sorted(REQUIRE_SEARCH_FIELDS))
    def test_has_at_least_3_list_view_fields(self, folder):
        data = _load_dt(folder)
        lv = [
            fld["fieldname"]
            for fld in data.get("fields", [])
            if fld.get("in_list_view", 0) == 1
        ]
        assert len(lv) >= 3, (
            f"DocType '{folder}' should have at least 3 in_list_view fields for useful list display."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 13. in_standard_filter fields
# ─────────────────────────────────────────────────────────────────────────────
class TestDoctypeStandardFilters:
    @pytest.mark.parametrize("folder", sorted(REQUIRE_SEARCH_FIELDS))
    def test_has_in_standard_filter_fields(self, folder):
        data = _load_dt(folder)
        sf_fields = [
            fld["fieldname"]
            for fld in data.get("fields", [])
            if fld.get("in_standard_filter", 0) == 1
        ]
        assert len(sf_fields) >= 1, (
            f"DocType '{folder}' should have at least one in_standard_filter field."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 14. DocType JSON still valid after search/list changes
# ─────────────────────────────────────────────────────────────────────────────
class TestDoctypeJSONStillValid:
    ALL_FOLDERS = [
        "nilegov_audit_event", "nilegov_case_note", "nilegov_citizen_notification",
        "nilegov_citizen_profile", "nilegov_consent_record", "nilegov_escalation_record",
        "nilegov_evidence_document", "nilegov_integration_simulation_log",
        "nilegov_payment_record", "nilegov_reporting_snapshot",
        "nilegov_service_catalogue", "nilegov_service_request",
        "nilegov_service_type", "nilegov_simulated_identity_verification",
        "nilegov_sla_event", "nilegov_sla_rule",
    ]

    @pytest.mark.parametrize("folder", ALL_FOLDERS)
    def test_doctype_json_parseable(self, folder):
        jp = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.json")
        with open(jp, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        assert data.get("doctype") == "DocType"
        assert data.get("name", "").startswith("NileGov")

    @pytest.mark.parametrize("folder", ALL_FOLDERS)
    def test_doctype_still_has_permissions(self, folder):
        data = _load_dt(folder)
        perms = data.get("permissions", [])
        assert len(perms) >= 1, (
            f"DocType '{folder}' lost all permission rows — check for JSON corruption."
        )
        nilegov_roles = [p["role"] for p in perms if p.get("role", "").startswith("NileGov")]
        assert len(nilegov_roles) >= 1, (
            f"DocType '{folder}' must retain at least one NileGov-prefixed role after 11B-3 edits."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 15. Service Request — spot check specific required search fields
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestSearch:
    def test_service_request_has_citizen_name_in_search(self):
        data = _load_dt("nilegov_service_request")
        sf = data.get("search_fields", "")
        assert "citizen_full_name" in sf

    def test_service_request_has_status_in_list_view(self):
        data = _load_dt("nilegov_service_request")
        lv = {fld["fieldname"] for fld in data.get("fields", [])
              if fld.get("in_list_view", 0) == 1}
        assert "internal_status" in lv

    def test_service_request_has_sla_state_in_list_view(self):
        data = _load_dt("nilegov_service_request")
        lv = {fld["fieldname"] for fld in data.get("fields", [])
              if fld.get("in_list_view", 0) == 1}
        assert "sla_state" in lv


# ─────────────────────────────────────────────────────────────────────────────
# 16. Reporting Snapshot — spot check
# ─────────────────────────────────────────────────────────────────────────────
class TestReportingSnapshotSearch:
    def test_reporting_snapshot_has_snapshot_name_as_title(self):
        data = _load_dt("nilegov_reporting_snapshot")
        assert data.get("title_field") == "snapshot_name"

    def test_reporting_snapshot_has_generated_at_in_list_view(self):
        data = _load_dt("nilegov_reporting_snapshot")
        lv = {fld["fieldname"] for fld in data.get("fields", [])
              if fld.get("in_list_view", 0) == 1}
        assert "generated_at" in lv


# ─────────────────────────────────────────────────────────────────────────────
# 17. Audit Event — spot check for auditor-facing search
# ─────────────────────────────────────────────────────────────────────────────
class TestAuditEventSearch:
    def test_audit_event_has_actor_in_search_fields(self):
        data = _load_dt("nilegov_audit_event")
        sf = data.get("search_fields", "")
        assert "actor" in sf

    def test_audit_event_has_event_time_sort_field(self):
        data = _load_dt("nilegov_audit_event")
        assert data.get("sort_field") == "event_time"
        assert data.get("sort_order") == "DESC"
