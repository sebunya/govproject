# Frappe-based SLA Rule Repository
# Prototype simulation only. No live Government registry access.

try:
    import frappe
except ImportError:
    frappe = None

from typing import Optional, List
from nilegov_stack.application.ports import SLARuleRepository
from nilegov_stack.domain.sla import SLARule


class FrappeSLARuleRepository(SLARuleRepository):
    """Frappe-based repository for persisting and loading SLA Rule aggregates."""

    def _check_frappe(self):
        if not frappe:
            raise ImportError("Frappe framework is not loaded in this environment.")

    def save(self, rule: SLARule) -> None:
        self._check_frappe()

        # Load or create document
        if frappe.db.exists("NileGov SLA Rule", rule.rule_id):
            doc = frappe.get_doc("NileGov SLA Rule", rule.rule_id)
        else:
            doc = frappe.new_doc("NileGov SLA Rule")
            doc.sla_rule_id = rule.rule_id

        doc.service_type = rule.service_type
        doc.response_hours = rule.response_hours
        doc.resolution_hours = rule.resolution_hours
        doc.at_risk_threshold_percent = rule.at_risk_threshold_percent
        doc.escalation_threshold_hours = rule.escalation_threshold_hours
        doc.escalation_queue = rule.escalation_queue
        doc.escalation_role = rule.escalation_role
        doc.notes = rule.notes
        doc.disclaimer = rule.disclaimer
        doc.active = 1 if rule.active else 0

        doc.save(ignore_permissions=True)
        frappe.db.commit()

    def get_by_id(self, rule_id: str) -> Optional[SLARule]:
        self._check_frappe()
        if not frappe.db.exists("NileGov SLA Rule", rule_id):
            return None

        doc = frappe.get_doc("NileGov SLA Rule", rule_id)
        return self._map_doc_to_aggregate(doc)

    def get_by_service_type(self, service_type: str) -> Optional[SLARule]:
        self._check_frappe()
        rules = frappe.get_all(
            "NileGov SLA Rule",
            filters={"service_type": service_type, "active": 1},
            pluck="name"
        )
        if not rules:
            return None
        return self.get_by_id(rules[0])

    def get_all(self) -> List[SLARule]:
        self._check_frappe()
        rule_ids = frappe.get_all("NileGov SLA Rule", pluck="name")
        results = []
        for rid in rule_ids:
            rule = self.get_by_id(rid)
            if rule:
                results.append(rule)
        return results

    def _map_doc_to_aggregate(self, doc) -> SLARule:
        return SLARule(
            rule_id=doc.sla_rule_id or doc.name,
            service_type=doc.service_type,
            response_hours=doc.response_hours,
            resolution_hours=doc.resolution_hours,
            at_risk_threshold_percent=doc.at_risk_threshold_percent or 80,
            escalation_threshold_hours=doc.escalation_threshold_hours or 2,
            escalation_queue=doc.escalation_queue or "Supervisor Review Queue",
            escalation_role=doc.escalation_role or "supervisor_demo",
            notes=doc.notes,
            disclaimer=doc.disclaimer,
            active=bool(doc.active)
        )
