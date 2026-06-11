import frappe
from frappe import _
from frappe.query_builder.functions import Count, Sum, Extract
import json

def validate_insights_access():
    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in roles and "NileGov Administrator" not in roles and "M&E Viewer" not in roles:
        frappe.throw(_("Not permitted to view Insights Data"), frappe.PermissionError)

from frappe.utils.data import getdate

def apply_filters(query, filters):
    if not filters:
        return query

    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except (json.JSONDecodeError, TypeError):
            filters = {}

    req = frappe.qb.DocType("NileGov Service Request")

    if filters.get("from_date"):
        try:
            query = query.where(req.creation >= getdate(filters.get("from_date")))
        except Exception:
            pass
    if filters.get("to_date"):
        try:
            query = query.where(req.creation <= getdate(filters.get("to_date")))
        except Exception:
            pass
    if filters.get("service_type"):
        query = query.where(req.service_type == filters.get("service_type"))
    if filters.get("status"):
        query = query.where(req.internal_status == filters.get("status"))
    if filters.get("location"):
        query = query.where(req.location == filters.get("location"))
    if filters.get("officer"):
        query = query.where(req.assigned_officer == filters.get("officer"))

    return query

@frappe.whitelist()
def get_command_centre_overview(filters=None):
    validate_insights_access()
    req = frappe.qb.DocType("NileGov Service Request")

    # Base query for all records
    q_all = apply_filters(frappe.qb.from_(req).select(
        Count(req.name).as_("total"),
        Sum(frappe.qb.terms.Case().when(req.internal_status == "Closed", 1).else_(0)).as_("completed"),
        Sum(frappe.qb.terms.Case().when(req.internal_status == "Pending", 1).else_(0)).as_("pending"),
        Sum(frappe.qb.terms.Case().when(req.internal_status == "In Progress", 1).else_(0)).as_("in_progress"),
        Sum(frappe.qb.terms.Case().when(req.internal_status == "Rejected", 1).else_(0)).as_("rejected"),
        Sum(frappe.qb.terms.Case().when(req.sla_state == "Overdue", 1).else_(0)).as_("sla_breaches"),
        Sum(frappe.qb.terms.Case().when(req.escalation_status == "Pending", 1).else_(0)).as_("escalated"),
        Sum(frappe.qb.terms.Case().when(req.payment_status == "Paid", req.payment_amount).else_(0)).as_("total_payments_collected"),
        Sum(frappe.qb.terms.Case().when(req.payment_status == "Pending", 1).else_(0)).as_("pending_payments_count"),
        Sum(frappe.qb.terms.Case().when(req.payment_status == "Failed", 1).else_(0)).as_("failed_payments_count")
    ), filters)

    result = q_all.run(as_dict=True)[0]

    # Defaults for None
    for k, v in result.items():
        if v is None:
            result[k] = 0

    total = result["total"] or 0
    breaches = result["sla_breaches"] or 0
    compliance = 100
    if total > 0:
        compliance = round(((total - breaches) / total) * 100, 1)

    result["sla_compliance"] = compliance
    result["active_backlog"] = result["pending"] + result["in_progress"]

    return result

@frappe.whitelist()
def get_service_delivery_analytics(filters=None):
    validate_insights_access()
    req = frappe.qb.DocType("NileGov Service Request")

    # 1. Service demand trend (by month)
    trend_q = apply_filters(frappe.qb.from_(req).select(
        Extract("month", req.creation).as_("month"),
        Extract("year", req.creation).as_("year"),
        Count(req.name).as_("count")
    ).groupby("year", "month").orderby("year", "month"), filters)
    trend_data = trend_q.run(as_dict=True)

    # 2. Requests by service type
    type_q = apply_filters(frappe.qb.from_(req).select(
        req.service_type,
        Count(req.name).as_("count")
    ).groupby(req.service_type), filters)
    type_data = type_q.run(as_dict=True)

    # 3. Requests by status
    status_q = apply_filters(frappe.qb.from_(req).select(
        req.internal_status,
        Count(req.name).as_("count")
    ).groupby(req.internal_status), filters)
    status_data = status_q.run(as_dict=True)

    # 4. Oldest pending backlog (drill down)
    backlog_q = apply_filters(frappe.qb.from_(req).select(
        req.name, req.service_type, req.creation, req.location, req.internal_status, req.assigned_officer
    ).where(req.internal_status.isin(["Pending", "In Progress"])).orderby(req.creation).limit(10), filters)
    backlog_data = backlog_q.run(as_dict=True)

    return {
        "trend": trend_data,
        "by_type": type_data,
        "by_status": status_data,
        "oldest_backlog": backlog_data
    }

@frappe.whitelist()
def get_sla_risk_analytics(filters=None):
    validate_insights_access()
    req = frappe.qb.DocType("NileGov Service Request")

    # Breaches by service
    breach_q = apply_filters(frappe.qb.from_(req).select(
        req.service_type,
        Count(req.name).as_("count")
    ).where(req.sla_state == "Overdue").groupby(req.service_type), filters)

    # Escalations by status
    esc_status_q = apply_filters(frappe.qb.from_(req).select(
        req.escalation_status,
        Count(req.name).as_("count")
    ).where(req.escalation_status.isnotnull()).groupby(req.escalation_status), filters)

    # Oldest escalations
    esc_table_q = apply_filters(frappe.qb.from_(req).select(
        req.name, req.service_type, req.escalation_status, req.escalated_at, req.assigned_officer
    ).where(req.escalation_status == "Pending").orderby(req.escalated_at).limit(10), filters)

    return {
        "breaches_by_service": breach_q.run(as_dict=True),
        "escalations_by_status": esc_status_q.run(as_dict=True),
        "oldest_escalations": esc_table_q.run(as_dict=True)
    }

@frappe.whitelist()
def get_payment_reconciliation_analytics(filters=None):
    validate_insights_access()
    req = frappe.qb.DocType("NileGov Service Request")

    status_q = apply_filters(frappe.qb.from_(req).select(
        req.payment_status,
        Count(req.name).as_("count"),
        Sum(req.payment_amount).as_("total_value")
    ).where(req.payment_status.isnotnull()).groupby(req.payment_status), filters)

    failed_q = apply_filters(frappe.qb.from_(req).select(
        req.name, req.service_type, req.payment_status, req.payment_amount, req.creation
    ).where(req.payment_status == "Failed").orderby(req.creation, order=frappe.qb.desc).limit(10), filters)

    pending_q = apply_filters(frappe.qb.from_(req).select(
        req.name, req.service_type, req.payment_status, req.payment_amount, req.creation
    ).where(req.payment_status == "Pending").orderby(req.creation).limit(10), filters)

    return {
        "status_summary": status_q.run(as_dict=True),
        "failed_payments": failed_q.run(as_dict=True),
        "pending_payments": pending_q.run(as_dict=True)
    }

@frappe.whitelist()
def get_officer_workload_analytics(filters=None):
    validate_insights_access()
    req = frappe.qb.DocType("NileGov Service Request")

    workload_q = apply_filters(frappe.qb.from_(req).select(
        req.assigned_officer,
        Sum(frappe.qb.terms.Case().when(req.internal_status.isin(["Pending", "In Progress"]), 1).else_(0)).as_("active_cases"),
        Sum(frappe.qb.terms.Case().when(req.internal_status == "Closed", 1).else_(0)).as_("completed_cases"),
        Sum(frappe.qb.terms.Case().when(req.sla_state == "Overdue", 1).else_(0)).as_("breached_cases")
    ).where(req.assigned_officer.isnotnull()).groupby(req.assigned_officer).orderby("active_cases", order=frappe.qb.desc), filters)

    return {
        "officer_workload": workload_q.run(as_dict=True)
    }

@frappe.whitelist()
def get_location_performance_analytics(filters=None):
    validate_insights_access()
    req = frappe.qb.DocType("NileGov Service Request")

    loc_q = apply_filters(frappe.qb.from_(req).select(
        req.location,
        Count(req.name).as_("total_requests"),
        Sum(frappe.qb.terms.Case().when(req.sla_state == "Overdue", 1).else_(0)).as_("breaches")
    ).where(req.location.isnotnull()).groupby(req.location).orderby("total_requests", order=frappe.qb.desc), filters)

    return {
        "location_performance": loc_q.run(as_dict=True)
    }

@frappe.whitelist()
def get_policy_me_summary(filters=None):
    # Safe stub returning empty dict if no direct M&E metrics fit outside of what's already covered.
    validate_insights_access()
    return {}

@frappe.whitelist()
def get_command_centre_filters():
    validate_insights_access()
    req = frappe.qb.DocType("NileGov Service Request")
    cat = frappe.qb.DocType("NileGov Service Catalogue")

    # 1. Try Service Catalogue first
    catalogue_services = frappe.get_all(
        "NileGov Service Catalogue",
        fields=["name", "service_name", "service_code", "active_status"],
        ignore_permissions=True
    )

    service_options = []
    if catalogue_services:
        for s in catalogue_services:
            if s.get("active_status") == "Inactive":
                continue
            val = s.get("service_code") or s.get("name")
            lbl = s.get("service_name") or s.get("service_code") or s.get("name")
            if val:
                service_options.append({"value": val, "label": lbl})
    else:
        # 2. Fallback to distinct service types from requests
        services = frappe.qb.from_(req).select(req.service_type).distinct().where(
            (req.service_type.isnotnull()) & (req.service_type != '')
        ).run(as_dict=True)
        for s in services:
            val = s.get("service_type")
            if val:
                service_options.append({"value": val, "label": val})

    locations = frappe.qb.from_(req).select(req.location).distinct().where(req.location.isnotnull()).run(as_dict=True)
    officers = frappe.qb.from_(req).select(req.assigned_officer).distinct().where(req.assigned_officer.isnotnull()).run(as_dict=True)
    statuses = frappe.qb.from_(req).select(req.internal_status).distinct().where(req.internal_status.isnotnull()).run(as_dict=True)

    return {
        "services": service_options,
        "locations": [l.location for l in locations],
        "officers": [o.assigned_officer for o in officers],
        "statuses": [s.internal_status for s in statuses]
    }
