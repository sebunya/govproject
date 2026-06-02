# Idempotent Service Types & SLA Rules Seeding Patch
# Prototype simulation only. No live Government registry access.

import frappe

def execute():
    """Idempotently inserts default service types and SLA rules into the database."""
    
    # 1. Seed Service Type
    service_code = "LOST_NATIONAL_ID"
    if not frappe.db.exists("NileGov Service Type", service_code):
        service = frappe.new_doc("NileGov Service Type")
        service.service_name = "Lost National ID / Replacement Service Request"
        service.service_code = service_code
        service.description = "Prototype replacement requests for lost or damaged National Identification Cards."
        service.default_sla_hours = 48
        service.requires_identity_check = 1
        service.requires_payment = 0
        service.requires_supporting_documents = 1
        service.is_active = 1
        service.insert(ignore_permissions=True)
        frappe.db.commit()

    # 2. Seed SLA Rule linked to the Service Type
    rule_id = "SLA-LOST-NID"
    if not frappe.db.exists("NileGov SLA Rule", rule_id):
        rule = frappe.new_doc("NileGov SLA Rule")
        rule.sla_rule_id = rule_id
        rule.service_type = service_code
        rule.response_hours = 4
        rule.resolution_hours = 48
        rule.at_risk_threshold_percent = 80
        rule.escalation_threshold_hours = 2
        rule.escalation_queue = "Supervisor Review Queue"
        rule.escalation_role = "supervisor_demo"
        rule.active = 1
        rule.notes = "Seeded SLA rule for Lost National ID replacement requests."
        rule.disclaimer = "Prototype simulation only. No live Government registry access."
        rule.insert(ignore_permissions=True)
        frappe.db.commit()
