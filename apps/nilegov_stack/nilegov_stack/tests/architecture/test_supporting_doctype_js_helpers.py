# Pass 11B-4B: Supporting DocType JS Helpers — Static Architecture Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live Government registry access.
#
# Static tests (no Frappe bench required) verifying:
#  1.  All four JS files exist and are non-empty
#  2.  Each JS has a prototype/simulated/sandbox disclaimer
#  3.  No JS contains forbidden live integration labels
#  4.  No JS contains external URLs
#  5.  No JS references .env, secrets, tokens or private keys
#  6.  Evidence JS does not claim official verification
#  7.  Payment JS does not claim production payment or real clearance
#  8.  Reporting Snapshot JS does not claim official government statistics
#  9.  Escalation JS introduces no unknown frappe.call backend methods
# 10.  Any frappe.call method references map to existing whitelisted methods
# 11.  Navigation buttons use frappe.set_route (safe read-only navigation)
# 12.  Each JS registers the correct DocType name in frappe.ui.form.on

import os
import re
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# tests/architecture/ → tests/ → nilegov_stack/ (outer package)
OUTER_PACKAGE = os.path.dirname(os.path.dirname(BASE_DIR))
INNER_APP = os.path.join(OUTER_PACKAGE, "nilegov_stack")
DOCTYPE_ROOT = os.path.join(INNER_APP, "doctype")

TARGET_DOCTYPE_INFO = {
    "nilegov_evidence_document": {
        "doctype_name": "NileGov Evidence Document",
        "forbidden_labels": [
            "live verification",
            "official police verification",
            "official nira verification",
            "live nira",
            "court verification",
        ],
        "required_disclaimer_words": ["prototype", "simulated", "no live"],
        "must_not_claim": ["official", "live registry"],
        "linked_fields": ["service_request", "citizen_profile"],
    },
    "nilegov_payment_record": {
        "doctype_name": "NileGov Payment Record",
        "forbidden_labels": [
            "production payment",
            "real payment",
            "real clearance",
            "live pesapal",
            "live payment gateway",
            "real money",
            "live mobile money",
        ],
        "required_disclaimer_words": ["simulated", "not process real", "sandbox"],
        "must_not_claim": ["live payment processing", "real money"],
        "linked_fields": ["service_request", "citizen_profile"],
    },
    "nilegov_escalation_record": {
        "doctype_name": "NileGov Escalation Record",
        "forbidden_labels": [
            "live ministry escalation",
            "live mda",
            "official escalation system",
        ],
        "required_disclaimer_words": ["prototype", "simulated"],
        "must_not_claim": [],
        "linked_fields": ["service_request"],
    },
    "nilegov_reporting_snapshot": {
        "doctype_name": "NileGov Reporting Snapshot",
        "forbidden_labels": [
            "official government statistics",
            "live government reporting",
            "official nira metrics",
            "official performance statistics produced",
            "production analytics",
        ],
        "required_disclaimer_words": ["prototype", "fictional", "not official government statistics"],
        "must_not_claim": ["official government statistics"],
        "linked_fields": [],
    },
}

# Reporting snapshot must NOT have official stats claim (even in non-comment content)
REPORTING_BANNED_CLAIMS = [
    "these are official",
    "live government",
    "production data",
]

# Escalation Record — no whitelisted methods exist in the controller (verified in audit)
# So frappe.call must not appear in the escalation JS
ESCALATION_HAS_NO_WHITELIST = True

# Known whitelisted methods in evidence/payment/escalation controllers (0 each)
# If new ones are added in future, add them here to keep tests accurate.
EVIDENCE_WHITELISTED: set = set()
PAYMENT_WHITELISTED: set = set()
ESCALATION_WHITELISTED: set = set()
SNAPSHOT_WHITELISTED: set = set()

EXTERNAL_URL_PATTERN = re.compile(r'https?://(?!localhost|127\.0\.0\.1)', re.IGNORECASE)
SECRET_PATTERN = re.compile(
    r'process\.env\.|os\.environ|SECRET_KEY\s*=|API_KEY\s*=\s*["\']|CONSUMER_KEY\s*=',
    re.IGNORECASE
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _js(folder):
    path = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.js")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _non_comment(content):
    """Strip // comment lines."""
    return "\n".join(
        line for line in content.splitlines()
        if not line.strip().startswith("//")
    )


def _remove_negating_phrases(content):
    """Remove 'no live X' / 'not official' negating phrases before checking for forbidden strings."""
    content = re.sub(r'\bno live (nira|ura|ughub|payment|registry|pesapal|mobile money|payment gateway)\b', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\bnot process real\b', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\bnot official government statistics\b', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\bnot official\b', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\bnot live\b', '', content, flags=re.IGNORECASE)
    return content


# ─────────────────────────────────────────────────────────────────────────────
# 1. JS files exist and are non-empty
# ─────────────────────────────────────────────────────────────────────────────
class TestJSFilesExist:
    @pytest.mark.parametrize("folder", list(TARGET_DOCTYPE_INFO.keys()))
    def test_js_file_exists(self, folder):
        path = os.path.join(DOCTYPE_ROOT, folder, f"{folder}.js")
        assert os.path.isfile(path), (
            f"JS helper file not found: {path}\n"
            f"Pass 11B-4B requires {folder}.js to exist."
        )

    @pytest.mark.parametrize("folder", list(TARGET_DOCTYPE_INFO.keys()))
    def test_js_file_is_non_empty(self, folder):
        content = _js(folder)
        assert len(content.strip()) > 100, (
            f"{folder}.js is too short — likely empty or stub."
        )

    @pytest.mark.parametrize("folder,info", list(TARGET_DOCTYPE_INFO.items()))
    def test_js_registers_correct_doctype(self, folder, info):
        content = _js(folder)
        expected = f"frappe.ui.form.on('{info['doctype_name']}'"
        assert expected in content, (
            f"{folder}.js must register frappe.ui.form.on for '{info['doctype_name']}'. "
            f"Found content does not contain: {expected}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Each JS has prototype/simulated/sandbox disclaimer
# ─────────────────────────────────────────────────────────────────────────────
class TestJSDisclaimerPresent:
    @pytest.mark.parametrize("folder,info", list(TARGET_DOCTYPE_INFO.items()))
    def test_js_has_required_disclaimer_words(self, folder, info):
        content = _js(folder).lower()
        for word in info["required_disclaimer_words"]:
            assert word.lower() in content, (
                f"{folder}.js must contain disclaimer word/phrase '{word}' "
                f"(found in set_intro or comment)."
            )

    @pytest.mark.parametrize("folder", list(TARGET_DOCTYPE_INFO.keys()))
    def test_js_uses_set_intro_for_banner(self, folder):
        content = _js(folder)
        assert "set_intro" in content or "msgprint" in content, (
            f"{folder}.js must display a user-visible prototype banner via set_intro or msgprint."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 3. No forbidden live integration labels (in non-comment, non-negating content)
# ─────────────────────────────────────────────────────────────────────────────
class TestJSNoForbiddenLabels:
    @pytest.mark.parametrize("folder,info", list(TARGET_DOCTYPE_INFO.items()))
    def test_no_forbidden_labels(self, folder, info):
        raw = _non_comment(_js(folder)).lower()
        cleaned = _remove_negating_phrases(raw)
        for label in info["forbidden_labels"]:
            assert label.lower() not in cleaned, (
                f"{folder}.js contains forbidden label '{label}' "
                f"(after stripping comment lines and negating phrases)."
            )


# ─────────────────────────────────────────────────────────────────────────────
# 4. No external URLs
# ─────────────────────────────────────────────────────────────────────────────
class TestJSNoExternalURLs:
    @pytest.mark.parametrize("folder", list(TARGET_DOCTYPE_INFO.keys()))
    def test_no_external_urls(self, folder):
        content = _js(folder)
        matches = EXTERNAL_URL_PATTERN.findall(content)
        assert not matches, (
            f"{folder}.js contains external URL references: {matches}"
        )

    @pytest.mark.parametrize("folder", list(TARGET_DOCTYPE_INFO.keys()))
    def test_no_xmlhttprequest(self, folder):
        content = _js(folder)
        assert "XMLHttpRequest" not in content, (
            f"{folder}.js must not use XMLHttpRequest directly."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. No .env / secrets
# ─────────────────────────────────────────────────────────────────────────────
class TestJSNoSecrets:
    @pytest.mark.parametrize("folder", list(TARGET_DOCTYPE_INFO.keys()))
    def test_no_env_references(self, folder):
        content = _js(folder)
        assert "process.env." not in content, (
            f"{folder}.js must not reference process.env.*"
        )

    @pytest.mark.parametrize("folder", list(TARGET_DOCTYPE_INFO.keys()))
    def test_no_hardcoded_secrets(self, folder):
        content = _js(folder)
        matches = re.findall(
            r'(?i)(api_key|secret_key|consumer_key|password)\s*[=:]\s*["\'][^"\']{4,}',
            content
        )
        assert not matches, (
            f"{folder}.js contains hardcoded secret-like values: {matches}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Evidence JS — no official verification claims
# ─────────────────────────────────────────────────────────────────────────────
class TestEvidenceJSSafety:
    FOLDER = "nilegov_evidence_document"

    def test_no_official_nira_claim(self):
        content = _non_comment(_js(self.FOLDER)).lower()
        cleaned = _remove_negating_phrases(content)
        assert "official nira" not in cleaned, (
            "Evidence JS must not claim official NIRA verification."
        )

    def test_no_official_police_claim(self):
        content = _non_comment(_js(self.FOLDER)).lower()
        assert "official police" not in content

    def test_has_verification_status_indicator(self):
        content = _js(self.FOLDER)
        assert "verification_status" in content, (
            "Evidence JS must use verification_status for status indicator."
        )

    def test_no_frappe_call(self):
        content = _js(self.FOLDER)
        assert "frappe.call" not in content, (
            "Evidence JS has no whitelisted methods — frappe.call must not appear."
        )

    def test_navigates_to_service_request(self):
        content = _js(self.FOLDER)
        assert "NileGov Service Request" in content, (
            "Evidence JS must include navigation to NileGov Service Request."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 7. Payment JS — no production payment or real clearance claims
# ─────────────────────────────────────────────────────────────────────────────
class TestPaymentJSSafety:
    FOLDER = "nilegov_payment_record"

    def test_no_production_payment_claim(self):
        content = _non_comment(_js(self.FOLDER)).lower()
        cleaned = _remove_negating_phrases(content)
        assert "production payment" not in cleaned, (
            "Payment JS must not claim production payment."
        )

    def test_no_real_clearance_claim(self):
        content = _non_comment(_js(self.FOLDER)).lower()
        assert "real clearance" not in content

    def test_has_payment_status_indicator(self):
        content = _js(self.FOLDER)
        assert "payment_status" in content, (
            "Payment JS must use payment_status for status indicator."
        )

    def test_has_simulated_wording(self):
        content = _js(self.FOLDER).lower()
        assert "simulated" in content, (
            "Payment JS must clearly say this is a simulated payment."
        )

    def test_no_frappe_call(self):
        content = _js(self.FOLDER)
        assert "frappe.call" not in content, (
            "Payment JS has no whitelisted methods — frappe.call must not appear."
        )

    def test_shows_amount_and_currency(self):
        content = _js(self.FOLDER)
        assert "doc.amount" in content and "doc.currency" in content, (
            "Payment JS should display amount and currency in the context summary."
        )

    def test_navigates_to_service_request(self):
        content = _js(self.FOLDER)
        assert "NileGov Service Request" in content


# ─────────────────────────────────────────────────────────────────────────────
# 8. Reporting Snapshot JS — no official statistics claims
# ─────────────────────────────────────────────────────────────────────────────
class TestReportingSnapshotJSSafety:
    FOLDER = "nilegov_reporting_snapshot"

    def test_no_official_statistics_claim(self):
        content = _non_comment(_js(self.FOLDER)).lower()
        cleaned = _remove_negating_phrases(content)
        for claim in REPORTING_BANNED_CLAIMS:
            assert claim.lower() not in cleaned, (
                f"Reporting Snapshot JS contains forbidden claim: '{claim}'"
            )

    def test_has_prototype_disclaimer_wording(self):
        content = _js(self.FOLDER).lower()
        assert "not official government statistics" in content or \
               "fictional" in content, (
            "Reporting Snapshot JS must state metrics are not official government statistics."
        )

    def test_has_metric_summary(self):
        content = _js(self.FOLDER)
        assert "total_requests" in content, (
            "Reporting Snapshot JS must display total_requests in the summary."
        )
        assert "overdue_count" in content, (
            "Reporting Snapshot JS must display overdue_count in the summary."
        )

    def test_has_disclaimer_field_reinforcement(self):
        content = _js(self.FOLDER)
        assert "disclaimer" in content, (
            "Reporting Snapshot JS must reference the disclaimer field."
        )

    def test_no_frappe_call(self):
        content = _js(self.FOLDER)
        assert "frappe.call" not in content, (
            "Reporting Snapshot JS has no whitelisted methods — frappe.call must not appear."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 9. Escalation JS — no unknown backend calls
# ─────────────────────────────────────────────────────────────────────────────
class TestEscalationJSSafety:
    FOLDER = "nilegov_escalation_record"

    def test_no_frappe_call(self):
        """Escalation controller has no whitelisted methods; JS must not call backend."""
        content = _js(self.FOLDER)
        assert "frappe.call" not in content, (
            "Escalation JS has no whitelisted methods — frappe.call must not appear. "
            "Use the Service Request Supervisor Actions instead."
        )

    def test_has_status_indicator(self):
        content = _js(self.FOLDER)
        assert "status" in content, (
            "Escalation JS must display the escalation status."
        )

    def test_navigates_to_service_request(self):
        content = _js(self.FOLDER)
        assert "NileGov Service Request" in content, (
            "Escalation JS must include navigation to NileGov Service Request."
        )

    def test_supervisor_actions_redirect_message(self):
        content = _js(self.FOLDER)
        assert "Supervisor Actions" in content, (
            "Escalation JS should reference Supervisor Actions group to guide users."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 10. Navigation uses frappe.set_route (safe)
# ─────────────────────────────────────────────────────────────────────────────
class TestJSNavigationSafety:
    FOLDERS_WITH_SR_NAV = [
        "nilegov_evidence_document",
        "nilegov_payment_record",
        "nilegov_escalation_record",
    ]

    @pytest.mark.parametrize("folder", FOLDERS_WITH_SR_NAV)
    def test_navigation_uses_set_route(self, folder):
        content = _js(folder)
        assert "frappe.set_route" in content, (
            f"{folder}.js must use frappe.set_route for navigation (safe, no HTTP call)."
        )

    def test_snapshot_has_list_navigation(self):
        content = _js("nilegov_reporting_snapshot")
        assert "frappe.set_route" in content, (
            "Reporting Snapshot JS must use frappe.set_route for the all-snapshots list button."
        )

    @pytest.mark.parametrize("folder", FOLDERS_WITH_SR_NAV)
    def test_navigation_links_to_valid_doctypes(self, folder):
        content = _js(folder)
        # All frappe.set_route calls should reference known NileGov DocTypes
        route_pattern = re.compile(r"frappe\.set_route\s*\(\s*['\"](?:Form|List)['\"],\s*['\"]([^'\"]+)['\"]")
        targets = route_pattern.findall(content)
        valid_doctypes = {
            "NileGov Service Request",
            "NileGov Citizen Profile",
            "NileGov Reporting Snapshot",
        }
        for target in targets:
            assert target in valid_doctypes, (
                f"{folder}.js navigates to unknown DocType '{target}'. "
                f"Must be one of: {sorted(valid_doctypes)}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# 11. Status indicator uses existing fields
# ─────────────────────────────────────────────────────────────────────────────
class TestJSFieldGuards:
    def test_evidence_uses_verification_status(self):
        content = _js("nilegov_evidence_document")
        assert "doc.verification_status" in content

    def test_payment_uses_payment_status(self):
        content = _js("nilegov_payment_record")
        assert "doc.payment_status" in content

    def test_payment_uses_verification_status(self):
        content = _js("nilegov_payment_record")
        assert "doc.verification_status" in content

    def test_escalation_uses_status(self):
        content = _js("nilegov_escalation_record")
        assert "doc.status" in content

    def test_snapshot_uses_total_requests(self):
        content = _js("nilegov_reporting_snapshot")
        assert "doc.total_requests" in content

    def test_snapshot_uses_overdue_count(self):
        content = _js("nilegov_reporting_snapshot")
        assert "doc.overdue_count" in content

    def test_snapshot_uses_escalated_count(self):
        content = _js("nilegov_reporting_snapshot")
        assert "doc.escalated_count" in content


# ─────────────────────────────────────────────────────────────────────────────
# 12. Payment amount display uses simulated wording
# ─────────────────────────────────────────────────────────────────────────────
class TestPaymentAmountDisplay:
    def test_amount_displayed_as_simulated(self):
        content = _js("nilegov_payment_record")
        # The amount display string should explicitly say "(simulated)"
        assert "simulated" in content.lower(), (
            "Payment amount display must be labelled as simulated."
        )

    def test_payment_js_has_sandbox_keyword(self):
        content = _js("nilegov_payment_record").lower()
        assert "sandbox" in content, (
            "Payment JS must include 'sandbox' wording to clarify non-production context."
        )
