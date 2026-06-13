import frappe
from frappe import _
from frappe.query_builder.functions import Count, Sum, Extract
import json

def validate_insights_access():
    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in roles and "NileGov Administrator" not in roles and "M&E Viewer" not in roles:
        frappe.throw(_("Not permitted to view Insights Data"), frappe.PermissionError)

from frappe.utils.data import getdate

COMMAND_CENTRE_OPEN_STATUSES = [
    "Submitted",
    "Under Review",
    "Information Required",
    "Payment Pending",
    "Payment Verified",
    "Approved",
    "Ready for Collection",
]

COMMAND_CENTRE_PAYMENT_SUCCESS_STATUSES = [
    "Verified",
    "Paid",
    "Successful",
    "Completed",
]

COMMAND_CENTRE_PAYMENT_PENDING_STATUSES = [
    "Pending",
    "Pending Verification",
    "Pending Reconciliation",
]

COMMAND_CENTRE_PAYMENT_FAILED_STATUSES = [
    "Failed",
    "Rejected",
    "Cancelled",
]

COMMAND_CENTRE_ESCALATION_OPEN_STATUSES = [
    "Pending",
    "Open",
    "Unresolved",
]

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

    # Base query for Service Request counts
    q_req = apply_filters(frappe.qb.from_(req).select(
        Count(req.name).as_("total"),
        Sum(frappe.qb.terms.Case().when(req.internal_status == "Closed", 1).else_(0)).as_("completed"),
        Sum(frappe.qb.terms.Case().when(req.internal_status == "Submitted", 1).else_(0)).as_("pending"),
        Sum(frappe.qb.terms.Case().when(req.internal_status.isin(COMMAND_CENTRE_OPEN_STATUSES), 1).else_(0)).as_("active_backlog"),
        Sum(frappe.qb.terms.Case().when(req.internal_status == "Rejected", 1).else_(0)).as_("rejected"),
        Sum(frappe.qb.terms.Case().when(req.sla_state == "Overdue", 1).else_(0)).as_("sla_breaches")
    ), filters)

    result = q_req.run(as_dict=True)[0]

    # Escalations
    esc = frappe.qb.DocType("NileGov Escalation Record")
    q_esc = apply_filters(frappe.qb.from_(req).inner_join(esc).on(esc.service_request == req.name).select(
        Count(esc.name).as_("escalated")
    ).where(esc.status.isin(COMMAND_CENTRE_ESCALATION_OPEN_STATUSES)), filters)
    esc_result = q_esc.run(as_dict=True)
    result["escalated"] = esc_result[0].escalated if esc_result and esc_result[0].escalated else 0

    # Payments
    pay = frappe.qb.DocType("NileGov Payment Record")
    q_pay = apply_filters(frappe.qb.from_(req).inner_join(pay).on(pay.service_request == req.name).select(
        Sum(frappe.qb.terms.Case().when(pay.payment_status.isin(COMMAND_CENTRE_PAYMENT_SUCCESS_STATUSES), pay.amount).else_(0)).as_("total_payments_collected"),
        Sum(frappe.qb.terms.Case().when(pay.payment_status.isin(COMMAND_CENTRE_PAYMENT_PENDING_STATUSES) | pay.reconciliation_status.isin(COMMAND_CENTRE_PAYMENT_PENDING_STATUSES), 1).else_(0)).as_("pending_payments_count"),
        Sum(frappe.qb.terms.Case().when(pay.payment_status.isin(COMMAND_CENTRE_PAYMENT_FAILED_STATUSES), 1).else_(0)).as_("failed_payments_count")
    ), filters)
    pay_result = q_pay.run(as_dict=True)

    for k, v in result.items():
        if v is None:
            result[k] = 0

    total = result["total"] or 0
    breaches = result["sla_breaches"] or 0
    compliance = 100
    if total > 0:
        compliance = round(((total - breaches) / total) * 100, 1)

    result["sla_compliance"] = compliance

    # Calculate in_progress
    active_backlog = result["active_backlog"] or 0
    pending = result["pending"] or 0
    result["in_progress"] = active_backlog - pending
    result["active_backlog"] = active_backlog

    if pay_result and pay_result[0]:
        result["total_payments_collected"] = pay_result[0].total_payments_collected or 0
        result["pending_payments_count"] = pay_result[0].pending_payments_count or 0
        result["failed_payments_count"] = pay_result[0].failed_payments_count or 0
    else:
        result["total_payments_collected"] = 0
        result["pending_payments_count"] = 0
        result["failed_payments_count"] = 0

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
    ).where(req.internal_status.isin(COMMAND_CENTRE_OPEN_STATUSES)).orderby(req.creation).limit(10), filters)
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
    esc = frappe.qb.DocType("NileGov Escalation Record")

    # Breaches by service
    breach_q = apply_filters(frappe.qb.from_(req).select(
        req.service_type,
        Count(req.name).as_("count")
    ).where(req.sla_state == "Overdue").groupby(req.service_type), filters)

    # Escalations by status
    esc_status_q = apply_filters(frappe.qb.from_(req).inner_join(esc).on(esc.service_request == req.name).select(
        esc.status.as_("escalation_status"),
        Count(esc.name).as_("count")
    ).where(esc.status.isnotnull()).groupby(esc.status), filters)

    # Oldest escalations
    esc_table_q = apply_filters(frappe.qb.from_(req).inner_join(esc).on(esc.service_request == req.name).select(
        esc.name,
        req.service_type,
        esc.status.as_("escalation_status"),
        esc.creation.as_("escalated_at"),
        req.assigned_officer,
        req.assigned_department
    ).where(esc.status.isin(COMMAND_CENTRE_ESCALATION_OPEN_STATUSES)).orderby(esc.creation).limit(10), filters)

    oldest_escalations = esc_table_q.run(as_dict=True)

    for row in oldest_escalations:
        row["assigned_officer"] = row.get("assigned_officer") or row.get("assigned_department") or "Unassigned"

    return {
        "breaches_by_service": breach_q.run(as_dict=True),
        "escalations_by_status": esc_status_q.run(as_dict=True),
        "oldest_escalations": oldest_escalations
    }

@frappe.whitelist()
def get_payment_reconciliation_analytics(filters=None):
    validate_insights_access()
    req = frappe.qb.DocType("NileGov Service Request")
    pay = frappe.qb.DocType("NileGov Payment Record")

    status_q = apply_filters(frappe.qb.from_(req).inner_join(pay).on(pay.service_request == req.name).select(
        pay.payment_status.as_("status"),
        Count(pay.name).as_("count"),
        Sum(pay.amount).as_("total_value")
    ).where(pay.payment_status.isnotnull()).groupby(pay.payment_status), filters)

    failed_q = apply_filters(frappe.qb.from_(req).inner_join(pay).on(pay.service_request == req.name).select(
        pay.name,
        req.service_type,
        pay.payment_status.as_("status"),
        pay.amount.as_("payment_amount"),
        pay.creation,
        pay.modified.as_("failed_at")
    ).where(pay.payment_status.isin(COMMAND_CENTRE_PAYMENT_FAILED_STATUSES)).orderby(pay.creation, order=frappe.qb.desc).limit(10), filters)

    pending_q = apply_filters(frappe.qb.from_(req).inner_join(pay).on(pay.service_request == req.name).select(
        pay.name,
        req.service_type,
        pay.payment_status.as_("status"),
        pay.amount.as_("payment_amount"),
        pay.creation
    ).where(pay.payment_status.isin(COMMAND_CENTRE_PAYMENT_PENDING_STATUSES) | pay.reconciliation_status.isin(COMMAND_CENTRE_PAYMENT_PENDING_STATUSES)).orderby(pay.creation).limit(10), filters)

    status_data = status_q.run(as_dict=True)
    return {
        "status_summary": status_data,
        "payment_status_summary": status_data,
        "failed_payments": failed_q.run(as_dict=True),
        "pending_payments": pending_q.run(as_dict=True)
    }

@frappe.whitelist()
def get_officer_workload_analytics(filters=None):
    validate_insights_access()
    req = frappe.qb.DocType("NileGov Service Request")

    workload_q = apply_filters(frappe.qb.from_(req).select(
        req.assigned_officer,
        req.assigned_department,
        Sum(frappe.qb.terms.Case().when(req.internal_status.isin(COMMAND_CENTRE_OPEN_STATUSES), 1).else_(0)).as_("active_cases"),
        Sum(frappe.qb.terms.Case().when(req.internal_status == "Closed", 1).else_(0)).as_("completed_cases"),
        Sum(frappe.qb.terms.Case().when(req.sla_state == "Overdue", 1).else_(0)).as_("breached_cases")
    ).groupby(req.assigned_officer, req.assigned_department).orderby("active_cases", order=frappe.qb.desc), filters)

    raw_rows = workload_q.run(as_dict=True)
    grouped = {}

    for row in raw_rows:
        owner = row.get("assigned_officer") or row.get("assigned_department") or "Unassigned"

        if owner not in grouped:
            grouped[owner] = {
                "assigned_officer": owner,
                "active_cases": 0,
                "completed_cases": 0,
                "breached_cases": 0,
            }

        grouped[owner]["active_cases"] += int(row.get("active_cases") or 0)
        grouped[owner]["completed_cases"] += int(row.get("completed_cases") or 0)
        grouped[owner]["breached_cases"] += int(row.get("breached_cases") or 0)

    officer_workload = sorted(
        grouped.values(),
        key=lambda item: item.get("active_cases") or 0,
        reverse=True,
    )

    return {
        "officer_workload": officer_workload
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
    validate_insights_access()
    return {"policy_performance": []}

COMMAND_CENTRE_STATUS_FALLBACKS = [
    "Submitted",
    "Pending",
    "In Progress",
    "Under Review",
    "Approved",
    "Rejected",
    "Closed",
    "Escalated",
]

def _dedupe(values):
    seen = set()
    result = []
    for value in values:
        if value is None:
            continue
        clean_value = str(value).strip()
        if not clean_value or clean_value in seen:
            continue
        seen.add(clean_value)
        result.append(clean_value)
    return result

def _get_status_options(req):
    statuses = frappe.qb.from_(req).select(req.internal_status).distinct().where(req.internal_status.isnotnull()).run(as_dict=True)
    opts = _dedupe([s.internal_status for s in statuses])
    return opts or COMMAND_CENTRE_STATUS_FALLBACKS

def _get_location_options(req=None):
    try:
        if not frappe.db.exists("DocType", "NileGov District"):
            return []

        return frappe.get_all(
            "NileGov District",
            filters={"disabled": 0},
            pluck="district_name",
            order_by="district_name asc",
        )
    except Exception:
        return []

def _clean_label(value):
    if value is None:
        return ""
    return " ".join(str(value).strip().split())

def _service_label_key(value):
    return _clean_label(value).casefold()

def _append_service_option(service_options, seen_labels, value, label):
    clean_value = _clean_label(value)
    clean_label = _clean_label(label)

    if not clean_value or not clean_label:
        return

    label_key = _service_label_key(clean_label)
    if label_key in seen_labels:
        return

    seen_labels.add(label_key)
    service_options.append({
        "value": clean_value,
        "label": clean_label,
    })

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
    seen_labels = set()

    if catalogue_services:
        for service in catalogue_services:
            if service.get("active_status") == "Inactive":
                continue

            value = service.get("service_code") or service.get("name")
            label = service.get("service_name") or service.get("service_code") or service.get("name")

            _append_service_option(service_options, seen_labels, value, label)
    else:
        # 2. Fallback to distinct service types from requests
        services = frappe.qb.from_(req).select(req.service_type).distinct().where(
            (req.service_type.isnotnull()) & (req.service_type != '')
        ).run(as_dict=True)

        for service in services:
            value = service.get("service_type")
            _append_service_option(service_options, seen_labels, value, value)

    officers = frappe.qb.from_(req).select(req.assigned_officer).distinct().where(req.assigned_officer.isnotnull()).run(as_dict=True)

    return {
        "services": service_options,
        "locations": _get_location_options(req),
        "officers": _dedupe([o.assigned_officer for o in officers]),
        "statuses": _get_status_options(req)
    }
