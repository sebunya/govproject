# Pass 11B-6B: Print Format Definitions — Static Architecture Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live government statistics claimed.
#

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
PRINT_FORMAT_ROOT = os.path.join(INNER_APP, "print_format")
HOOKS_PATH = os.path.join(OUTER_PACKAGE, "hooks.py")

EXPECTED_PRINT_FORMATS = {
    "nilegov_service_request_acknowledgement_slip": {
        "name": "NileGov Service Request Acknowledgement Slip",
        "doc_type": "NileGov Service Request",
    },
    "nilegov_lost_national_id_replacement_case_summary": {
        "name": "NileGov Lost National ID Replacement Case Summary",
        "doc_type": "NileGov Service Request",
    },
    "nilegov_simulated_payment_receipt": {
        "name": "NileGov Simulated Payment Receipt",
        "doc_type": "NileGov Payment Record",
    },
    "nilegov_evidence_review_sheet": {
        "name": "NileGov Evidence Review Sheet",
        "doc_type": "NileGov Evidence Document",
    },
    "nilegov_sla_escalation_memo": {
        "name": "NileGov SLA Escalation Memo",
        "doc_type": "NileGov Escalation Record",
    },
    "nilegov_case_closure_certificate": {
        "name": "NileGov Case Closure Certificate",
        "doc_type": "NileGov Service Request",
    },
    "nilegov_m_e_summary_brief": {
        "name": "NileGov M&E Summary Brief",
        "doc_type": "NileGov Reporting Snapshot",
    },
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

FORBIDDEN_OFFICIAL_CLAIMS = [
    "official government statistics",
    "live government",
    "live nilegov",
    "live nira",
    "live ura",
    "live ughub",
]

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _load_print_format_json(folder):
    path = os.path.join(PRINT_FORMAT_ROOT, folder, f"{folder}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestPrintFormatFilesExist:
    @pytest.mark.parametrize("folder", list(EXPECTED_PRINT_FORMATS.keys()))
    def test_print_format_json_exists(self, folder):
        path = os.path.join(PRINT_FORMAT_ROOT, folder, f"{folder}.json")
        assert os.path.isfile(path), f"Print Format JSON not found: {path}"

class TestPrintFormatJSONValidity:
    REQUIRED_KEYS = {"name", "doc_type", "doctype", "module", "is_standard", "html"}

    @pytest.mark.parametrize("folder", list(EXPECTED_PRINT_FORMATS.keys()))
    def test_print_format_json_is_valid(self, folder):
        doc = _load_print_format_json(folder)
        assert isinstance(doc, dict), f"{folder}.json must be a JSON object"

    @pytest.mark.parametrize("folder", list(EXPECTED_PRINT_FORMATS.keys()))
    def test_print_format_has_required_keys(self, folder):
        doc = _load_print_format_json(folder)
        for key in self.REQUIRED_KEYS:
            assert key in doc, f"{folder}.json missing required key: '{key}'"

    @pytest.mark.parametrize("folder,info", list(EXPECTED_PRINT_FORMATS.items()))
    def test_print_format_metadata_matches(self, folder, info):
        doc = _load_print_format_json(folder)
        assert doc["name"] == info["name"], f"{folder} name mismatch"
        assert doc["doc_type"] == info["doc_type"], f"{folder} doc_type mismatch"
        assert doc["doctype"] == "Print Format", f"{folder} doctype mismatch"
        assert doc["module"] == "NileGov Stack", f"{folder} module mismatch"
        assert doc["is_standard"] == "Yes", f"{folder} is_standard mismatch"

class TestPrintFormatSafety:
    @pytest.mark.parametrize("folder", list(EXPECTED_PRINT_FORMATS.keys()))
    def test_print_format_html_has_disclaimer(self, folder):
        doc = _load_print_format_json(folder)
        html = (doc.get("html") or "").lower()
        has_disclaimer = (
            "prototype" in html or "simulated" in html
            or "not official" in html or "sandbox" in html
            or "simulation" in html
        )
        assert has_disclaimer, f"{folder} html missing prototype/simulated disclaimer warning."

    @pytest.mark.parametrize("folder", list(EXPECTED_PRINT_FORMATS.keys()))
    def test_no_forbidden_claims_in_html(self, folder):
        doc = _load_print_format_json(folder)
        html = (doc.get("html") or "").lower()
        # Clean expected disclaimers to prevent false positives
        cleaned = html
        cleaned = re.sub(r'\bnot official government statistics\b', '', cleaned)
        cleaned = re.sub(r'\bprototype simulation only\b', '', cleaned)
        cleaned = re.sub(r'\bno live payment was processed\b', '', cleaned)
        cleaned = re.sub(r'\bno live government registry access\b', '', cleaned)
        for claim in FORBIDDEN_OFFICIAL_CLAIMS:
            assert claim.lower() not in cleaned, f"{folder} html contains forbidden claim: '{claim}'"

class TestHooksFixturesPrintFormat:
    def test_hooks_lists_all_7_print_formats(self):
        with open(HOOKS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert '"dt": "Print Format"' in content or "'dt': 'Print Format'" in content
        
        for folder, info in EXPECTED_PRINT_FORMATS.items():
            name = info["name"]
            assert name in content, f"hooks.py fixtures does not include print format: '{name}'"
