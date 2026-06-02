# Pass 11B-5B: NileGov Workspace Reporting Shortcuts and Verification Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live government statistics claimed.
#

import json
import os
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
WS_PATH = os.path.join(
    PACKAGE_ROOT, "nilegov_stack", "nilegov_stack",
    "workspace", "nilegov_case_operations", "nilegov_case_operations.json"
)
REPORT_ROOT = os.path.join(PACKAGE_ROOT, "nilegov_stack", "nilegov_stack", "report")
DASHBOARD_ROOT = os.path.join(PACKAGE_ROOT, "nilegov_stack", "nilegov_stack", "dashboard")

# Expected dashboard & reports
EXPECTED_DASHBOARD = "NileGov Case Operations Dashboard"
EXPECTED_REPORTS = {
    "NileGov Requests by Status",
    "NileGov Requests by Service",
    "NileGov SLA Compliance",
    "NileGov Officer Workload",
    "NileGov Evidence Completeness",
    "NileGov Payment Reconciliation",
    "NileGov Notification Delivery",
    "NileGov Integration Simulation Report",
    "NileGov Reporting Snapshot Summary",
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _load_ws():
    with open(WS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestWorkspaceReportingLinks:
    def test_workspace_file_exists(self):
        assert os.path.isfile(WS_PATH), f"Workspace JSON not found: {WS_PATH}"

    def test_workspace_has_dashboard_link(self):
        data = _load_ws()
        links = data.get("links", [])
        dashboard_links = [
            lnk for lnk in links
            if lnk.get("link_to") == EXPECTED_DASHBOARD and lnk.get("link_type") == "Dashboard"
        ]
        assert len(dashboard_links) >= 1, f"Workspace must link to dashboard '{EXPECTED_DASHBOARD}'"
        
        # Verify dashboard link label has prototype wording
        label = dashboard_links[0].get("label", "").lower()
        assert "prototype" in label or "simulated" in label or "demo" in label, (
            f"Dashboard link label '{dashboard_links[0].get('label')}' must contain 'Prototype', 'Simulated', or 'Demo'."
        )

    def test_workspace_has_all_9_reports(self):
        data = _load_ws()
        links = data.get("links", [])
        shortcuts = data.get("shortcuts", [])
        
        referenced_reports = set()
        for lnk in links:
            if lnk.get("link_type") == "Report":
                referenced_reports.add(lnk.get("link_to"))
        for sh in shortcuts:
            if sh.get("type") == "Report":
                referenced_reports.add(sh.get("link_to"))
                
        missing = EXPECTED_REPORTS - referenced_reports
        assert not missing, f"Workspace missing shortcuts/links for reports: {missing}"

    def test_reports_point_to_existing_report_definitions(self):
        data = _load_ws()
        links = data.get("links", [])
        
        # Collect report link_to values
        report_names = [
            lnk.get("link_to") for lnk in links
            if lnk.get("link_type") == "Report"
        ]
        
        # For each report linked, verify there's a matching folder with a valid JSON report name
        for name in report_names:
            found = False
            for folder in os.listdir(REPORT_ROOT):
                folder_path = os.path.join(REPORT_ROOT, folder)
                if not os.path.isdir(folder_path):
                    continue
                json_path = os.path.join(folder_path, f"{folder}.json")
                if os.path.isfile(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        rep_data = json.load(f)
                        if rep_data.get("report_name") == name:
                            found = True
                            break
            assert found, f"Linked report '{name}' does not point to an existing report definition JSON in {REPORT_ROOT}"

    def test_dashboard_points_to_existing_dashboard_definition(self):
        data = _load_ws()
        links = data.get("links", [])
        
        dashboard_names = [
            lnk.get("link_to") for lnk in links
            if lnk.get("link_type") == "Dashboard"
        ]
        
        for name in dashboard_names:
            found = False
            for folder in os.listdir(DASHBOARD_ROOT):
                folder_path = os.path.join(DASHBOARD_ROOT, folder)
                if not os.path.isdir(folder_path):
                    continue
                json_path = os.path.join(folder_path, f"{folder}.json")
                if os.path.isfile(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        dash_data = json.load(f)
                        if dash_data.get("dashboard_name") == name:
                            found = True
                            break
            assert found, f"Linked dashboard '{name}' does not point to an existing dashboard definition JSON in {DASHBOARD_ROOT}"

    def test_payment_report_label_safety(self):
        data = _load_ws()
        links = data.get("links", [])
        
        payment_link = [
            lnk for lnk in links
            if lnk.get("link_to") == "NileGov Payment Reconciliation"
        ]
        assert payment_link, "Payment Reconciliation report link missing from workspace"
        label = payment_link[0].get("label", "").lower()
        
        # Verify payment reconciliation label contains simulated or sandbox
        assert "simulated" in label or "sandbox" in label, (
            f"Payment Reconciliation label '{payment_link[0].get('label')}' must contain 'simulated' or 'sandbox' to avoid live payment claims."
        )
        assert "live" not in label, "Payment Reconciliation label must not use 'live' payment claims"

    def test_reporting_snapshot_label_safety(self):
        data = _load_ws()
        links = data.get("links", [])
        
        snapshot_link = [
            lnk for lnk in links
            if lnk.get("link_to") == "NileGov Reporting Snapshot Summary"
        ]
        assert snapshot_link, "Reporting Snapshot Summary report link missing from workspace"
        label = snapshot_link[0].get("label", "").lower()
        
        # Verify reporting snapshot summary label does not claim official statistics and includes prototype/demo/simulated
        assert "official government statistics" not in label, "Reporting Snapshot label must not claim official government statistics"
        assert "official statistics" not in label, "Reporting Snapshot label must not claim official statistics"
        assert "prototype" in label or "demo" in label or "simulated" in label, (
            f"Reporting Snapshot label '{snapshot_link[0].get('label')}' must contain 'prototype', 'demo', or 'simulated'."
        )

    def test_integration_simulation_label_safety(self):
        data = _load_ws()
        links = data.get("links", [])
        
        integration_link = [
            lnk for lnk in links
            if lnk.get("link_to") == "NileGov Integration Simulation Report"
        ]
        assert integration_link, "Integration Simulation report link missing from workspace"
        label = integration_link[0].get("label", "").lower()
        
        # Verify integration report label clearly uses simulation wording
        assert "simulation" in label, (
            f"Integration report label '{integration_link[0].get('label')}' must clearly contain 'simulation' wording."
        )
