# Pass 11B-6C: Notification Definitions — Static Architecture Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live government channels/delivery.
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
NOTIFICATION_ROOT = os.path.join(INNER_APP, "notification")
HOOKS_PATH = os.path.join(OUTER_PACKAGE, "hooks.py")

EXPECTED_NOTIFICATIONS = {
    "nilegov_officer_assigned_alert": {
        "name": "NileGov Officer Assigned Alert",
        "document_type": "NileGov Service Request",
        "event": "Value Change",
        "disclaimer": "Prototype notification readiness only. No live SMS, WhatsApp or production email was sent.",
        "recipients": ["NileGov Citizen Officer"],
    },
    "nilegov_evidence_incomplete_alert": {
        "name": "NileGov Evidence Incomplete Alert",
        "document_type": "NileGov Evidence Document",
        "event": "Save",
        "disclaimer": "Prototype notification readiness only. No live SMS, WhatsApp or production email was sent.",
        "recipients": ["NileGov Records Officer"],
    },
    "nilegov_payment_pending_review_alert": {
        "name": "NileGov Payment Pending Review Alert",
        "document_type": "NileGov Payment Record",
        "event": "Save",
        "disclaimer": "Payment status is simulated/sandbox-only. No real money movement or live payment clearance is claimed.",
        "recipients": ["NileGov Payments Officer"],
    },
    "nilegov_sla_at_risk_alert": {
        "name": "NileGov SLA At Risk Alert",
        "document_type": "NileGov Service Request",
        "event": "Value Change",
        "disclaimer": "Prototype notification readiness only. No live SMS, WhatsApp or production email was sent.",
        "recipients": ["NileGov SLA Supervisor"],
    },
    "nilegov_sla_overdue_alert": {
        "name": "NileGov SLA Overdue Alert",
        "document_type": "NileGov Service Request",
        "event": "Value Change",
        "disclaimer": "Prototype notification readiness only. No live SMS, WhatsApp or production email was sent.",
        "recipients": ["NileGov SLA Supervisor"],
    },
    "nilegov_escalation_assigned_alert": {
        "name": "NileGov Escalation Assigned Alert",
        "document_type": "NileGov Escalation Record",
        "event": "New",
        "disclaimer": "Prototype notification readiness only. No live SMS, WhatsApp or production email was sent.",
        "recipients": ["NileGov SLA Supervisor"],
    },
    "nilegov_case_closed_alert": {
        "name": "NileGov Case Closed Alert",
        "document_type": "NileGov Service Request",
        "event": "Value Change",
        "disclaimer": "Prototype notification readiness only. No live SMS, WhatsApp or production email was sent.",
        "recipients": ["NileGov Citizen Officer", "NileGov M&E Viewer"],
    },
    "nilegov_simulated_citizen_status_update": {
        "name": "NileGov Simulated Citizen Status Update",
        "document_type": "NileGov Citizen Notification",
        "event": "Save",
        "disclaimer": "Citizen-facing delivery is simulated until a live notification channel is configured and approved.",
        "recipients": ["NileGov Citizen Officer"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _load_notification_json(folder):
    path = os.path.join(NOTIFICATION_ROOT, folder, f"{folder}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestNotificationFilesExist:
    @pytest.mark.parametrize("folder", list(EXPECTED_NOTIFICATIONS.keys()))
    def test_notification_json_exists(self, folder):
        path = os.path.join(NOTIFICATION_ROOT, folder, f"{folder}.json")
        assert os.path.isfile(path), f"Notification JSON not found: {path}"

class TestNotificationJSONValidity:
    REQUIRED_KEYS = {"name", "document_type", "doctype", "module", "is_standard", "message", "recipients"}

    @pytest.mark.parametrize("folder", list(EXPECTED_NOTIFICATIONS.keys()))
    def test_notification_json_is_valid(self, folder):
        doc = _load_notification_json(folder)
        assert isinstance(doc, dict), f"{folder}.json must be a JSON object"

    @pytest.mark.parametrize("folder", list(EXPECTED_NOTIFICATIONS.keys()))
    def test_notification_has_required_keys(self, folder):
        doc = _load_notification_json(folder)
        for key in self.REQUIRED_KEYS:
            assert key in doc, f"{folder}.json missing required key: '{key}'"

    @pytest.mark.parametrize("folder,info", list(EXPECTED_NOTIFICATIONS.items()))
    def test_notification_metadata_matches(self, folder, info):
        doc = _load_notification_json(folder)
        assert doc["name"] == info["name"], f"{folder} name mismatch"
        assert doc["name"].startswith("NileGov"), f"{folder} name must start with 'NileGov'"
        assert doc["document_type"] == info["document_type"], f"{folder} document_type mismatch"
        assert doc["doctype"] == "Notification", f"{folder} doctype mismatch"
        assert doc["module"] == "NileGov Stack", f"{folder} module mismatch"
        assert doc["is_standard"] == 1, f"{folder} is_standard mismatch"
        assert doc["event"] == info["event"], f"{folder} event mismatch"

    @pytest.mark.parametrize("folder,info", list(EXPECTED_NOTIFICATIONS.items()))
    def test_notification_recipients(self, folder, info):
        doc = _load_notification_json(folder)
        recipients = doc["recipients"]
        assert isinstance(recipients, list), f"{folder} recipients must be a list"
        
        roles_in_doc = []
        for r in recipients:
            assert r.get("doctype") == "Notification Recipient"
            assert r.get("receiver_type") == "By Role"
            role = r.get("receiver_by_role")
            assert role.startswith("NileGov"), f"Recipient role '{role}' in {folder} must start with 'NileGov'"
            roles_in_doc.append(role)
            
        for expected_role in info["recipients"]:
            assert expected_role in roles_in_doc, f"Expected role '{expected_role}' not found in {folder} recipients"

class TestNotificationSafety:
    @pytest.mark.parametrize("folder,info", list(EXPECTED_NOTIFICATIONS.items()))
    def test_notification_message_has_disclaimer(self, folder, info):
        doc = _load_notification_json(folder)
        msg = doc.get("message") or ""
        assert info["disclaimer"] in msg, f"{folder} message missing required disclaimer: '{info['disclaimer']}'"

class TestHooksFixturesNotification:
    def test_hooks_lists_all_8_notifications(self):
        with open(HOOKS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert '"dt": "Notification"' in content or "'dt': 'Notification'" in content
        
        for folder, info in EXPECTED_NOTIFICATIONS.items():
            name = info["name"]
            assert name in content, f"hooks.py fixtures does not include notification: '{name}'"
