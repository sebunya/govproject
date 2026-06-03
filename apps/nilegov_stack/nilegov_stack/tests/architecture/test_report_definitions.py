# Pass 11B-5A: Report and Dashboard Definitions — Static Architecture Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live government statistics claimed.
#
# Static tests (no Frappe bench required) verifying:
#  1.  All 9 report JSON files exist
#  2.  All 9 report JSON files are valid JSON with required keys
#  3.  Every report has report_type = "Report Builder"
#  4.  Every report ref_doctype is a known NileGov DocType
#  5.  Every report roles list contains only canonical NileGov roles
#  6.  No report description claims official government statistics
#  7.  Reporting Snapshot Summary carries prototype disclaimer
#  8.  Payment Reconciliation does not claim live payment clearance
#  9.  All 9 number card JSON files exist and are valid
# 10.  All 8 dashboard chart JSON files exist and are valid
# 11.  Dashboard JSON exists and references all charts and number cards
# 12.  hooks.py fixtures include Report, Dashboard Chart, Number Card, Dashboard
# 13.  No report JSON contains external URLs
# 14.  All report JS companion files exist and contain onload disclaimer
# 15.  Payment report JS shows red alert (not orange — higher risk)

import json
import os
import re
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTER_PACKAGE = os.path.dirname(os.path.dirname(BASE_DIR))
INNER_APP = os.path.join(OUTER_PACKAGE, "nilegov_stack")
REPORT_ROOT = os.path.join(INNER_APP, "report")
CARD_ROOT = os.path.join(INNER_APP, "number_card")
CHART_ROOT = os.path.join(INNER_APP, "dashboard_chart")
DASHBOARD_ROOT = os.path.join(INNER_APP, "dashboard")
HOOKS_PATH = os.path.join(OUTER_PACKAGE, "hooks.py")

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

KNOWN_DOCTYPES = {
    "NileGov Service Request",
    "NileGov Citizen Profile",
    "NileGov Consent Record",
    "NileGov Evidence Document",
    "NileGov Payment Record",
    "NileGov Citizen Notification",
    "NileGov SLA Event",
    "NileGov SLA Rule",
    "NileGov Escalation Record",
    "NileGov Case Note",
    "NileGov Audit Event",
    "NileGov Integration Simulation Log",
    "NileGov Reporting Snapshot",
    "NileGov Simulated Identity Verification",
    "NileGov Service Type",
    "NileGov Service Catalogue",
}

REPORT_DEFINITIONS = {
    "nilegov_requests_by_status": {
        "name": "NileGov Requests by Status",
        "ref_doctype": "NileGov Service Request",
    },
    "nilegov_requests_by_service": {
        "name": "NileGov Requests by Service",
        "ref_doctype": "NileGov Service Request",
    },
    "nilegov_sla_compliance": {
        "name": "NileGov SLA Compliance",
        "ref_doctype": "NileGov SLA Event",
    },
    "nilegov_officer_workload": {
        "name": "NileGov Officer Workload",
        "ref_doctype": "NileGov Service Request",
    },
    "nilegov_evidence_completeness": {
        "name": "NileGov Evidence Completeness",
        "ref_doctype": "NileGov Evidence Document",
    },
    "nilegov_payment_reconciliation": {
        "name": "NileGov Payment Reconciliation",
        "ref_doctype": "NileGov Payment Record",
    },
    "nilegov_notification_delivery": {
        "name": "NileGov Notification Delivery",
        "ref_doctype": "NileGov Citizen Notification",
    },
    "nilegov_integration_simulation_report": {
        "name": "NileGov Integration Simulation Report",
        "ref_doctype": "NileGov Integration Simulation Log",
    },
    "nilegov_reporting_snapshot_summary": {
        "name": "NileGov Reporting Snapshot Summary",
        "ref_doctype": "NileGov Reporting Snapshot",
    },
}

NUMBER_CARDS = [
    "nilegov_total_requests",
    "nilegov_open_requests",
    "nilegov_overdue_sla_cases",
    "nilegov_escalated_cases",
    "nilegov_pending_payments",
    "nilegov_verified_payments",
    "nilegov_evidence_incomplete",
    "nilegov_simulated_notifications_sent",
    "nilegov_reporting_snapshots",
]

DASHBOARD_CHARTS = [
    "nilegov_requests_by_status_chart",
    "nilegov_requests_by_service_chart",
    "nilegov_sla_compliance_chart",
    "nilegov_payment_status_chart",
    "nilegov_evidence_verification_chart",
    "nilegov_notification_delivery_chart",
    "nilegov_officer_workload_chart",
    "nilegov_integration_simulation_chart",
]

FORBIDDEN_OFFICIAL_CLAIMS = [
    "official government statistics",
    "live government",
    "live nilegov",
    "production analytics",
    "official performance data",
    "live nira",
    "live ura",
]

EXTERNAL_URL_RE = re.compile(r'https?://(?!localhost|127\.0\.0\.1)', re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _load_report_json(folder):
    path = os.path.join(REPORT_ROOT, folder, f"{folder}.json")
    with open(path) as f:
        return json.load(f)


def _load_card_json(folder):
    path = os.path.join(CARD_ROOT, folder, f"{folder}.json")
    with open(path) as f:
        return json.load(f)


def _load_chart_json(folder):
    path = os.path.join(CHART_ROOT, folder, f"{folder}.json")
    with open(path) as f:
        return json.load(f)


def _report_js(folder):
    path = os.path.join(REPORT_ROOT, folder, f"{folder}.js")
    with open(path) as f:
        return f.read()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Report JSON files exist
# ─────────────────────────────────────────────────────────────────────────────
class TestReportFilesExist:
    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_report_json_exists(self, folder):
        path = os.path.join(REPORT_ROOT, folder, f"{folder}.json")
        assert os.path.isfile(path), f"Report JSON not found: {path}"

    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_report_js_exists(self, folder):
        path = os.path.join(REPORT_ROOT, folder, f"{folder}.js")
        assert os.path.isfile(path), f"Report JS companion not found: {path}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Report JSON is valid and has required keys
# ─────────────────────────────────────────────────────────────────────────────
class TestReportJSONValidity:
    REQUIRED_KEYS = {"report_name", "ref_doctype", "report_type", "module", "roles"}

    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_report_json_is_valid(self, folder):
        doc = _load_report_json(folder)
        assert isinstance(doc, dict), f"{folder}.json must be a JSON object"

    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_report_has_required_keys(self, folder):
        doc = _load_report_json(folder)
        for key in self.REQUIRED_KEYS:
            assert key in doc, f"{folder}.json missing required key: '{key}'"

    @pytest.mark.parametrize("folder,info", list(REPORT_DEFINITIONS.items()))
    def test_report_name_matches(self, folder, info):
        doc = _load_report_json(folder)
        assert doc["report_name"] == info["name"], (
            f"{folder}.json report_name mismatch. "
            f"Expected '{info['name']}', got '{doc['report_name']}'"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 3. report_type = "Report Builder"
# ─────────────────────────────────────────────────────────────────────────────
class TestReportType:
    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_report_type_is_report_builder(self, folder):
        doc = _load_report_json(folder)
        assert doc.get("report_type") == "Report Builder", (
            f"{folder}.json must have report_type='Report Builder'. "
            f"Got: '{doc.get('report_type')}'"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 4. ref_doctype is a known NileGov DocType
# ─────────────────────────────────────────────────────────────────────────────
class TestReportRefDoctype:
    @pytest.mark.parametrize("folder,info", list(REPORT_DEFINITIONS.items()))
    def test_ref_doctype_is_known(self, folder, info):
        doc = _load_report_json(folder)
        ref = doc.get("ref_doctype", "")
        assert ref == info["ref_doctype"], (
            f"{folder}.json ref_doctype mismatch. "
            f"Expected '{info['ref_doctype']}', got '{ref}'"
        )
        assert ref in KNOWN_DOCTYPES, (
            f"{folder}.json ref_doctype '{ref}' is not a known NileGov DocType."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Roles contain only canonical NileGov roles
# ─────────────────────────────────────────────────────────────────────────────
class TestReportRoles:
    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_roles_are_canonical(self, folder):
        doc = _load_report_json(folder)
        roles = {r.get("role") for r in doc.get("roles", [])}
        assert len(roles) > 0, f"{folder}.json must define at least one role."
        non_canonical = roles - CANONICAL_ROLES - {"System Manager"}
        assert not non_canonical, (
            f"{folder}.json contains non-canonical roles: {non_canonical}. "
            f"Allowed: {sorted(CANONICAL_ROLES)}"
        )

    def test_payment_report_roles_restricted(self):
        """Payment Reconciliation must NOT be visible to Citizen Officer or Records Officer."""
        doc = _load_report_json("nilegov_payment_reconciliation")
        roles = {r.get("role") for r in doc.get("roles", [])}
        assert "NileGov Citizen Officer" not in roles, (
            "Payment Reconciliation must not be accessible to NileGov Citizen Officer."
        )
        assert "NileGov Records Officer" not in roles, (
            "Payment Reconciliation must not be accessible to NileGov Records Officer."
        )

    def test_snapshot_report_roles_restricted(self):
        """Reporting Snapshot Summary should be restricted to M&E/Admin/Auditor roles."""
        doc = _load_report_json("nilegov_reporting_snapshot_summary")
        roles = {r.get("role") for r in doc.get("roles", [])}
        assert "NileGov Citizen Officer" not in roles, (
            "Reporting Snapshot Summary must not be accessible to NileGov Citizen Officer."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 6. No report description claims official government statistics
# ─────────────────────────────────────────────────────────────────────────────
class TestReportNoOfficialClaims:
    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_no_official_claims_in_description(self, folder):
        doc = _load_report_json(folder)
        desc = (doc.get("description") or "").lower()
        # Strip negating disclaimer phrases before checking for forbidden strings
        cleaned = desc
        cleaned = re.sub(r'\bnot official government statistics\b', '', cleaned)
        cleaned = re.sub(r'\bnot official\b', '', cleaned)
        cleaned = re.sub(r'\bnot live payment clearance\b', '', cleaned)
        cleaned = re.sub(r'\bnot live\b', '', cleaned)
        cleaned = re.sub(r'\bno live (nira|ura|ughub|payment|registry|pesapal)\b', '', cleaned)
        cleaned = re.sub(r'\bnot represent live (nilegov|nira|ura|ministry)\b', '', cleaned)
        cleaned = re.sub(r'\bdoes not represent live (nilegov|nira|ura|ministry)\b', '', cleaned)
        for claim in FORBIDDEN_OFFICIAL_CLAIMS:
            assert claim.lower() not in cleaned, (
                f"{folder}.json description contains forbidden claim: '{claim}'"
            )

    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_no_external_urls_in_json(self, folder):
        doc = _load_report_json(folder)
        raw = json.dumps(doc)
        matches = EXTERNAL_URL_RE.findall(raw)
        assert not matches, (
            f"{folder}.json contains external URL(s): {matches}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 7. Reporting Snapshot Summary carries prototype disclaimer
# ─────────────────────────────────────────────────────────────────────────────
class TestSnapshotReportDisclaimer:
    def test_snapshot_description_has_prototype_disclaimer(self):
        doc = _load_report_json("nilegov_reporting_snapshot_summary")
        desc = (doc.get("description") or "").lower()
        assert "prototype" in desc or "fictional" in desc, (
            "Reporting Snapshot Summary description must state 'prototype' or 'fictional'."
        )

    def test_snapshot_description_says_not_official(self):
        doc = _load_report_json("nilegov_reporting_snapshot_summary")
        desc = (doc.get("description") or "").lower()
        assert "not official government statistics" in desc, (
            "Reporting Snapshot Summary description must explicitly say "
            "'not official government statistics'."
        )

    def test_snapshot_js_shows_msgprint_not_just_alert(self):
        content = _report_js("nilegov_reporting_snapshot_summary")
        assert "frappe.msgprint" in content, (
            "Reporting Snapshot Summary JS must use frappe.msgprint (not just show_alert) "
            "due to the high risk of implying official statistics."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 8. Payment Reconciliation does not claim live payment clearance
# ─────────────────────────────────────────────────────────────────────────────
class TestPaymentReportSafety:
    PAYMENT_FORBIDDEN = [
        "live payment clearance",
        "real payment",
        "production payment",
        "real money",
    ]

    def test_payment_description_no_live_claim(self):
        doc = _load_report_json("nilegov_payment_reconciliation")
        desc = (doc.get("description") or "").lower()
        # Strip negating disclaimer phrases before checking
        cleaned = re.sub(r'\bnot live payment clearance\b', '', desc)
        cleaned = re.sub(r'\bnot live\b', '', cleaned)
        cleaned = re.sub(r'\bno real money moved\b', '', cleaned)
        for claim in self.PAYMENT_FORBIDDEN:
            assert claim not in cleaned, (
                f"Payment Reconciliation description contains forbidden claim: '{claim}'"
            )

    def test_payment_description_says_simulated(self):
        doc = _load_report_json("nilegov_payment_reconciliation")
        desc = (doc.get("description") or "").lower()
        assert "simulated" in desc or "sandbox" in desc, (
            "Payment Reconciliation description must clearly say 'simulated' or 'sandbox'."
        )

    def test_payment_js_uses_red_alert(self):
        content = _report_js("nilegov_payment_reconciliation")
        assert '"red"' in content or "'red'" in content, (
            "Payment Reconciliation JS must use a red indicator to signal sandbox-only context."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 9. Number card JSON files exist and are valid
# ─────────────────────────────────────────────────────────────────────────────
class TestNumberCardsExist:
    @pytest.mark.parametrize("folder", NUMBER_CARDS)
    def test_card_json_exists(self, folder):
        path = os.path.join(CARD_ROOT, folder, f"{folder}.json")
        assert os.path.isfile(path), f"Number card JSON not found: {path}"

    @pytest.mark.parametrize("folder", NUMBER_CARDS)
    def test_card_json_is_valid(self, folder):
        doc = _load_card_json(folder)
        assert isinstance(doc, dict), f"{folder}.json must be a JSON object"
        assert "document_type" in doc, f"{folder}.json missing 'document_type'"
        assert "function" in doc, f"{folder}.json missing 'function'"
        assert doc.get("function") == "Count", (
            f"{folder}.json function must be 'Count', got '{doc.get('function')}'"
        )

    @pytest.mark.parametrize("folder", NUMBER_CARDS)
    def test_card_doctype_is_known(self, folder):
        doc = _load_card_json(folder)
        dt = doc.get("document_type", "")
        assert dt in KNOWN_DOCTYPES, (
            f"{folder}.json document_type '{dt}' is not a known NileGov DocType."
        )

    def test_payment_cards_have_simulated_label(self):
        for folder in ["nilegov_pending_payments", "nilegov_verified_payments"]:
            doc = _load_card_json(folder)
            label = (doc.get("label") or "").lower()
            assert "simulated" in label, (
                f"{folder}.json label must include 'Simulated' to clarify sandbox context."
            )

    def test_snapshot_card_has_prototype_label(self):
        doc = _load_card_json("nilegov_reporting_snapshots")
        label = (doc.get("label") or "").lower()
        assert "prototype" in label, (
            "nilegov_reporting_snapshots.json label must include 'Prototype'."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 10. Dashboard chart JSON files exist and are valid
# ─────────────────────────────────────────────────────────────────────────────
class TestDashboardChartsExist:
    @pytest.mark.parametrize("folder", DASHBOARD_CHARTS)
    def test_chart_json_exists(self, folder):
        path = os.path.join(CHART_ROOT, folder, f"{folder}.json")
        assert os.path.isfile(path), f"Dashboard chart JSON not found: {path}"

    @pytest.mark.parametrize("folder", DASHBOARD_CHARTS)
    def test_chart_json_is_valid(self, folder):
        doc = _load_chart_json(folder)
        assert isinstance(doc, dict), f"{folder}.json must be a JSON object"
        assert "document_type" in doc, f"{folder}.json missing 'document_type'"
        assert "chart_type" in doc, f"{folder}.json missing 'chart_type'"

    @pytest.mark.parametrize("folder", DASHBOARD_CHARTS)
    def test_chart_doctype_is_known(self, folder):
        doc = _load_chart_json(folder)
        dt = doc.get("document_type", "")
        assert dt in KNOWN_DOCTYPES, (
            f"{folder}.json document_type '{dt}' is not a known NileGov DocType."
        )

    @pytest.mark.parametrize("folder", DASHBOARD_CHARTS)
    def test_chart_label_contains_prototype(self, folder):
        doc = _load_chart_json(folder)
        label = (doc.get("label") or "").lower()
        assert "prototype" in label or "simulated" in label or "demo" in label, (
            f"{folder}.json label must contain 'Prototype', 'Simulated' or 'Demo' "
            f"to clarify non-production context."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 11. Dashboard JSON exists and references all charts and number cards
# ─────────────────────────────────────────────────────────────────────────────
class TestDashboardDefinition:
    DASHBOARD_FOLDER = "nilegov_case_operations_dashboard"
    DASHBOARD_FILE = "nilegov_case_operations_dashboard.json"

    def _load(self):
        path = os.path.join(DASHBOARD_ROOT, self.DASHBOARD_FOLDER, self.DASHBOARD_FILE)
        with open(path) as f:
            return json.load(f)

    def test_dashboard_json_exists(self):
        path = os.path.join(DASHBOARD_ROOT, self.DASHBOARD_FOLDER, self.DASHBOARD_FILE)
        assert os.path.isfile(path), f"Dashboard JSON not found: {path}"

    def test_dashboard_has_required_keys(self):
        doc = self._load()
        for key in ("dashboard_name", "charts", "cards"):
            assert key in doc, f"Dashboard JSON missing key: '{key}'"

    def test_dashboard_references_all_8_charts(self):
        doc = self._load()
        chart_names = {c["chart"] for c in doc.get("charts", [])}
        expected = {
            "NileGov Requests by Status Chart",
            "NileGov Requests by Service Chart",
            "NileGov SLA Compliance Chart",
            "NileGov Payment Status Chart",
            "NileGov Evidence Verification Chart",
            "NileGov Notification Delivery Chart",
            "NileGov Officer Workload Chart",
            "NileGov Integration Simulation Chart",
        }
        assert chart_names == expected, (
            f"Dashboard chart references mismatch.\n"
            f"Expected: {sorted(expected)}\n"
            f"Got:      {sorted(chart_names)}"
        )

    def test_dashboard_references_all_9_cards(self):
        doc = self._load()
        card_names = {c["card"] for c in doc.get("cards", [])}
        expected = {
            "NileGov Total Requests",
            "NileGov Open Requests",
            "NileGov Overdue SLA Cases",
            "NileGov Escalated Cases",
            "NileGov Pending Payments",
            "NileGov Verified Payments",
            "NileGov Evidence Incomplete",
            "NileGov Simulated Notifications Sent",
            "NileGov Reporting Snapshots",
        }
        assert card_names == expected, (
            f"Dashboard number card references mismatch.\n"
            f"Expected: {sorted(expected)}\n"
            f"Got:      {sorted(card_names)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 12. hooks.py fixtures include all 5 fixture types
# ─────────────────────────────────────────────────────────────────────────────
class TestHooksFixtures:
    def _hooks(self):
        with open(HOOKS_PATH) as f:
            return f.read()

    def test_hooks_includes_report_fixture(self):
        content = self._hooks()
        assert '"dt": "Report"' in content or "'dt': 'Report'" in content, (
            "hooks.py fixtures must include {\"dt\": \"Report\", ...} for report loading."
        )

    def test_hooks_includes_number_card_fixture(self):
        content = self._hooks()
        assert '"dt": "Number Card"' in content or "'dt': 'Number Card'" in content, (
            "hooks.py fixtures must include {\"dt\": \"Number Card\", ...}."
        )

    def test_hooks_includes_dashboard_chart_fixture(self):
        content = self._hooks()
        assert '"dt": "Dashboard Chart"' in content or "'dt': 'Dashboard Chart'" in content, (
            "hooks.py fixtures must include {\"dt\": \"Dashboard Chart\", ...}."
        )

    def test_hooks_includes_dashboard_fixture(self):
        content = self._hooks()
        assert '"dt": "Dashboard"' in content or "'dt': 'Dashboard'" in content, (
            "hooks.py fixtures must include {\"dt\": \"Dashboard\", ...}."
        )

    def test_hooks_lists_all_9_reports(self):
        content = self._hooks()
        for name in [
            "NileGov Requests by Status",
            "NileGov Requests by Service",
            "NileGov SLA Compliance",
            "NileGov Officer Workload",
            "NileGov Evidence Completeness",
            "NileGov Payment Reconciliation",
            "NileGov Notification Delivery",
            "NileGov Integration Simulation Report",
            "NileGov Reporting Snapshot Summary",
        ]:
            assert name in content, (
                f"hooks.py fixtures does not include report: '{name}'"
            )

    def test_hooks_lists_all_9_number_cards(self):
        content = self._hooks()
        for name in [
            "NileGov Total Requests",
            "NileGov Open Requests",
            "NileGov Overdue SLA Cases",
            "NileGov Escalated Cases",
            "NileGov Pending Payments",
            "NileGov Verified Payments",
            "NileGov Evidence Incomplete",
            "NileGov Simulated Notifications Sent",
            "NileGov Reporting Snapshots",
        ]:
            assert name in content, (
                f"hooks.py fixtures does not include number card: '{name}'"
            )

    def test_hooks_lists_the_dashboard(self):
        content = self._hooks()
        assert "NileGov Case Operations Dashboard" in content, (
            "hooks.py fixtures must include 'NileGov Case Operations Dashboard'."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 13 & 14. No external URLs in report JSON; JS companion has onload disclaimer
# ─────────────────────────────────────────────────────────────────────────────
class TestReportJSSafety:
    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_js_has_onload_with_disclaimer(self, folder):
        content = _report_js(folder)
        assert "onload" in content, (
            f"{folder}.js must have an onload handler for prototype disclaimer."
        )
        lower = content.lower()
        has_disclaimer = (
            "prototype" in lower or "simulated" in lower
            or "not official" in lower or "demo data" in lower
            or "fictional" in lower or "sandbox" in lower
        )
        assert has_disclaimer, (
            f"{folder}.js onload must include a prototype/simulated/disclaimer message."
        )

    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_js_has_no_external_urls(self, folder):
        content = _report_js(folder)
        matches = EXTERNAL_URL_RE.findall(content)
        assert not matches, (
            f"{folder}.js contains external URLs: {matches}"
        )

    @pytest.mark.parametrize("folder", list(REPORT_DEFINITIONS.keys()))
    def test_js_has_no_frappe_call(self, folder):
        content = _report_js(folder)
        assert "frappe.call" not in content, (
            f"{folder}.js must not use frappe.call — Report Builder reports are read-only."
        )
