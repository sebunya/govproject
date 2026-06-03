# Pass 11B-8D: Static Submission Manifest Verification Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live external integration.
#

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTER_PACKAGE = os.path.dirname(os.path.dirname(BASE_DIR))
MANIFEST_PATH = os.path.join(OUTER_PACKAGE, "..", "..", "..", "docs", "submission", "14_frappe_native_evidence_manifest.md")


class TestSubmissionManifest:
    def test_manifest_file_exists(self):
        assert os.path.isfile(MANIFEST_PATH), f"Manifest file not found at: {MANIFEST_PATH}"

    def test_manifest_contains_required_sections(self):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        sections = [
            "Executive Summary",
            "Current Verified State",
            "Capability-to-Artifact Matrix",
            "Frappe-Native Asset Register",
            "Test Coverage Register",
            "Runtime Validation Register",
            "Safe Claims",
            "Claims to Avoid",
            "Known Runtime Risks",
        ]
        for section in sections:
            assert section in content, f"Manifest is missing required section: '{section}'"

    def test_manifest_does_not_contain_secrets(self):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        assert ".env" not in content
        # Ensure no actual mock secrets or raw sensitive keys are written
        forbidden_patterns = ["=sk_", "api_key = ", "password = ", "client_secret = "]
        for pattern in forbidden_patterns:
            assert pattern not in content, f"Manifest contains forbidden pattern: {pattern}"

    def test_manifest_avoids_live_integration_claims(self):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # Check legacy and strict mock requirements
        assert "NileGov is NOT connected to live registry interfaces" in content
        assert "production payment" in content.lower()
