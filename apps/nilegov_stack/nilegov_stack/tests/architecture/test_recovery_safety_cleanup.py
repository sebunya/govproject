# Recovery Safety Cleanup - Static Architecture Tests
# Digi-Verse Uganda Limited

import os
import re
try:
    import pytest
except ImportError:
    pytest = None

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
API_FILE = os.path.join(BASE_DIR, "interfaces", "frappe", "api", "public_readiness.py")
API_INIT = os.path.join(BASE_DIR, "interfaces", "frappe", "api", "__init__.py")
WWW_DIR = os.path.join(BASE_DIR, "nilegov_stack", "www")
DOCTYPE_DIR = os.path.join(BASE_DIR, "nilegov_stack", "doctype")
WEBFORM_DIR = os.path.join(BASE_DIR, "nilegov_stack", "web_form")

APPROVED_ENDPOINTS = {
    "get_service_catalogue_preview",
    "get_lost_nid_intake_schema",
    "get_evidence_metadata_schema",
    "get_consent_capture_schema",
    "get_prototype_payment_requirement_preview",
    "get_interoperability_disclaimer",
    "get_redacted_case_status_preview",
}

REMOVED_ENDPOINTS = {
    "get_nira_data_preview",
    "get_ura_data_preview",
    "simulate_erp_sync",
    "simulate_payment",
}

class TestRecoverySafetyCleanup:
    def test_removed_endpoints_are_absent_from_api(self):
        """Verifies that all unapproved guest simulated endpoints have been completely deleted from API."""
        assert os.path.isfile(API_FILE), f"API file not found at {API_FILE}"
        with open(API_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        for ep in REMOVED_ENDPOINTS:
            assert f"def {ep}(" not in content, f"Unapproved endpoint '{ep}' is still defined in public_readiness.py"

    def test_only_approved_endpoints_are_exported(self):
        """Verifies that API init only imports/exports approved endpoints and no unapproved ones."""
        assert os.path.isfile(API_INIT), f"API init not found at {API_INIT}"
        with open(API_INIT, "r", encoding="utf-8") as f:
            content = f.read()

        for ep in REMOVED_ENDPOINTS:
            assert ep not in content, f"API init exports/imports unapproved endpoint '{ep}'"

    def test_no_bypass_patterns_exist_in_api(self):
        """Ensures that no string-concatenation or byte-decoding bypasses are present in public_readiness.py."""
        assert os.path.isfile(API_FILE), f"API file not found at {API_FILE}"
        with open(API_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Forbidden bypass indicators
        bypass_indicators = [
            '"payment_" + "status"',
            "'payment_' + 'status'",
            '("pay" + "ment_status")',
            "('pay' + 'ment_status')",
            'b"payment_status".decode',
            "b'payment_status'.decode",
            "string concatenation bypass",
        ]
        for indicator in bypass_indicators:
            assert indicator not in content, f"Bypass indicator '{indicator}' detected in public_readiness.py"

    def test_no_mbarara_wording_in_codebase(self):
        """Verifies that the hardcoded municipality reference 'Mbarara' is not present in doctypes, www, or web forms."""
        paths_to_scan = [WWW_DIR, DOCTYPE_DIR, WEBFORM_DIR]
        for path in paths_to_scan:
            if not os.path.exists(path):
                continue
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith((".py", ".js", ".html", ".json")):
                        file_path = os.path.join(root, file)
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        assert "mbarara" not in content.lower(), f"Forbidden locality name 'Mbarara' detected in file: {file_path}"

    def test_no_unverified_data_protection_act_claims(self):
        """Ensures that specific Section 10 and Data Protection Act 2019 claims are generalized."""
        paths_to_scan = [WWW_DIR, DOCTYPE_DIR, WEBFORM_DIR]
        for path in paths_to_scan:
            if not os.path.exists(path):
                continue
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith((".py", ".js", ".html")):
                        file_path = os.path.join(root, file)
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        assert "section 10" not in content.lower(), f"Unverified clause 'Section 10' detected in file: {file_path}"
                        assert "data protection act" not in content.lower(), f"Unverified claim 'Data Protection Act' detected in file: {file_path}"

    def test_track_page_is_prototype_only(self):
        """Verifies that track.html includes the required prototype status banner and uses redacted API lookup."""
        track_html_path = os.path.join(WWW_DIR, "track.html")
        assert os.path.isfile(track_html_path), "track.html not found"
        with open(track_html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should present a prototype warning banner
        assert "Prototype status preview only" in content, "track.html missing prototype warning banner"
        # Verify it only references the approved redacted case status endpoint
        assert "get_redacted_case_status_preview" in content, "track.html is not calling get_redacted_case_status_preview"
        for ep in REMOVED_ENDPOINTS:
            assert ep not in content, f"track.html calls unapproved endpoint {ep}"

    def test_web_form_js_is_safe_and_generic(self):
        """Ensures Web Form JS files are clean of removed endpoints and specific legislation claims."""
        js_files = [
            os.path.join(WEBFORM_DIR, "nilegov_lost_nid_replacement_intake", "nilegov_lost_nid_replacement_intake.js"),
            os.path.join(WEBFORM_DIR, "nilegov_citizen_consent_capture", "nilegov_citizen_consent_capture.js"),
            os.path.join(WEBFORM_DIR, "nilegov_evidence_supplement_metadata", "nilegov_evidence_supplement_metadata.js"),
        ]
        for js_path in js_files:
            if not os.path.isfile(js_path):
                continue
            with open(js_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Ensure no removed endpoint calls
            for ep in REMOVED_ENDPOINTS:
                assert ep not in content, f"Web Form JS {js_path} references unapproved endpoint {ep}"
            assert "mbarara" not in content.lower(), f"Web Form JS {js_path} references Mbarara"
            assert "section 10" not in content.lower(), f"Web Form JS {js_path} references Section 10"

    def test_service_request_js_is_generic(self):
        """Verifies service request JS uses generic SOP checklist titles and has no Mbarara references."""
        sr_js_path = os.path.join(DOCTYPE_DIR, "nilegov_service_request", "nilegov_service_request.js")
        assert os.path.isfile(sr_js_path), "nilegov_service_request.js not found"
        with open(sr_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "SOP Checklist (District Service Protocol)" in content, "nilegov_service_request.js has unapproved SOP title"
        assert "mbarara" not in content.lower(), "nilegov_service_request.js has hardcoded Mbarara references"
        assert "District Jurisdiction Validated" in content, "nilegov_service_request.js missing jurisdiction validator check"
