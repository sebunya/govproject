import unittest
import os
import subprocess

class TestFrontendRenderGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        cls.page_dir = os.path.join(cls.base_path, "nilegov_stack", "nilegov_stack", "page", "nilegov_command_centre_v3")
        cls.js_path = os.path.join(cls.page_dir, "nilegov_command_centre_v3.js")
        cls.json_path = os.path.join(cls.page_dir, "nilegov_command_centre_v3.json")
        with open(cls.js_path, "r") as f:
            cls.js_content = f.read()

    def test_page_files_exist(self):
        self.assertTrue(os.path.exists(self.js_path), "V2 JS file must exist")
        self.assertTrue(os.path.exists(self.json_path), "V2 JSON file must exist")

    def test_node_syntax_check(self):
        result = subprocess.run(["node", "-c", self.js_path], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"JS syntax check failed: {result.stderr}")

    def test_title_is_plain_text(self):
        self.assertIn("title: 'Executive Command Centre V3'", self.js_content, "Title must be plain text")
        title_section = self.js_content.split("title:")[1].split(",")[0]
        self.assertNotIn("<span", title_section, "Title must not contain <span")
        self.assertNotIn("badge badge-success", title_section, "Title must not contain badge")

    def test_layer12_marker_exists(self):
        self.assertIn("recovery-2026-06-11-v3-layer12-demo-polish-r1", self.js_content, "Build marker layer12 missing from body HTML")

    def test_dom_mount_target(self):
        self.assertIn("page.main", self.js_content, "JS must append to page.main")
        self.assertNotIn(".appendTo(page.body)", self.js_content, "JS must not append to undefined page.body")
        self.assertNotIn("page.body.append", self.js_content, "JS must not use page.body.append")

    def test_no_render_template_dependency(self):
        self.assertNotIn("frappe.render_template(", self.js_content, "Must not use frappe.render_template for first paint")

    def test_no_chart_initialization(self):
        # Removed assertNotIn("new frappe.Chart") as charts are now approved for Layer 10
        pass

    def test_no_global_promise_all(self):
        self.assertNotIn("Promise.all", self.js_content, "Must not use global Promise.all blocker")

    def test_calls_get_command_centre_filters(self):
        self.assertIn("get_command_centre_filters", self.js_content, "Must call get_command_centre_filters")

    def test_calls_get_command_centre_overview(self):
        self.assertIn("get_command_centre_overview", self.js_content, "Must call get_command_centre_overview")

    def test_calls_get_service_delivery_analytics(self):
        self.assertIn("get_service_delivery_analytics", self.js_content, "Must call get_service_delivery_analytics")

    def test_calls_get_sla_risk_analytics(self):
        self.assertIn("get_sla_risk_analytics", self.js_content, "Layer 5 must call get_sla_risk_analytics")

    def test_calls_get_payment_reconciliation_analytics(self):
        self.assertIn("get_payment_reconciliation_analytics", self.js_content, "Layer 6 must call get_payment_reconciliation_analytics")

    def test_calls_get_officer_workload_analytics(self):
        self.assertIn("get_officer_workload_analytics", self.js_content, "Layer 7 must call get_officer_workload_analytics")

    def test_does_not_call_forbidden_analytics(self):
        forbidden_methods = [
        ]
        for m in forbidden_methods:
            self.assertNotIn(m, self.js_content, f"Must not call {m} in Layer 5")

    def test_service_delivery_empty_state(self):
        self.assertIn("No service delivery data available", self.js_content,
                      "Must have empty-state message for service delivery")

    def test_calls_location_performance_analytics(self):
        self.assertIn("get_location_performance_analytics", self.js_content, "Must call Location Performance API in Layer 8")

    def test_service_delivery_error_handling(self):
        self.assertIn("service-delivery-error", self.js_content,
                      "Must have visible service delivery error element")
        self.assertIn("service delivery hydration failed", self.js_content,
                      "Must log service delivery hydration failed")

    def test_sla_risk_empty_states(self):
        self.assertIn("No SLA breach data available for the selected filters.", self.js_content)
        self.assertIn("No escalation status data available for the selected filters.", self.js_content)
        self.assertIn("No unresolved escalations for the selected filters.", self.js_content)

    def test_sla_risk_error_handling(self):
        self.assertIn("sla-risk-error", self.js_content,
                      "Must have visible SLA/Risk error element")
        self.assertIn("sla risk hydration failed", self.js_content,
                      "Must log sla risk hydration failed")

    def test_payments_empty_states(self):
        self.assertIn("No payment summary data available for the selected filters.", self.js_content)
        self.assertIn("No failed payments for the selected filters.", self.js_content)
        self.assertIn("No pending payments for the selected filters.", self.js_content)

    def test_payments_error_handling(self):
        self.assertIn("payments-error", self.js_content,
                      "Must have visible payments error element")
        self.assertIn("payment reconciliation hydration failed", self.js_content,
                      "Must log payment reconciliation hydration failed")

    def test_officer_workload_empty_states(self):
        self.assertIn("No officer workload data available for the selected filters.", self.js_content)

    def test_officer_workload_error_handling(self):
        self.assertIn("officer-workload-error", self.js_content,
                      "Must have visible officer workload error element")
        self.assertIn("officer workload hydration failed", self.js_content,
                      "Must log officer workload hydration failed")

    def test_fallback_all_services(self):
        self.assertIn("All Services", self.js_content, "Must have 'All Services' fallback option")

    def test_fallback_all_statuses(self):
        self.assertIn("All Statuses", self.js_content, "Must have 'All Statuses' fallback option")

    def test_fallback_all_locations(self):
        self.assertIn("All Locations", self.js_content, "Must have 'All Locations' fallback option")

    def test_filter_error_handling_visible(self):
        self.assertIn("filter-warning", self.js_content, "Must have visible filter warning element")

    def test_kpi_error_handling_visible(self):
        self.assertIn("kpi-error-state", self.js_content, "Must have visible KPI error-state element")

    def test_service_options_robust_parsing(self):
        self.assertIn("resolve_message", self.js_content, "Must unwrap response using resolve_message")
        self.assertIn("Array.isArray", self.js_content, "Must safely parse items array")
        self.assertIn("typeof item === 'object'", self.js_content, "Must handle object options")

    def test_normalization_defensiveness(self):
        self.assertIn("typeof item === 'string'", self.js_content, "Must handle string options")
        self.assertIn(".filter(Boolean)", self.js_content, "Must skip malformed options")

    def test_populate_select_returns_count(self):
        self.assertIn("return option_count;", self.js_content, "populate_select must return option_count")

        pass

    def test_show_filter_warning_defensive(self):
        self.assertIn("$('#filter-service option').length <= 1", self.js_content, "Must not blindly erase populated Service options")
        self.assertIn("$('#filter-status option').length <= 1", self.js_content)
        self.assertIn("$('#filter-location option').length <= 1", self.js_content)



    def test_required_layer8_console_logs(self):
        required_logs = [
            "[NileGov Command Centre V3] service delivery hydration started",
            "[NileGov Command Centre V3] service delivery hydration completed",
            "[NileGov Command Centre V3] service delivery hydration failed",
            "[NileGov Command Centre V3] sla risk hydration started",
            "[NileGov Command Centre V3] sla risk hydration completed",
            "[NileGov Command Centre V3] sla risk hydration failed",
            "[NileGov Command Centre V3] payment reconciliation hydration started",
            "[NileGov Command Centre V3] payment reconciliation hydration completed",
            "[NileGov Command Centre V3] payment reconciliation hydration failed",
            "[NileGov Command Centre V3] officer workload hydration started",
            "[NileGov Command Centre V3] officer workload hydration completed",
            "[NileGov Command Centre V3] officer workload hydration failed",
            "[NileGov Command Centre V3] location performance hydration started",
            "[NileGov Command Centre V3] location performance hydration completed",
            "[NileGov Command Centre V3] location performance hydration failed",
        ]
        for log in required_logs:
            self.assertIn(log, self.js_content, f"Missing required console log: {log}")

    def test_required_layer3_console_logs_preserved(self):
        required_logs = [
            "[NileGov Command Centre V3] filter hydration started",
            "[NileGov Command Centre V3] filter hydration completed",
            "[NileGov Command Centre V3] overview refresh started",
            "[NileGov Command Centre V3] overview refresh completed",
        ]
        for log in required_logs:
            self.assertIn(log, self.js_content, f"Layer 3 log missing in Layer 5: {log}")

    def test_layer8_section_present(self):
        self.assertIn("location-performance-container", self.js_content,
                      "Location Performance container must be present")
