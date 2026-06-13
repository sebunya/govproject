import frappe

SERVICE_TYPES = [
    {
        "service_name": "Birth Certificate",
        "service_code": "BIRTH_CERTIFICATE",
        "description": "Civil registration service for birth certificate requests.",
        "default_sla_hours": 96,
        "requires_identity_check": 1,
        "requires_payment": 1,
        "requires_supporting_documents": 1,
        "is_active": 1
    },
    {
        "service_name": "Business Permit",
        "service_code": "BUSINESS_PERMIT",
        "description": "Local government business permit application service.",
        "default_sla_hours": 120,
        "requires_identity_check": 1,
        "requires_payment": 1,
        "requires_supporting_documents": 1,
        "is_active": 1
    },
    {
        "service_name": "Land Search",
        "service_code": "LAND_SEARCH",
        "description": "Land and property search information request service.",
        "default_sla_hours": 168,
        "requires_identity_check": 1,
        "requires_payment": 1,
        "requires_supporting_documents": 1,
        "is_active": 1
    },
    {
        "service_name": "Tax Clearance",
        "service_code": "TAX_CLEARANCE",
        "description": "Tax clearance support and verification service.",
        "default_sla_hours": 72,
        "requires_identity_check": 1,
        "requires_payment": 0,
        "requires_supporting_documents": 1,
        "is_active": 1
    },
    {
        "service_name": "Agricultural Permit",
        "service_code": "AGRICULTURAL_PERMIT",
        "description": "Agricultural permit application service for district-level processing.",
        "default_sla_hours": 120,
        "requires_identity_check": 1,
        "requires_payment": 1,
        "requires_supporting_documents": 1,
        "is_active": 1
    },
    {
        "service_name": "Driving Permit Renewal",
        "service_code": "DRIVING_PERMIT_RENEWAL",
        "description": "Driving permit renewal support service.",
        "default_sla_hours": 72,
        "requires_identity_check": 1,
        "requires_payment": 1,
        "requires_supporting_documents": 1,
        "is_active": 1
    },
    {
        "service_name": "Passport Support",
        "service_code": "PASSPORT_SUPPORT",
        "description": "Passport application support and follow-up service.",
        "default_sla_hours": 168,
        "requires_identity_check": 1,
        "requires_payment": 1,
        "requires_supporting_documents": 1,
        "is_active": 1
    },
    {
        "service_name": "Social Protection Registration",
        "service_code": "SOCIAL_PROTECTION_REGISTRATION",
        "description": "Social protection registration service for equity and inclusion analytics.",
        "default_sla_hours": 144,
        "requires_identity_check": 1,
        "requires_payment": 0,
        "requires_supporting_documents": 1,
        "is_active": 1
    },
    {
        "service_name": "Local Government Letter",
        "service_code": "LOCAL_GOVERNMENT_LETTER",
        "description": "District-level local government letter request service.",
        "default_sla_hours": 96,
        "requires_identity_check": 1,
        "requires_payment": 1,
        "requires_supporting_documents": 0,
        "is_active": 1
    }
]

SLA_RULES = [
    {
        "sla_rule_id": "SLA-BIRTH-CERTIFICATE",
        "service_type": "BIRTH_CERTIFICATE",
        "response_hours": 24,
        "resolution_hours": 96,
        "at_risk_threshold_percent": 80,
        "escalation_threshold_hours": 4,
        "active": 1
    },
    {
        "sla_rule_id": "SLA-BUSINESS-PERMIT",
        "service_type": "BUSINESS_PERMIT",
        "response_hours": 24,
        "resolution_hours": 120,
        "at_risk_threshold_percent": 75,
        "escalation_threshold_hours": 6,
        "active": 1
    },
    {
        "sla_rule_id": "SLA-LAND-SEARCH",
        "service_type": "LAND_SEARCH",
        "response_hours": 48,
        "resolution_hours": 168,
        "at_risk_threshold_percent": 85,
        "escalation_threshold_hours": 12,
        "active": 1
    },
    {
        "sla_rule_id": "SLA-TAX-CLEARANCE",
        "service_type": "TAX_CLEARANCE",
        "response_hours": 12,
        "resolution_hours": 72,
        "at_risk_threshold_percent": 80,
        "escalation_threshold_hours": 2,
        "active": 1
    },
    {
        "sla_rule_id": "SLA-AGRICULTURAL-PERMIT",
        "service_type": "AGRICULTURAL_PERMIT",
        "response_hours": 24,
        "resolution_hours": 120,
        "at_risk_threshold_percent": 80,
        "escalation_threshold_hours": 8,
        "active": 1
    },
    {
        "sla_rule_id": "SLA-DRIVING-PERMIT-RENEWAL",
        "service_type": "DRIVING_PERMIT_RENEWAL",
        "response_hours": 12,
        "resolution_hours": 72,
        "at_risk_threshold_percent": 80,
        "escalation_threshold_hours": 2,
        "active": 1
    },
    {
        "sla_rule_id": "SLA-PASSPORT-SUPPORT",
        "service_type": "PASSPORT_SUPPORT",
        "response_hours": 48,
        "resolution_hours": 168,
        "at_risk_threshold_percent": 90,
        "escalation_threshold_hours": 12,
        "active": 1
    },
    {
        "sla_rule_id": "SLA-SOCIAL-PROTECTION-REGISTRATION",
        "service_type": "SOCIAL_PROTECTION_REGISTRATION",
        "response_hours": 24,
        "resolution_hours": 144,
        "at_risk_threshold_percent": 80,
        "escalation_threshold_hours": 8,
        "active": 1
    },
    {
        "sla_rule_id": "SLA-LOCAL-GOVERNMENT-LETTER",
        "service_type": "LOCAL_GOVERNMENT_LETTER",
        "response_hours": 24,
        "resolution_hours": 96,
        "at_risk_threshold_percent": 80,
        "escalation_threshold_hours": 4,
        "active": 1
    }
]

SERVICE_CATALOGUE = [
    {
        "service_catalogue_id": "CAT-BIRTH-CERTIFICATE",
        "service_name": "Birth Certificate",
        "service_code": "BIRTH_CERTIFICATE",
        "service_category": "Identity Services",
        "service_description": "Civil registration service for birth certificate requests.",
        "fee_required": 1,
        "default_fee_amount": 10000,
        "default_sla_rule": "SLA-BIRTH-CERTIFICATE",
        "active_status": "Demo Only",
        "public_visibility": "Demo Visible"
    },
    {
        "service_catalogue_id": "CAT-BUSINESS-PERMIT",
        "service_name": "Business Permit",
        "service_code": "BUSINESS_PERMIT",
        "service_category": "Permit Applications",
        "service_description": "Local government business permit application service.",
        "fee_required": 1,
        "default_fee_amount": 50000,
        "default_sla_rule": "SLA-BUSINESS-PERMIT",
        "active_status": "Demo Only",
        "public_visibility": "Demo Visible"
    },
    {
        "service_catalogue_id": "CAT-LAND-SEARCH",
        "service_name": "Land Search",
        "service_code": "LAND_SEARCH",
        "service_category": "Information Requests",
        "service_description": "Land and property search information request service.",
        "fee_required": 1,
        "default_fee_amount": 25000,
        "default_sla_rule": "SLA-LAND-SEARCH",
        "active_status": "Demo Only",
        "public_visibility": "Demo Visible"
    },
    {
        "service_catalogue_id": "CAT-TAX-CLEARANCE",
        "service_name": "Tax Clearance",
        "service_code": "TAX_CLEARANCE",
        "service_category": "Other Government Services",
        "service_description": "Tax clearance support and verification service.",
        "fee_required": 0,
        "default_fee_amount": 0,
        "default_sla_rule": "SLA-TAX-CLEARANCE",
        "active_status": "Demo Only",
        "public_visibility": "Demo Visible"
    },
    {
        "service_catalogue_id": "CAT-AGRICULTURAL-PERMIT",
        "service_name": "Agricultural Permit",
        "service_code": "AGRICULTURAL_PERMIT",
        "service_category": "Permit Applications",
        "service_description": "Agricultural permit application service for district-level processing.",
        "fee_required": 1,
        "default_fee_amount": 20000,
        "default_sla_rule": "SLA-AGRICULTURAL-PERMIT",
        "active_status": "Demo Only",
        "public_visibility": "Demo Visible"
    },
    {
        "service_catalogue_id": "CAT-DRIVING-PERMIT-RENEWAL",
        "service_name": "Driving Permit Renewal",
        "service_code": "DRIVING_PERMIT_RENEWAL",
        "service_category": "Permit Applications",
        "service_description": "Driving permit renewal support service.",
        "fee_required": 1,
        "default_fee_amount": 60000,
        "default_sla_rule": "SLA-DRIVING-PERMIT-RENEWAL",
        "active_status": "Demo Only",
        "public_visibility": "Demo Visible"
    },
    {
        "service_catalogue_id": "CAT-PASSPORT-SUPPORT",
        "service_name": "Passport Support",
        "service_code": "PASSPORT_SUPPORT",
        "service_category": "Identity Services",
        "service_description": "Passport application support and follow-up service.",
        "fee_required": 1,
        "default_fee_amount": 75000,
        "default_sla_rule": "SLA-PASSPORT-SUPPORT",
        "active_status": "Demo Only",
        "public_visibility": "Demo Visible"
    },
    {
        "service_catalogue_id": "CAT-SOCIAL-PROTECTION-REGISTRATION",
        "service_name": "Social Protection Registration",
        "service_code": "SOCIAL_PROTECTION_REGISTRATION",
        "service_category": "Other Government Services",
        "service_description": "Social protection registration service for equity and inclusion analytics.",
        "fee_required": 0,
        "default_fee_amount": 0,
        "default_sla_rule": "SLA-SOCIAL-PROTECTION-REGISTRATION",
        "active_status": "Demo Only",
        "public_visibility": "Demo Visible"
    },
    {
        "service_catalogue_id": "CAT-LOCAL-GOVERNMENT-LETTER",
        "service_name": "Local Government Letter",
        "service_code": "LOCAL_GOVERNMENT_LETTER",
        "service_category": "Information Requests",
        "service_description": "District-level local government letter request service.",
        "fee_required": 1,
        "default_fee_amount": 5000,
        "default_sla_rule": "SLA-LOCAL-GOVERNMENT-LETTER",
        "active_status": "Demo Only",
        "public_visibility": "Demo Visible"
    }
]

def execute():
    ensure_service_types()
    ensure_sla_rules()
    ensure_service_catalogue()

def ensure_service_types():
    for st in SERVICE_TYPES:
        if not frappe.db.exists("NileGov Service Type", st["service_code"]):
            doc = frappe.new_doc("NileGov Service Type")
            doc.update(st)
            doc.insert(ignore_permissions=True)

def ensure_sla_rules():
    for rule in SLA_RULES:
        if not frappe.db.exists("NileGov SLA Rule", rule["sla_rule_id"]):
            doc = frappe.new_doc("NileGov SLA Rule")
            doc.update(rule)
            doc.insert(ignore_permissions=True)

def ensure_service_catalogue():
    for cat in SERVICE_CATALOGUE:
        if not frappe.db.exists("NileGov Service Catalogue", cat["service_catalogue_id"]):
            doc = frappe.new_doc("NileGov Service Catalogue")
            doc.update(cat)
            doc.insert(ignore_permissions=True)
