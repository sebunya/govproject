# Pass 11B-7C: Public REST API Scaffold — Static Architecture Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live external integration.
#

import inspect
import os
import re
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Path & Module Import
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTER_PACKAGE = os.path.dirname(os.path.dirname(BASE_DIR))
API_MODULE_PATH = os.path.join(OUTER_PACKAGE, "interfaces", "frappe", "api", "public_readiness.py")

EXPECTED_FUNCTIONS = [
    "get_service_catalogue_preview",
    "get_lost_nid_intake_schema",
    "get_evidence_metadata_schema",
    "get_consent_capture_schema",
    "get_prototype_payment_requirement_preview",
    "get_interoperability_disclaimer",
]

# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestPublicAPIScaffoldExists:
    def test_api_module_exists(self):
        assert os.path.isfile(API_MODULE_PATH), f"public_readiness.py not found: {API_MODULE_PATH}"

class TestPublicAPIMethodsDecoration:
    def test_functions_are_defined_and_whitelisted(self):
        with open(API_MODULE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        for fn in EXPECTED_FUNCTIONS:
            # Check function definition
            assert f"def {fn}(" in content, f"Function '{fn}' is not defined in public_readiness.py"
            
            # Verify whitelist decoration
            pattern = rf"@frappe\.whitelist\([^)]*\)\s*def {fn}\("
            assert re.search(pattern, content) or f"@frappe.whitelist()\ndef {fn}" in content or f"@frappe.whitelist(allow_guest=True)\ndef {fn}" in content, (
                f"Function '{fn}' is not decorated with @frappe.whitelist"
            )

class TestPublicAPISafetyRules:
    FORBIDDEN_FIELDS = [
        "officer_notes",
        "assigned_officer",
        "assigned_supervisor",
        "closure_notes",
        "payment_status",
        "identity_status",
        "decision",
        "verification_status",
    ]

    def test_no_secrets_or_forbidden_fields_in_api(self):
        with open(API_MODULE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # No secrets
        assert ".env" not in content
        assert "secret" not in content.lower()
        assert "password" not in content.lower()
        assert "token" not in content.lower()
        # Filter decorators to check for forbidden email-like "@"
        clean_content = re.sub(r'@[a-zA-Z_][a-zA-Z0-9_.]*', '', content)
        assert "@" not in clean_content

        # Exclude internal workflow and private details
        for field in self.FORBIDDEN_FIELDS:
            # Skip docstring/comments checks if matched in quotes as fields
            assert f"'{field}'" not in content, f"API contains forbidden field string: '{field}'"
            assert f'"{field}"' not in content, f"API contains forbidden field string: '{field}'"

    def test_disclaimer_mandatory_presence(self):
        with open(API_MODULE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        assert "PUBLIC_DISCLAIMER" in content
        assert "PAYMENT_DISCLAIMER" in content
        assert "Prototype" in content
        assert "No live" in content
