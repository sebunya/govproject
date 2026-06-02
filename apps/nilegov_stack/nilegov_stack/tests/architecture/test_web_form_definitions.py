# Pass 11B-7B: Web Form Definitions — Static Architecture Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live web portal intakes claimed.
#

import json
import os
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTER_PACKAGE = os.path.dirname(os.path.dirname(BASE_DIR))
INNER_APP = os.path.join(OUTER_PACKAGE, "nilegov_stack")
WEB_FORM_ROOT = os.path.join(INNER_APP, "web_form")
HOOKS_PATH = os.path.join(OUTER_PACKAGE, "hooks.py")

EXPECTED_WEB_FORMS = {
    "nilegov_lost_nid_replacement_intake": {
        "name": "NileGov Lost National ID Replacement Intake",
        "doc_type": "NileGov Service Request",
        "exposed_fields": ["citizen_full_name", "nin", "phone", "email", "location", "reason_for_request", "consent_confirmed"],
        "excluded_fields": ["internal_status", "assigned_officer", "assigned_supervisor", "assigned_department", "sla_state", "payment_status", "decision", "closure_notes"],
    },
    "nilegov_evidence_supplement_metadata": {
        "name": "NileGov Evidence Supplement Metadata",
        "doc_type": "NileGov Evidence Document",
        "exposed_fields": ["service_request", "document_type", "document_title"],
        "excluded_fields": ["verification_status", "verified_by", "verified_timestamp", "officer_notes"],
    },
    "nilegov_citizen_consent_capture": {
        "name": "NileGov Citizen Consent Capture",
        "doc_type": "NileGov Consent Record",
        "exposed_fields": ["citizen_profile", "service_request", "consent_purpose", "consent_status"],
        "excluded_fields": ["consent_given_at", "consent_withdrawn_at", "consent_expiry_date"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _load_web_form_json(folder):
    path = os.path.join(WEB_FORM_ROOT, folder, f"{folder}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestWebFormFilesExist:
    @pytest.mark.parametrize("folder", list(EXPECTED_WEB_FORMS.keys()))
    def test_web_form_json_exists(self, folder):
        path = os.path.join(WEB_FORM_ROOT, folder, f"{folder}.json")
        assert os.path.isfile(path), f"Web Form JSON not found: {path}"

class TestWebFormJSONValidity:
    REQUIRED_KEYS = {"name", "doc_type", "doctype", "module", "is_standard", "published", "login_required", "web_form_fields", "introduction_text"}

    @pytest.mark.parametrize("folder", list(EXPECTED_WEB_FORMS.keys()))
    def test_web_form_json_is_valid(self, folder):
        doc = _load_web_form_json(folder)
        assert isinstance(doc, dict), f"{folder}.json must be a JSON object"

    @pytest.mark.parametrize("folder", list(EXPECTED_WEB_FORMS.keys()))
    def test_web_form_has_required_keys(self, folder):
        doc = _load_web_form_json(folder)
        for key in self.REQUIRED_KEYS:
            assert key in doc, f"{folder}.json missing required key: '{key}'"

    @pytest.mark.parametrize("folder,info", list(EXPECTED_WEB_FORMS.items()))
    def test_web_form_metadata_matches(self, folder, info):
        doc = _load_web_form_json(folder)
        assert doc["name"] == info["name"], f"{folder} name mismatch"
        assert doc["name"].startswith("NileGov"), f"{folder} name must start with 'NileGov'"
        assert doc["doc_type"] == info["doc_type"], f"{folder} doc_type mismatch"
        assert doc["doctype"] == "Web Form", f"{folder} doctype mismatch"
        assert doc["module"] == "NileGov Stack", f"{folder} module mismatch"
        assert doc["is_standard"] == 1, f"{folder} is_standard mismatch"
        assert doc["published"] == 0, f"{folder} must be unpublished (published=0)"
        assert doc["login_required"] == 1, f"{folder} must be login-required (login_required=1)"

    @pytest.mark.parametrize("folder,info", list(EXPECTED_WEB_FORMS.items()))
    def test_web_form_field_exposure(self, folder, info):
        doc = _load_web_form_json(folder)
        fields = [f.get("fieldname") for f in doc.get("web_form_fields", [])]
        
        # Verify exposed fields
        for f_exp in info["exposed_fields"]:
            assert f_exp in fields, f"{folder} missing expected public field: '{f_exp}'"
            
        # Verify excluded fields are NOT in web_form_fields
        for f_excl in info["excluded_fields"]:
            assert f_excl not in fields, f"{folder} exposes internal-only field: '{f_excl}'"

class TestWebFormSafety:
    @pytest.mark.parametrize("folder", list(EXPECTED_WEB_FORMS.keys()))
    def test_web_form_introduction_has_disclaimer(self, folder):
        doc = _load_web_form_json(folder)
        intro = doc.get("introduction_text") or ""
        assert "Prototype" in intro or "simulated" in intro or "No live" in intro, f"{folder} missing prototype/no-live disclaimer"
        assert "NIRA" in intro, f"{folder} disclaimer missing NIRA reference"

    @pytest.mark.parametrize("folder", list(EXPECTED_WEB_FORMS.keys()))
    def test_no_sensitive_claims_or_secrets(self, folder):
        doc = _load_web_form_json(folder)
        raw_text = json.dumps(doc).lower()
        
        # No secrets
        assert "secret" not in raw_text
        assert "token" not in raw_text
        assert "key" not in raw_text
        assert "password" not in raw_text
        
        # No personal emails
        assert "@" not in raw_text

class TestHooksFixturesWebForm:
    def test_hooks_lists_all_3_web_forms(self):
        with open(HOOKS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert '"dt": "Web Form"' in content or "'dt': 'Web Form'" in content
        
        for folder, info in EXPECTED_WEB_FORMS.items():
            name = info["name"]
            assert name in content, f"hooks.py fixtures does not include Web Form: '{name}'"
