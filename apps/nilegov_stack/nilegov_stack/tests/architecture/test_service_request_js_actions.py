# Pass 11B-4A: Service Request JS Action Wiring — Static Architecture Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.
#
# These are static (no runtime Frappe bench required) tests that verify:
#  1.  JS file exists and is non-empty
#  2.  JS contains prototype/simulated disclaimer wording
#  3.  JS does not contain forbidden live-integration labels
#  4.  Every method: reference resolves to a whitelisted Python function
#  5.  JS contains no external HTTP URLs (no live calls)
#  6.  JS contains no .env or secret-like references
#  7.  State-changing buttons use frappe.confirm (confirmation prompts)
#  8.  Simulated action labels contain "Simulated" keyword
#  9.  JS button groups are the expected three groups
# 10.  All 10 whitelisted Python methods are present in the .py file
# 11.  JS references exactly the 10 known whitelisted methods
# 12.  METHODS constant maps all 10 method keys
# 13.  No Pesapal live references
# 14.  No .env access patterns

import os
import re
import ast
import inspect

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# tests/architecture/ → tests/ → nilegov_stack/ (outer package with tests/ and nilegov_stack/ subdirs)
OUTER_PACKAGE = os.path.dirname(os.path.dirname(BASE_DIR))
# Inner app dir is OUTER_PACKAGE/nilegov_stack/
INNER_APP = os.path.join(OUTER_PACKAGE, "nilegov_stack")
SR_DIR = os.path.join(INNER_APP, "doctype", "nilegov_service_request")
JS_PATH = os.path.join(SR_DIR, "nilegov_service_request.js")
PY_PATH = os.path.join(SR_DIR, "nilegov_service_request.py")

# Fully-qualified Python module path prefix used in JS
SR_MODULE_PATH = "nilegov_stack.nilegov_stack.doctype.nilegov_service_request.nilegov_service_request"

# Expected whitelisted function names (10 total)
EXPECTED_WHITELISTED = {
    "run_simulated_identity_check",
    "verify_payment",
    "assign_officer",
    "reassign_officer",
    "assign_department_team",
    "mark_supervisor_review",
    "return_case_to_officer",
    "evaluate_sla_state",
    "escalate_case",
    "resolve_escalation",
}

# Forbidden substrings in JS (case-insensitive) — live integration claims
FORBIDDEN_JS_STRINGS = [
    "live nira",
    "live ura",
    "live ughub",
    "production payment",
    "real payment clearance",
    "pesapal live",
    "nira live",
    "live payment gateway",
    "clearance from ministry",
]

# External URL patterns that must NOT appear
EXTERNAL_URL_PATTERN = re.compile(
    r'https?://(?!localhost|127\.0\.0\.1)',
    re.IGNORECASE
)

# Secret / .env patterns that must NOT appear
SECRET_PATTERN = re.compile(
    r'process\.env\.|os\.environ|SECRET_KEY|API_KEY\s*=\s*["\']',
    re.IGNORECASE
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────
def _js():
    with open(JS_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _py():
    with open(PY_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ─────────────────────────────────────────────────────────────────────────────
# 1. File existence
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSExists:
    def test_js_file_exists(self):
        assert os.path.isfile(JS_PATH), (
            f"Service Request JS not found: {JS_PATH}\n"
            "Pass 11B-4A requires nilegov_service_request.js to exist."
        )

    def test_js_file_is_non_empty(self):
        content = _js()
        assert len(content.strip()) > 200, (
            "Service Request JS file is too short — likely not upgraded."
        )

    def test_js_registers_form_handler(self):
        content = _js()
        assert "frappe.ui.form.on('NileGov Service Request'" in content, (
            "JS must register a handler for 'NileGov Service Request'."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Prototype wording
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSPrototypeBanner:
    def test_js_contains_prototype_disclaimer(self):
        content = _js()
        assert "Prototype" in content or "prototype" in content, (
            "JS must contain prototype disclaimer wording."
        )

    def test_js_contains_simulated_wording(self):
        content = _js()
        assert "simulated" in content.lower() or "Simulated" in content, (
            "JS must clarify that actions are simulated."
        )

    def test_js_has_no_live_gov_registry_claim(self):
        content = _js()
        assert "No live Government registry" in content or \
               "no live" in content.lower(), (
            "JS must explicitly state no live government registry is contacted."
        )

    def test_js_has_prototype_banner_via_set_intro_or_msgprint(self):
        content = _js()
        # onload sets prototype message via set_intro
        assert "set_intro" in content or "msgprint" in content, (
            "JS must display a prototype banner (set_intro or msgprint)."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 3. No forbidden live labels
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSNoForbiddenLabels:
    def _non_comment_content(self):
        """Return JS content with // comment lines stripped."""
        lines = _js().splitlines()
        return "\n".join(
            line for line in lines
            if not line.strip().startswith("//")
        )

    def test_no_live_nira_label(self):
        content = self._non_comment_content().lower()
        # 'no live nira' is acceptable (it is a disclaimer);
        # 'live nira' without a preceding 'no' negation is forbidden.
        import re as _re
        # Remove acceptable negating phrases first
        cleaned = _re.sub(r'no live (nira|ura|ughub|payment)', '', content)
        assert 'live nira' not in cleaned, (
            "JS button labels must not contain 'Live NIRA' as an affirmative claim."
        )

    def test_no_live_ughub_label(self):
        assert "live ughub" not in _js().lower()

    def test_no_live_ura_label(self):
        assert "live ura" not in _js().lower()

    def test_no_production_payment_label(self):
        assert "production payment" not in _js().lower()

    def test_no_pesapal_live_label(self):
        assert "pesapal live" not in _js().lower()

    def test_no_real_payment_clearance_label(self):
        assert "real payment clearance" not in _js().lower()

    def test_no_forbidden_strings_any(self):
        import re as _re
        content = self._non_comment_content().lower()
        # Remove negating phrases first (e.g. 'no live nira' is acceptable)
        content = _re.sub(r'no live (nira|ura|ughub|payment)', '', content)
        for kw in FORBIDDEN_JS_STRINGS:
            assert kw.lower() not in content, (
                f"JS contains forbidden live-integration string: '{kw}'"
            )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Method references resolve to whitelisted Python functions
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSMethodReferences:
    def _extract_all_method_strings(self):
        """Extract all function names defined in the JS METHODS constant.
        
        The JS uses a METHODS constant where values are built as:
          SR_MODULE + '.function_name'
        The pattern matches '.function_name' string literals concatenated via +.
        """
        content = _js()
        # Match string literals of form: + '.function_name' or + ".function_name"
        # These are the right-hand sides of METHODS constant entries
        suffix_pattern = re.compile(r"\+\s*['\"]\.(\w+)['\"]")
        return suffix_pattern.findall(content)

    def test_all_method_refs_start_with_sr_module_path(self):
        content = _js()
        # The METHODS constant must define SR_MODULE using the expected module path
        assert SR_MODULE_PATH in content, (
            f"JS must contain the module path '{SR_MODULE_PATH}' in the METHODS constant."
        )

    def test_all_method_refs_resolve_to_whitelisted_functions(self):
        refs = self._extract_all_method_strings()
        assert refs, "JS METHODS constant must define at least one function suffix."
        py_content = _py()
        for func_name in refs:
            assert func_name in EXPECTED_WHITELISTED, (
                f"JS METHODS constant references '{func_name}' which is not whitelisted."
            )
            assert func_name in py_content, (
                f"JS METHODS constant references '{func_name}' not found in {PY_PATH}"
            )

    def test_no_method_refs_to_unknown_functions(self):
        refs = self._extract_all_method_strings()
        for func_name in refs:
            assert func_name in EXPECTED_WHITELISTED, (
                f"JS METHODS constant references unknown function '{func_name}'."
            )


# ─────────────────────────────────────────────────────────────────────────────
# 5. No external URLs
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSNoExternalURLs:
    def test_no_external_http_calls(self):
        content = _js()
        matches = EXTERNAL_URL_PATTERN.findall(content)
        # Filter out any that are inside comments (start with // on same line)
        # Simple check: find if the URL is in a non-comment context
        # For prototype level, just flag any external URL at all
        assert not matches, (
            f"JS contains external URL references (no live calls permitted): {matches}"
        )

    def test_no_fetch_or_xmlhttprequest_to_external(self):
        content = _js()
        # These patterns indicate a hand-rolled HTTP call bypassing frappe.call
        assert "XMLHttpRequest" not in content, (
            "JS must not use XMLHttpRequest directly."
        )
        # fetch() to external is also forbidden; frappe.call is the only allowed method
        # Allow fetch only if followed by /api/ (Frappe internal)
        raw_fetch = re.findall(r"fetch\s*\(\s*['\"]https?://", content)
        assert not raw_fetch, (
            f"JS contains fetch() to external URL: {raw_fetch}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 6. No .env or secret references
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSNoSecrets:
    def test_no_env_references(self):
        content = _js()
        assert "process.env." not in content, (
            "JS must not reference process.env.* (no secret exposure)."
        )

    def test_no_api_key_hardcoded(self):
        content = _js()
        matches = re.findall(r'(?i)(api_key|secret_key|password)\s*[=:]\s*["\'][^"\']{4,}', content)
        assert not matches, (
            f"JS contains hardcoded secret-like values: {matches}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 7. Confirmation prompts on state-changing actions
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSConfirmation:
    def test_has_frappe_confirm_calls(self):
        content = _js()
        assert "frappe.confirm" in content, (
            "JS must use frappe.confirm() for state-changing button actions."
        )

    def test_confirm_count_matches_state_changing_buttons(self):
        content = _js()
        # frappe.confirm appears once in the helper definition _confirm();
        # _confirm( calls are the actual usages — count both
        direct_confirms = content.count("frappe.confirm")
        helper_calls = content.count("_confirm(")
        total = direct_confirms + helper_calls
        assert total >= 6, (
            f"Expected at least 6 total confirmation invocations "
            f"(frappe.confirm={direct_confirms} + _confirm calls={helper_calls}), "
            f"total={total}."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 8. Simulated action labels contain "Simulated"
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSSimulatedLabels:
    def test_identity_check_button_labelled_simulated(self):
        content = _js()
        # The identity check button must say "Simulated" in its label
        assert "Simulated Identity Check" in content or \
               "Run Simulated Identity" in content, (
            "Identity check button must contain 'Simulated' in its label."
        )

    def test_payment_button_labelled_simulated(self):
        content = _js()
        assert "Simulated Payment" in content or \
               "Run Simulated Payment" in content, (
            "Payment verification button must contain 'Simulated' in its label."
        )

    def test_simulated_group_label_present(self):
        content = _js()
        assert "Simulated Actions" in content, (
            "JS must group simulated actions under a 'Simulated Actions' button group."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 9. Button groups
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSButtonGroups:
    EXPECTED_GROUPS = {
        "Simulated Actions",
        "Officer Actions",
        "Supervisor Actions",
    }

    def test_all_button_groups_present(self):
        content = _js()
        for grp in self.EXPECTED_GROUPS:
            assert grp in content, (
                f"JS must define button group '{grp}' for logical grouping."
            )


# ─────────────────────────────────────────────────────────────────────────────
# 10. All 10 whitelisted Python methods exist in .py
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestPythonWhitelist:
    def test_py_file_exists(self):
        assert os.path.isfile(PY_PATH)

    def test_all_10_whitelisted_methods_present(self):
        content = _py()
        missing = []
        for fn in EXPECTED_WHITELISTED:
            if f"def {fn}" not in content:
                missing.append(fn)
        assert not missing, (
            f"Python controller is missing these whitelisted methods: {missing}"
        )

    def test_all_whitelisted_methods_have_decorator(self):
        content = _py()
        for fn in EXPECTED_WHITELISTED:
            # Find the @frappe.whitelist() decorator immediately before def fn
            idx = content.find(f"def {fn}")
            if idx == -1:
                continue  # caught by previous test
            # Check backward for @frappe.whitelist in the preceding 80 chars
            preceding = content[max(0, idx - 80):idx]
            assert "@frappe.whitelist" in preceding, (
                f"Function '{fn}' is not decorated with @frappe.whitelist()."
            )


# ─────────────────────────────────────────────────────────────────────────────
# 11. JS references exactly the 10 known methods (no extras, no missing)
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSMethodCoverage:
    def _js_func_names(self):
        """Extract all function suffix names from the JS METHODS constant."""
        content = _js()
        # Match + '.function_name' patterns (METHODS constant values)
        pattern = re.compile(r"\+\s*['\"]\.(\w+)['\"]")
        return set(pattern.findall(content))

    def test_js_references_all_10_whitelisted_methods(self):
        found = self._js_func_names()
        missing = EXPECTED_WHITELISTED - found
        assert not missing, (
            f"JS METHODS constant missing these whitelisted methods: {sorted(missing)}. "
            f"Each must appear as \"+ '.func_name'\" in the METHODS constant."
        )

    def test_js_does_not_reference_unknown_methods(self):
        found = self._js_func_names()
        extra = found - EXPECTED_WHITELISTED
        assert not extra, (
            f"JS METHODS constant references unknown (non-whitelisted) methods: {sorted(extra)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 12. METHODS constant in JS maps all 10 keys
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSMethodsConstant:
    EXPECTED_KEYS = {
        "runSimulatedIdentityCheck",
        "verifyPayment",
        "assignOfficer",
        "reassignOfficer",
        "assignDepartmentTeam",
        "markSupervisorReview",
        "returnCaseToOfficer",
        "evaluateSLAState",
        "escalateCase",
        "resolveEscalation",
    }

    def test_methods_constant_has_all_10_keys(self):
        content = _js()
        for key in self.EXPECTED_KEYS:
            assert key in content, (
                f"JS METHODS constant is missing key '{key}'."
            )


# ─────────────────────────────────────────────────────────────────────────────
# 13. No Pesapal live references
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSNoPesapalLive:
    def test_no_pesapal_live_key(self):
        content = _js()
        assert "pesapal_live" not in content.lower()
        assert "pesapal live" not in content.lower()

    def test_no_consumer_key_hardcoded(self):
        content = _js()
        assert "ConsumerKey" not in content
        assert "consumer_key" not in content.lower() or \
               "simulated" in content.lower(), (
            "If consumer_key appears, it must be in a simulated context."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 14. Error handling present
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceRequestJSErrorHandling:
    def test_has_error_callback(self):
        content = _js()
        assert "error:" in content or "r.exc" in content, (
            "JS must handle errors from frappe.call (error: or r.exc check)."
        )

    def test_has_show_alert_or_msgprint_on_success(self):
        content = _js()
        assert "frappe.show_alert" in content or "frappe.msgprint" in content, (
            "JS must show a user-visible success message after actions."
        )

    def test_form_reloads_after_action(self):
        content = _js()
        assert "frm.reload_doc()" in content or "frm.refresh()" in content, (
            "JS must reload/refresh the form after a successful action."
        )
