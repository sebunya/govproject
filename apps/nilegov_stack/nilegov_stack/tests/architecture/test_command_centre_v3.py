"""
Layer 6 architecture tests for NileGov Command Centre V2.

Verifies:
- Build marker is layer6
- get_service_delivery_analytics is called
- get_sla_risk_analytics is called
- get_command_centre_filters is still called
- get_command_centre_overview is still called
- Forbidden analytics methods are absent
- No Frappe Charts initialization
- No global Promise.all blocker
- page.main is used, page.body is not
- Plain text title
- Service delivery empty-state handling present
- Service delivery error element present
- SLA/Risk empty-state handling present
- SLA/Risk error element present
- Fallback options for All Services, All Statuses, All Locations
- Workspace still links to nilegov-command-centre-v3 and not the old route
"""
import json
import os
import subprocess
import unittest


class TestCommandCentreV3Layer6(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        cls.page_dir = os.path.join(cls.base_path, "nilegov_stack", "nilegov_stack", "page", "nilegov_command_centre_v3")
        cls.js_path = os.path.join(cls.page_dir, "nilegov_command_centre_v3.js")
        cls.workspace_json = os.path.join(cls.base_path, "nilegov_stack", "nilegov_stack", "workspace", "nilegov_insights_reporting", "nilegov_insights_reporting.json")

        with open(cls.js_path, "r") as f:
            cls.js = f.read()
        with open(cls.workspace_json, "r") as f:
            cls.workspace = json.load(f)

    # ── Build marker ──────────────────────────────────────────────────────────

    def test_layer7_build_marker(self):
        self.assertIn("recovery-2026-06-10-v3-layer7-filterfix-r1", self.js,
                      "V2 JS must contain layer7 build marker")

    # ── Required API calls ────────────────────────────────────────────────────

    def test_calls_get_command_centre_filters(self):
        self.assertIn("get_command_centre_filters", self.js,
                      "V2 JS must still call get_command_centre_filters")

    def test_calls_get_command_centre_overview(self):
        self.assertIn("get_command_centre_overview", self.js,
                      "V2 JS must still call get_command_centre_overview")

    def test_calls_get_service_delivery_analytics(self):
        self.assertIn("get_service_delivery_analytics", self.js,
                      "V2 JS must call get_service_delivery_analytics")

    def test_calls_get_sla_risk_analytics(self):
        self.assertIn("get_sla_risk_analytics", self.js,
                      "Layer 6 must call get_sla_risk_analytics")

    def test_calls_get_payment_reconciliation_analytics(self):
        self.assertIn("get_payment_reconciliation_analytics", self.js,
                      "Layer 6 must call get_payment_reconciliation_analytics")

    def test_calls_get_officer_workload_analytics(self):
        self.assertIn("get_officer_workload_analytics", self.js,
                      "Layer 7 must call get_officer_workload_analytics")

    # ── Forbidden analytics calls ─────────────────────────────────────────────

    def test_no_location_performance_analytics(self):
        self.assertNotIn("get_location_performance_analytics", self.js)

    def test_no_policy_me_summary(self):
        self.assertNotIn("get_policy_me_summary", self.js)

    # ── Chart and async safety ────────────────────────────────────────────────

    def test_no_frappe_chart_init(self):
        self.assertNotIn("new frappe.Chart", self.js,
                          "Must not initialize Frappe Charts in Layer 5")

    def test_no_global_promise_all(self):
        self.assertNotIn("Promise.all", self.js,
                          "Must not use global Promise.all blocker")

    # ── DOM safety ────────────────────────────────────────────────────────────

    def test_uses_page_main(self):
        self.assertIn("page.main", self.js)

    def test_does_not_use_page_body(self):
        self.assertNotIn(".appendTo(page.body)", self.js)
        self.assertNotIn("page.body.append", self.js)

    def test_title_is_plain_text(self):
        self.assertIn("title: 'Executive Command Centre V3'", self.js)
        title_section = self.js.split("title:")[1].split(",")[0]
        self.assertNotIn("<span", title_section)

    def test_no_render_template(self):
        self.assertNotIn("frappe.render_template(", self.js)

    # ── Service Delivery empty-state and error handling ───────────────────────

    def test_service_delivery_empty_state(self):
        self.assertIn("No service delivery data available", self.js,
                      "Must have empty-state text for service delivery sections")

    def test_service_delivery_error_element(self):
        self.assertIn("service-delivery-error", self.js,
                      "Must have visible service-delivery-error element")

    def test_service_delivery_error_log(self):
        self.assertIn("service delivery hydration failed", self.js)

    # ── SLA/Risk empty-state and error handling ───────────────────────────────

    def test_sla_risk_empty_states(self):
        self.assertIn("No SLA breach data available for the selected filters.", self.js)
        self.assertIn("No escalation status data available for the selected filters.", self.js)
        self.assertIn("No unresolved escalations for the selected filters.", self.js)

    def test_sla_risk_error_element(self):
        self.assertIn("sla-risk-error", self.js,
                      "Must have visible sla-risk-error element")

    def test_sla_risk_error_log(self):
        self.assertIn("sla risk hydration failed", self.js)

    # ── Payments empty-state and error handling ───────────────────────────────

    def test_payments_empty_states(self):
        self.assertIn("No payment summary data available for the selected filters.", self.js)
        self.assertIn("No failed payments for the selected filters.", self.js)
        self.assertIn("No pending payments for the selected filters.", self.js)

    def test_payments_error_element(self):
        self.assertIn("payments-error", self.js,
                      "Must have visible payments-error element")

    def test_payments_error_log(self):
        self.assertIn("payment reconciliation hydration failed", self.js)

    # ── Officer Workload empty-state and error handling ───────────────────────

    def test_officer_workload_empty_state(self):
        self.assertIn("No officer workload data available for the selected filters.", self.js)

    def test_officer_workload_error_element(self):
        self.assertIn("officer-workload-error", self.js,
                      "Must have visible officer-workload-error element")

    def test_officer_workload_error_log(self):
        self.assertIn("officer workload hydration failed", self.js)

    # ── Console log discipline ────────────────────────────────────────────────

    def test_layer7_first_paint_log(self):
        self.assertIn("[NileGov Command Centre V2] layer7 first paint injected", self.js)

    def test_service_delivery_started_log(self):
        self.assertIn("[NileGov Command Centre V2] service delivery hydration started", self.js)

    def test_service_delivery_completed_log(self):
        self.assertIn("[NileGov Command Centre V2] service delivery hydration completed", self.js)

    def test_sla_risk_started_log(self):
        self.assertIn("[NileGov Command Centre V2] sla risk hydration started", self.js)

    def test_sla_risk_completed_log(self):
        self.assertIn("[NileGov Command Centre V2] sla risk hydration completed", self.js)

    def test_officer_workload_started_log(self):
        self.assertIn("[NileGov Command Centre V2] officer workload hydration started", self.js)

    def test_officer_workload_completed_log(self):
        self.assertIn("[NileGov Command Centre V2] officer workload hydration completed", self.js)

    # ── Layer 3 behaviors preserved ───────────────────────────────────────────

    def test_filter_hydration_logs_preserved(self):
        self.assertIn("[NileGov Command Centre V2] filter hydration started", self.js)
        self.assertIn("[NileGov Command Centre V2] filter hydration completed", self.js)
        self.assertIn("[NileGov Command Centre V2] filter hydration failed", self.js)

    def test_overview_refresh_logs_preserved(self):
        self.assertIn("[NileGov Command Centre V2] overview refresh started", self.js)
        self.assertIn("[NileGov Command Centre V2] overview refresh completed", self.js)
        self.assertIn("[NileGov Command Centre V2] overview refresh failed", self.js)

    def test_fallback_all_services(self):
        self.assertIn("All Services", self.js)

    def test_fallback_all_statuses(self):
        self.assertIn("All Statuses", self.js)

    def test_fallback_all_locations(self):
        self.assertIn("All Locations", self.js)

    def test_filter_warning_element(self):
        self.assertIn("filter-warning", self.js)

    def test_kpi_error_state_element(self):
        self.assertIn("kpi-error-state", self.js)

    def test_zero_value_fallback(self):
        self.assertIn("'0'", self.js)

    # ── JS syntax ─────────────────────────────────────────────────────────────

    def test_js_syntax_valid(self):
        result = subprocess.run(["node", "-c", self.js_path], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"JS syntax error: {result.stderr}")

    # ── Workspace routing ──────────────────────────────────────────────────────

    def test_workspace_links_to_v2(self):
        links = self.workspace.get("links", [])
        v2_linked = any(
            l.get("type") == "Link" and l.get("link_to") == "nilegov-command-centre-v3"
            for l in links
        )
        self.assertTrue(v2_linked, "Workspace must link to nilegov-command-centre-v3")

    def test_workspace_does_not_link_to_old_route(self):
        links = self.workspace.get("links", [])
        old_linked = any(
            l.get("type") == "Link" and l.get("link_to") == "nilegov-command-centre"
            for l in links
        )
        self.assertFalse(old_linked, "Workspace must NOT link to old nilegov-command-centre")
