# Pass 11B-6D: Assignment Rule Definitions — Static Architecture Tests
# Digi-Verse Uganda Limited
# Prototype simulation only. No live queue routing or official government MDA queue integration.
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
ASSIGNMENT_RULE_ROOT = os.path.join(INNER_APP, "assignment_rule")
HOOKS_PATH = os.path.join(OUTER_PACKAGE, "hooks.py")

EXPECTED_ASSIGNMENT_RULES = {
    "nilegov_submitted_request_queue_assignment": {
        "name": "NileGov Submitted Request Queue Assignment",
        "document_type": "NileGov Service Request",
        "assign_to_role": "NileGov Citizen Officer",
        "priority": 1,
    },
    "nilegov_evidence_review_assignment": {
        "name": "NileGov Evidence Review Assignment",
        "document_type": "NileGov Evidence Document",
        "assign_to_role": "NileGov Records Officer",
        "priority": 1,
    },
    "nilegov_payment_review_assignment": {
        "name": "NileGov Payment Review Assignment",
        "document_type": "NileGov Payment Record",
        "assign_to_role": "NileGov Payments Officer",
        "priority": 1,
    },
    "nilegov_sla_at_risk_supervisor_assignment": {
        "name": "NileGov SLA At Risk Supervisor Assignment",
        "document_type": "NileGov Service Request",
        "assign_to_role": "NileGov SLA Supervisor",
        "priority": 2,
    },
    "nilegov_sla_overdue_supervisor_assignment": {
        "name": "NileGov SLA Overdue Supervisor Assignment",
        "document_type": "NileGov Service Request",
        "assign_to_role": "NileGov SLA Supervisor",
        "priority": 3,
    },
    "nilegov_escalation_review_assignment": {
        "name": "NileGov Escalation Review Assignment",
        "document_type": "NileGov Escalation Record",
        "assign_to_role": "NileGov SLA Supervisor",
        "priority": 1,
    },
    "nilegov_closure_review_assignment": {
        "name": "NileGov Closure Review Assignment",
        "document_type": "NileGov Service Request",
        "assign_to_role": "NileGov SLA Supervisor",
        "priority": 1,
    },
}

KNOWN_ROLES = {
    "NileGov Citizen Officer",
    "NileGov Records Officer",
    "NileGov Payments Officer",
    "NileGov SLA Supervisor",
    "NileGov M&E Viewer",
    "NileGov MDA Admin",
    "NileGov System Auditor",
    "NileGov System Manager",
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _load_assignment_rule_json(folder):
    path = os.path.join(ASSIGNMENT_RULE_ROOT, folder, f"{folder}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────
class TestAssignmentRuleFilesExist:
    @pytest.mark.parametrize("folder", list(EXPECTED_ASSIGNMENT_RULES.keys()))
    def test_assignment_rule_json_exists(self, folder):
        path = os.path.join(ASSIGNMENT_RULE_ROOT, folder, f"{folder}.json")
        assert os.path.isfile(path), f"Assignment Rule JSON not found: {path}"

class TestAssignmentRuleJSONValidity:
    REQUIRED_KEYS = {"name", "document_type", "doctype", "assign_condition", "rule", "priority", "is_standard", "assign_to_role"}

    @pytest.mark.parametrize("folder", list(EXPECTED_ASSIGNMENT_RULES.keys()))
    def test_assignment_rule_json_is_valid(self, folder):
        doc = _load_assignment_rule_json(folder)
        assert isinstance(doc, dict), f"{folder}.json must be a JSON object"

    @pytest.mark.parametrize("folder", list(EXPECTED_ASSIGNMENT_RULES.keys()))
    def test_assignment_rule_has_required_keys(self, folder):
        doc = _load_assignment_rule_json(folder)
        for key in self.REQUIRED_KEYS:
            assert key in doc, f"{folder}.json missing required key: '{key}'"

    @pytest.mark.parametrize("folder,info", list(EXPECTED_ASSIGNMENT_RULES.items()))
    def test_assignment_rule_metadata_matches(self, folder, info):
        doc = _load_assignment_rule_json(folder)
        assert doc["name"] == info["name"], f"{folder} name mismatch"
        assert doc["name"].startswith("NileGov"), f"{folder} name must start with 'NileGov'"
        assert doc["document_type"] == info["document_type"], f"{folder} document_type mismatch"
        assert doc["doctype"] == "Assignment Rule", f"{folder} doctype mismatch"
        assert doc["is_standard"] == 1, f"{folder} is_standard mismatch"
        assert doc["priority"] == info["priority"], f"{folder} priority mismatch"
        assert doc["assign_to_role"] == info["assign_to_role"], f"{folder} assign_to_role mismatch"
        assert doc["assign_to_role"] in KNOWN_ROLES, f"{folder} uses unknown role: '{doc['assign_to_role']}'"

    @pytest.mark.parametrize("folder", list(EXPECTED_ASSIGNMENT_RULES.keys()))
    def test_no_sensitive_data_in_assignment_rules(self, folder):
        doc = _load_assignment_rule_json(folder)
        desc = (doc.get("description") or "").lower()
        cond = (doc.get("assign_condition") or "").lower()
        
        # Ensure no emails
        assert "@" not in desc, f"{folder} contains email in description"
        assert "@" not in cond, f"{folder} contains email in condition"
        
        # Ensure prototype disclaimer in description
        assert "prototype" in desc or "simulated" in desc or "assign" in desc, f"{folder} missing description / disclaimer"

class TestHooksFixturesAssignmentRule:
    def test_hooks_lists_all_7_assignment_rules(self):
        with open(HOOKS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert '"dt": "Assignment Rule"' in content or "'dt': 'Assignment Rule'" in content
        
        for folder, info in EXPECTED_ASSIGNMENT_RULES.items():
            name = info["name"]
            assert name in content, f"hooks.py fixtures does not include assignment rule: '{name}'"
