# Idempotent Demo Records Seeding Patch
# Prototype simulation only. No live Government registry access.

import frappe
import random
import json
from frappe.utils import get_datetime, add_to_date
from nilegov_stack.utils.synthetic_identities import (
    DEMO_BATCH_ID,
    generate_synthetic_name,
    get_demo_email,
    get_demo_phone,
    get_demo_zone,
    generate_officer_names
)

# Deterministic seed for consistency across idempotency runs if limit isn't used
random.seed(42)

def validate_schema():
    """Ensure all required DocTypes are installed and warn about optional ones."""
    required = [
        "NileGov Service Type", "NileGov Service Catalogue", "NileGov SLA Rule",
        "NileGov Citizen Profile", "NileGov Service Request", "NileGov Consent Record",
        "NileGov Evidence Document", "NileGov Citizen Notification", "NileGov Payment Record",
        "NileGov Reporting Snapshot", "NileGov SLA Event",
        "NileGov Escalation Record", "NileGov Simulated Identity Verification", "NileGov Audit Event",
        "NileGov Management Review Note", "User"
    ]
    optional = [
        "NileGov Integration Simulation Log", "NileGov Integration Log"
    ]
    
    missing_required = []
    for dt in required:
        if not frappe.db.table_exists(dt):
            missing_required.append(dt)
            
    if missing_required:
        frappe.throw(f"Missing required DocTypes: {missing_required}")
        
    available_optional = []
    skipped_optional = []
    for dt in optional:
        if frappe.db.table_exists(dt):
            available_optional.append(dt)
        else:
            skipped_optional.append(dt)
            
    if skipped_optional:
        print(f"Warning: Skipping optional DocTypes not found in schema: {skipped_optional}")
        
    return available_optional

def reset_demo_data(dry_run=False):
    """Deletes only records tagged with DEMO_BATCH_ID."""
    print(f"\n--- Initiating Reset for Batch: {DEMO_BATCH_ID} {'(DRY RUN)' if dry_run else ''} ---")
    
    # Dependency-safe order
    doctypes_to_reset = [
        "NileGov Citizen Notification",
        "NileGov Audit Event",
        "NileGov Integration Simulation Log",
        "NileGov Escalation Record",
        "NileGov SLA Event",
        "NileGov Payment Record",
        "NileGov Simulated Identity Verification",
        "NileGov Evidence Document",
        "NileGov Consent Record",
        "NileGov Service Request",
        "NileGov Citizen Profile",
        "NileGov Reporting Snapshot",
        "NileGov Management Review Note",
        "NileGov Service Catalogue"
    ]

    total_deleted = 0
    for dt in doctypes_to_reset:
        try:
            # Check if there is a disclaimer or remarks field that holds our batch ID
            # All demo data in Nilegov is seeded with disclaimer containing DEMO_BATCH_ID, except requests where we might put it in closure_notes or a similar text field. 
            # To be robust, let's query standard name patterns since they are DEMO-prefixed.
            prefix = get_prefix_for_doctype(dt)
            if not prefix:
                continue

            records = frappe.get_all(dt, filters={"name": ("like", f"{prefix}%")}, pluck="name", limit=10000)
            
            if dry_run:
                print(f"Would delete {len(records)} records from {dt}")
                total_deleted += len(records)
                continue
                
            count = 0
            for record in records:
                frappe.delete_doc(dt, record, force=True, ignore_permissions=True)
                count += 1
            if count > 0:
                print(f"Deleted {count} records from {dt}")
            total_deleted += count
        except Exception as e:
            print(f"Warning: Could not reset {dt}: {str(e)}")

    if not dry_run:
        frappe.db.commit()
    print(f"Total records {'planned for deletion' if dry_run else 'deleted'}: {total_deleted}")

def get_prefix_for_doctype(dt):
    mapping = {
        "NileGov Citizen Profile": "DEMO-CIT-2026-",
        "NileGov Service Request": "DEMO-REQ-2026-",
        "NileGov Consent Record": "DEMO-CON-2026-",
        "NileGov Evidence Document": "DEMO-EVD-2026-",
        "NileGov Citizen Notification": "DEMO-NOTIF-2026-",
        "NileGov Payment Record": "DEMO-PAY-2026-",
        "NileGov SLA Event": "DEMO-SLA-2026-",
        "NileGov Escalation Record": "DEMO-ESC-2026-",
        "NileGov Simulated Identity Verification": "DEMO-IDV-2026-",
        "NileGov Audit Event": "DEMO-AUD-2026-",
        "NileGov Integration Simulation Log": "DEMO-INT-2026-",
        "NileGov Reporting Snapshot": "DEMO-SNAP-2026-",
        "NileGov Management Review Note": "DEMO-REV-2026-"
    }
    return mapping.get(dt)

def create_users(dry_run=False):
    officers = generate_officer_names(5)
    officer_usernames = []
    
    for i, name in enumerate(officers):
        username = f"officer_demo_{i+1}"
        email = get_demo_email(name, i+1, is_staff=True)
        
        if not frappe.db.exists("User", email):
            user = frappe.new_doc("User")
            user.email = email
            user.first_name = name.split()[0]
            user.last_name = " ".join(name.split()[1:])
            user.username = username
            user.name = email
            user.enabled = 1
            user.send_welcome_email = 0
            if dry_run:
                if hasattr(user, 'validate'): user.validate()
            else:
                user.insert(ignore_permissions=True)
            if not dry_run:
                user.add_roles("NileGov Citizen Officer", "NileGov SLA Supervisor", "NileGov M&E Viewer", "NileGov System Auditor")
            frappe.db.commit()
        officer_usernames.append(email)
        
    return officer_usernames

def run(dry_run=False, reset=False, limit=None):
    """Main execution entry point."""
    if reset:
        reset_demo_data(dry_run=dry_run)
        
    available_optional = validate_schema()
    
    print(f"\n--- Initiating Generation for Batch: {DEMO_BATCH_ID} {'(DRY RUN)' if dry_run else ''} ---")
    
    # Adjust scale depending on limit, default is ~3500 items via ratios
    # Ratios
    target_profiles = 200 if limit is None else limit
    target_requests = target_profiles * 2
    
    counts = {
        "NileGov Service Catalogue": 3,
        "NileGov Citizen Profile": target_profiles,
        "NileGov Service Request": target_requests,
        "NileGov Consent Record": int(target_requests * 0.8),
        "NileGov Evidence Document": int(target_requests * 1.5),
        "NileGov Simulated Identity Verification": int(target_requests * 0.9),
        "NileGov Payment Record": int(target_requests * 0.9),
        "NileGov SLA Event": int(target_requests * 1.2),
        "NileGov Escalation Record": int(target_requests * 0.2),
        "NileGov Citizen Notification": int(target_requests * 1.5),
        "NileGov Audit Event": int(target_requests * 2.0)
    }
    
    if "NileGov Integration Simulation Log" in available_optional:
        counts["NileGov Integration Simulation Log"] = int(target_requests * 0.5)
    else:
        # Compensate volume through other DocTypes
        counts["NileGov Audit Event"] += int(target_requests * 0.25)
        counts["NileGov Citizen Notification"] += int(target_requests * 0.25)

    counts["NileGov Reporting Snapshot"] = 12
    counts["NileGov Management Review Note"] = 6
    
    if dry_run:
        print("Performing Dry-Run Validation on generated records...")

    # 1. Create Users
    officers = create_users(dry_run=dry_run)
    
    inserted_counts = {dt: 0 for dt in counts.keys()}
    
    # 2. Service Catalogue
    catalogue_seeds = [
        {
            "id": "DEMO-SVC-LOST-NID", "code": "LOST_NATIONAL_ID", "name": "Lost National ID Replacement", 
            "fee": 50000.0, "queue": "National ID Replacement Desk", "category": "Identity Services",
            "workflow": "Replacement Request Workflow", "pay_purpose": "National ID Replacement Fee",
            "mda": "National Identification and Registration Authority"
        },
        {
            "id": "DEMO-SVC-COMPLAINT", "code": "CITIZEN_COMPLAINT", "name": "Citizen Complaint Portal", 
            "fee": 0.0, "queue": "Citizen Services Desk", "category": "Citizen Complaints",
            "workflow": "Complaint Resolution Workflow", "pay_purpose": "Not Applicable",
            "mda": "Office of the Inspector General"
        },
        {
            "id": "DEMO-SVC-PERMIT", "code": "ENVIRONMENT_PERMIT", "name": "Environmental Permit Application", 
            "fee": 250000.0, "queue": "Citizen Services Desk", "category": "Permit Applications",
            "workflow": "Standard Application Workflow", "pay_purpose": "Service Processing Fee",
            "mda": "National Environment Management Authority"
        }
    ]
    for cs in catalogue_seeds:
        if not dry_run and not frappe.db.exists("NileGov Service Type", cs["code"]):
            st_doc = frappe.new_doc("NileGov Service Type")
            st_doc.service_code = cs["code"]
            st_doc.service_name = cs["name"]
            st_doc.default_sla_hours = 48
            st_doc.insert(ignore_permissions=True)
            
        if dry_run or not frappe.db.exists("NileGov Service Catalogue", cs["id"]):
            cat_doc = frappe.new_doc("NileGov Service Catalogue")
            cat_doc.service_catalogue_id = cs["id"]
            cat_doc.service_name = cs["name"]
            cat_doc.service_code = cs["code"]
            cat_doc.responsible_mda_placeholder = cs["mda"]
            cat_doc.service_category = cs["category"]
            cat_doc.service_description = "Simulated Service for Demo purposes"
            cat_doc.fee_required = 1 if cs["fee"] > 0 else 0
            cat_doc.default_fee_amount = cs["fee"]
            cat_doc.default_currency = "UGX"
            cat_doc.default_payment_purpose = cs["pay_purpose"]
            cat_doc.default_payment_provider = "Simulated"
            cat_doc.responsible_department = "Citizen Services Department"
            cat_doc.responsible_queue = cs["queue"]
            cat_doc.workflow_template = cs["workflow"]
            cat_doc.active_status = "Active"
            cat_doc.public_visibility = "Demo Visible"
            cat_doc.disclaimer = DEMO_BATCH_ID
            
            if dry_run:
                if hasattr(cat_doc, 'validate'): cat_doc.validate()
            else:
                cat_doc.validate() if dry_run and hasattr(cat_doc, "validate") else cat_doc.insert(ignore_permissions=True) if not dry_run else None
            inserted_counts["NileGov Service Catalogue"] += 1
    frappe.db.commit()

    # 3. Citizen Profiles
    now_dt = get_datetime()
    profiles = []
    for i in range(1, target_profiles + 1):
        cp_id = f"DEMO-CIT-2026-{i:06d}"
        profiles.append({
            "id": cp_id,
            "name": generate_synthetic_name(),
            "phone": get_demo_phone(i),
            "email": get_demo_email(f"citizen{i}", i),
            "location": get_demo_zone(),
            "nin": f"DEMO-NIN-2026-{i:06d}"
        })
        if dry_run or not frappe.db.exists("NileGov Citizen Profile", cp_id):
            p = frappe.new_doc("NileGov Citizen Profile")
            p.citizen_profile_id = cp_id
            p.full_name = profiles[-1]["name"]
            p.phone = profiles[-1]["phone"]
            p.email = profiles[-1]["email"]
            p.location = profiles[-1]["location"]
            p.preferred_contact_channel = random.choice(["SMS", "Email", "WhatsApp"])
            p.status = "Active"
            p.nin = profiles[-1]["nin"]
            p.validate() if dry_run and hasattr(p, "validate") else p.validate() if dry_run and hasattr(p, "validate") else p.insert(ignore_permissions=True) if not dry_run else None if not dry_run else None
            inserted_counts["NileGov Citizen Profile"] += 1
    frappe.db.commit()

    # 4. Service Requests & related relational web
    statuses = ["Submitted", "Under Review", "Information Required", "Payment Pending", "Payment Verified", "Approved", "Ready for Collection", "Closed", "Rejected"]
    
    # We will build audit events and integration logs progressively
    audit_events_to_insert = []
    logs_to_insert = []
    
    for i in range(1, target_requests + 1):
        req_id = f"DEMO-REQ-2026-{i:06d}"
        if not dry_run and frappe.db.exists("NileGov Service Request", req_id):
            continue
            
        cp = random.choice(profiles)
        cat = random.choice(catalogue_seeds)
        
        # Age distribution: 0 to 90 days ago
        age_hours = random.randint(1, 90 * 24)
        creation_dt = add_to_date(now_dt, hours=-age_hours)
        
        status = random.choices(statuses, weights=[10, 15, 5, 10, 15, 15, 10, 15, 5])[0]
        
        # Build Request
        r = frappe.new_doc("NileGov Service Request")
        r.service_request_id = req_id
        r.reference_no = f"DEMO-REF-2026-{i:06d}"
        r.service_type = cat["code"]
        r.citizen_profile = cp["id"]
        r.citizen_full_name = cp["name"]
        r.nin = cp["nin"]
        r.phone = cp["phone"]
        r.email = cp["email"]
        r.location = cp["location"]
        r.reason_for_request = "Synthetic demo request"
        r.internal_status = status
        r.citizen_visible_status = status
        r.queue_name = cat["queue"]
        r.creation = creation_dt
        
        assigned_officer = random.choice(officers) if status != "Submitted" else None
        if assigned_officer:
            r.assignment_status = "Assigned"
            r.assigned_officer = assigned_officer
            r.assigned_at = add_to_date(creation_dt, hours=random.randint(1, 24))
        else:
            r.assignment_status = "Unassigned"
            
        # SLA Calculation
        r.response_due_at = add_to_date(creation_dt, hours=4)
        r.resolution_due_at = add_to_date(creation_dt, hours=48)
        r.sla_deadline = r.resolution_due_at
        
        overdue_hours = age_hours - 48
        if status in ["Closed", "Rejected", "Approved", "Ready for Collection"]:
            r.sla_state = "Met" if random.random() > 0.2 else "Overdue"
        elif overdue_hours > 0:
            r.sla_state = "Overdue"
            r.overdue_flag = 1
        elif overdue_hours > -12:
            r.sla_state = "At Risk"
            r.at_risk_flag = 1
        else:
            r.sla_state = "Within SLA"
            
        if status in ["Closed", "Rejected", "Resolved"]:
            r.closure_notes = "Automatically closed by demo generator"
            r.closure_date = add_to_date(creation_dt, days=3)
            r.decision = "Approved" if status != "Rejected" else "Rejected"
        r.validate() if dry_run and hasattr(r, "validate") else r.validate() if dry_run and hasattr(r, "validate") else r.insert(ignore_permissions=True) if not dry_run else None if not dry_run else None
        inserted_counts["NileGov Service Request"] += 1

        # Consent
        if random.random() > 0.2:
            con_id = f"DEMO-CON-2026-{i:06d}"
            c = frappe.new_doc("NileGov Consent Record")
            c.consent_record_id = con_id
            c.citizen_profile = cp["id"]
            c.consent_purpose = "Service Request Processing"
            c.consent_channel = "Portal"
            c.consent_status = "Granted"
            c.consent_given_by = cp["name"]
            c.consent_given_at = creation_dt
            c.validate() if dry_run and hasattr(c, "validate") else c.insert(ignore_permissions=True) if not dry_run else None
            inserted_counts["NileGov Consent Record"] += 1
            
        # Evidence
        ev_count = random.randint(1, 3)
        for e_i in range(ev_count):
            ev_id = f"DEMO-EVD-2026-{i:06d}-{e_i}"
            ev = frappe.new_doc("NileGov Evidence Document")
            ev.evidence_document_id = ev_id
            ev.citizen_profile = cp["id"]
            ev.service_request = req_id
            ev.document_type = "Other Supporting Document"
            ev.visibility = "Officer Only"
            ev.document_title = f"Document {e_i}"
            ev.file = "demo-placeholder.pdf"
            ev.upload_channel = "Portal"
            ev.uploaded_by = "Administrator"
            ev.uploaded_at = creation_dt
            
            ev_stat = random.choices(["Accepted", "Requires Replacement", "Rejected", "Under Review"], weights=[70, 10, 5, 15])[0]
            ev.verification_status = ev_stat
            if ev_stat in ["Accepted", "Rejected"]:
                ev.verified_by = assigned_officer
                ev.verified_timestamp = add_to_date(creation_dt, hours=2)
            ev.disclaimer = DEMO_BATCH_ID
            ev.validate() if dry_run and hasattr(ev, "validate") else ev.insert(ignore_permissions=True) if not dry_run else None
            inserted_counts["NileGov Evidence Document"] += 1
            
        # Identity Verification
        if random.random() > 0.1:
            idv_id = f"DEMO-IDV-2026-{i:06d}"
            idv = frappe.new_doc("NileGov Simulated Identity Verification")
            idv.verification_event_id = idv_id
            idv.citizen_profile = cp["id"]
            idv.service_request = req_id
            idv.simulated_at = creation_dt
            idv.nin = cp["nin"]
            idv.provider = "NIRA Mock"
            outcomes = ["Matched", "Partial Match", "No Match", "Service Unavailable"]
            outcome = random.choices(outcomes, weights=[80, 10, 5, 5])[0]
            idv.match_outcome = outcome
            idv.verified_at = add_to_date(creation_dt, minutes=5)
            idv.confidence_score = random.uniform(50.0, 99.9) if outcome == "Matched" else 0.0
            idv.validate() if dry_run and hasattr(idv, "validate") else idv.insert(ignore_permissions=True) if not dry_run else None
            inserted_counts["NileGov Simulated Identity Verification"] += 1

        # Payment
        if cat["fee"] > 0 and status not in ["Submitted"]:
            pay_id = f"DEMO-PAY-2026-{i:06d}"
            p = frappe.new_doc("NileGov Payment Record")
            p.payment_record_id = pay_id
            p.service_request = req_id
            p.citizen_profile = cp["id"]
            p.amount = cat["fee"]
            p.payment_purpose = cat["pay_purpose"]
            p.payment_channel = random.choice(["Simulated Mobile Money", "Simulated Card", "Simulated Bank"])
            p_stat = random.choices(["Verified", "Pending", "Failed"], weights=[80, 15, 5])[0]
            p.payment_status = p_stat
            p.simulated_transaction_reference = f"SIM-TXN-{i:06d}"
            p.verification_status = "Simulated Verified" if p_stat == "Verified" else "Not Checked"
            p.reconciliation_status = "Reconciled" if p_stat == "Verified" else "Pending Reconciliation"
            p.disclaimer = DEMO_BATCH_ID
            p.validate() if dry_run and hasattr(p, "validate") else p.validate() if dry_run and hasattr(p, "validate") else p.insert(ignore_permissions=True) if not dry_run else None if not dry_run else None
            inserted_counts["NileGov Payment Record"] += 1
            
        # SLA Events & Escalations
        if overdue_hours > -12:
            sla_id = f"DEMO-SLA-2026-{i:06d}"
            sla = frappe.new_doc("NileGov SLA Event")
            sla.sla_event_id = sla_id
            sla.service_request = req_id
            sla.event_type = "SLA Resolution Nearing" if overdue_hours <= 0 else "SLA Escalated"
            sla.due_at = r.resolution_due_at
            sla.triggered_at = add_to_date(r.resolution_due_at, hours=-4 if overdue_hours <= 0 else 1)
            sla.validate() if dry_run and hasattr(sla, "validate") else sla.insert(ignore_permissions=True) if not dry_run else None
            inserted_counts["NileGov SLA Event"] += 1
            
            if overdue_hours > 24 and random.random() > 0.5:
                esc_id = f"DEMO-ESC-2026-{i:06d}"
                esc = frappe.new_doc("NileGov Escalation Record")
                esc.escalation_record_id = esc_id
                esc.service_request = req_id
                esc.escalated_by = "Administrator"
                esc.escalated_to = random.choice(officers)
                esc.escalated_at = add_to_date(r.resolution_due_at, hours=24)
                esc.escalation_reason = "SLA Breach > 24 hours"
                esc.escalation_status = "Open" if status not in ["Closed", "Approved"] else "Resolved"
                esc.validate() if dry_run and hasattr(esc, "validate") else esc.insert(ignore_permissions=True) if not dry_run else None
                inserted_counts["NileGov Escalation Record"] += 1

        # Notifications
        notif_id = f"DEMO-NOTIF-2026-{i:06d}"
        notif = frappe.new_doc("NileGov Citizen Notification")
        notif.notification_event_id = notif_id
        notif.service_request = req_id
        notif.citizen_profile = cp["id"]
        notif.recipient = cp["phone"]
        notif.recipient_type = "Citizen"
        notif.channel = "SMS"
        notif.message_type = "Request Received" if status == "Submitted" else status
        notif.notification_type = "Status Update"
        notif.message = f"Request {req_id} status changed to {status}. {DEMO_BATCH_ID}"
        notif.delivery_status = random.choices(["Simulated Sent", "Simulated Failed", "Queued"], weights=[90, 5, 5])[0]
        notif.simulated_sent_at = creation_dt
        notif.sent_at = creation_dt
        notif.disclaimer = DEMO_BATCH_ID
        notif.validate() if dry_run and hasattr(notif, "validate") else notif.insert(ignore_permissions=True) if not dry_run else None
        inserted_counts["NileGov Citizen Notification"] += 1

        # Collect Audits and Logs for bulk insertion simulation
        audit_events_to_insert.append({
            "audit_event_id": f"DEMO-AUD-2026-{i:06d}-1",
            "service_request": req_id,
            "event_type": "Creation",
            "actor": "Administrator",
            "actor_role": "System Manager",
            "event_time": creation_dt,
            "action_summary": "Request created",
            "new_status": "Submitted"
        })
        if assigned_officer:
            audit_events_to_insert.append({
                "audit_event_id": f"DEMO-AUD-2026-{i:06d}-2",
                "service_request": req_id,
                "event_type": "Assignment",
                "actor": assigned_officer,
                "actor_role": "Officer",
                "event_time": add_to_date(creation_dt, hours=1),
                "action_summary": f"Assigned to {assigned_officer}",
                "previous_status": "Submitted",
                "new_status": "Under Review"
            })
            
        if random.random() > 0.8:
            logs_to_insert.append({
                "integration_simulation_log_id": f"DEMO-INT-2026-{i:06d}",
                "service_request": req_id,
                "integration_name": "NIRA API Integration",
                "simulation_type": "NIRA Identity Lookup",
                "status": "Success" if status != "Information Required" else "Failed",
                "simulated_at": add_to_date(creation_dt, hours=1),
                "disclaimer": "Prototype simulation only. No live Government registry access.",
                "target_system": "NIRA API Mock",
                "endpoint_called": "/verify",
                "http_status": 200 if status != "Information Required" else 500,
                "simulated_at": creation_dt,
                "status": "Success" if status != "Information Required" else "Failed"
            })
            
        if i % 50 == 0:
            frappe.db.commit()
            print(f"  Generated {i} request clusters...")

    # Insert Audits
    for au in audit_events_to_insert:
        if dry_run or not frappe.db.exists("NileGov Audit Event", au["audit_event_id"]):
            a = frappe.new_doc("NileGov Audit Event")
            a.update(au)
            a.validate() if dry_run and hasattr(a, "validate") else a.insert(ignore_permissions=True) if not dry_run else None
            inserted_counts["NileGov Audit Event"] += 1
    frappe.db.commit()

    # Insert Logs if supported
    if "NileGov Integration Simulation Log" in available_optional:
        for lg in logs_to_insert:
            if dry_run or not frappe.db.exists("NileGov Integration Simulation Log", lg["integration_simulation_log_id"]):
                l = frappe.new_doc("NileGov Integration Simulation Log")
                l.update(lg)
                l.validate() if dry_run and hasattr(l, "validate") else l.insert(ignore_permissions=True) if not dry_run else None
                inserted_counts["NileGov Integration Simulation Log"] += 1
        frappe.db.commit()

    # 5. Snapshots & Reviews
    for i in range(1, counts["NileGov Reporting Snapshot"] + 1):
        snap_id = f"DEMO-SNAP-2026-{i:03d}"
        if dry_run or not frappe.db.exists("NileGov Reporting Snapshot", snap_id):
            s = frappe.new_doc("NileGov Reporting Snapshot")
            s.reporting_snapshot_id = snap_id
            s.snapshot_name = f"Monthly Perf {i}"
            s.reporting_period_start = '2026-03-01'
            s.reporting_period_end = '2026-03-31'
            s.generated_at = '2026-03-31 23:59:59'
            s.generated_by = random.choice(officers)
            s.source_dataset = DEMO_BATCH_ID
            s.total_requests = 150
            s.total_services = 3
            s.requests_by_status = '{"Closed": 100, "Approved": 50}'
            s.requests_by_service = '{"LOST_NATIONAL_ID": 150}'
            s.requests_by_queue = '{}'
            s.requests_by_location = '{}'
            s.officer_workload_summary = '{}'
            s.payment_value_summary = '{}'
            s.disclaimer = DEMO_BATCH_ID
            s.validate() if dry_run and hasattr(s, "validate") else s.insert(ignore_permissions=True) if not dry_run else None
            inserted_counts["NileGov Reporting Snapshot"] += 1
            
    for i in range(1, counts["NileGov Management Review Note"] + 1):
        rev_id = f"DEMO-REV-2026-{i:03d}"
        if dry_run or not frappe.db.exists("NileGov Management Review Note", rev_id):
            r = frappe.new_doc("NileGov Management Review Note")
            r.review_note_id = rev_id
            r.review_title = f"Service Delivery Optimization Q{i}"
            r.review_date = get_datetime()
            r.reviewed_by = random.choice(officers)
            r.observations = f"Review notes based on {DEMO_BATCH_ID}"
            r.action_items = "Improve verification SLA"
            r.status = "Draft"
        if status in ["Closed", "Rejected", "Resolved"]:
            r.closure_notes = "Automatically closed by demo generator"
            r.closure_date = add_to_date(creation_dt, days=3)
            r.decision = "Approved" if status != "Rejected" else "Rejected"
            r.validate() if dry_run and hasattr(r, "validate") else r.validate() if dry_run and hasattr(r, "validate") else r.insert(ignore_permissions=True) if not dry_run else None if not dry_run else None
            inserted_counts["NileGov Management Review Note"] += 1
            
    frappe.db.commit()

    print("\n--- Seed Results ---")
    total_inserted = 0
    for dt, count in inserted_counts.items():
        print(f"{dt}: {count} records generated")
        total_inserted += count
    print(f"Total Demo Records Generated: {total_inserted}")
    print("--- End of Generation ---")

def execute():
    run()
