# Idempotent Demo Records Seeding Patch
# Prototype simulation only. No live Government registry access.

import frappe
from frappe.utils import get_datetime, add_to_date

def execute():
    """Idempotently seeds User, Profiles and Service Requests for Pass 3 browser demo validation."""
    
    # 1. Seed Officer User
    officer_user = "officer_demo"
    officer_email = "officer.demo@example.test"
    if not frappe.db.exists("User", officer_user):
        user = frappe.new_doc("User")
        user.email = officer_email
        user.first_name = "Officer"
        user.last_name = "Demo"
        user.username = officer_user
        user.enabled = 1
        user.send_welcome_email = 0
        user.insert(ignore_permissions=True)
        
        # Add Service Desk Officer role
        user.add_roles("NileGov Citizen Officer")  # Pass 11B-2: canonical role
        frappe.db.commit()

    # Seed Officer Review User
    if not frappe.db.exists("User", "officer_review"):
        user = frappe.new_doc("User")
        user.email = "officer.review@example.test"
        user.first_name = "Officer"
        user.last_name = "Review"
        user.username = "officer_review"
        user.enabled = 1
        user.send_welcome_email = 0
        user.insert(ignore_permissions=True)
        user.add_roles("NileGov Citizen Officer")  # Pass 11B-2: canonical role
        frappe.db.commit()

    # Seed Supervisor Demo User
    if not frappe.db.exists("User", "supervisor_demo"):
        user = frappe.new_doc("User")
        user.email = "supervisor.demo@example.test"
        user.first_name = "Supervisor"
        user.last_name = "Demo"
        user.username = "supervisor_demo"
        user.enabled = 1
        user.send_welcome_email = 0
        user.insert(ignore_permissions=True)
        user.add_roles("NileGov SLA Supervisor")  # Pass 11B-2: canonical role
        frappe.db.commit()

    # Ensure service type exists
    service_code = "LOST_NATIONAL_ID"
    if not frappe.db.exists("NileGov Service Type", service_code):
        return
        
    demo_scenarios = [
        {
            "id": "req_pass3_001",
            "ref": "NGS-NIRA-2026-0001",
            "profile_id": "CP-001",
            "nin": "CF900000000000",
            "name": "Demo Citizen A",
            "phone": "+256700000001",
            "email": "demo.citizen.a@example.test",
            "location": "Ntinda, Kampala",
            "status": "Submitted",
            "payment_status": "Not Required",
            "identity_status": "Requires Review",
            "sla_overdue": False,
            "channel": "Phone",
            "profile_status": "Active"
        },
        {
            "id": "req_pass3_002",
            "ref": "NGS-NIRA-2026-0002",
            "profile_id": "CP-002",
            "nin": "CF900000000001",
            "name": "Demo Citizen B",
            "phone": "+256700000002",
            "email": "demo.citizen.b@example.test",
            "location": "Bukoto, Kampala",
            "status": "Under Review",
            "payment_status": "Not Required",
            "identity_status": "Matched",
            "sla_overdue": False,
            "channel": "Email",
            "profile_status": "Active"
        },
        {
            "id": "req_pass3_003",
            "ref": "NGS-NIRA-2026-0003",
            "profile_id": "CP-003",
            "nin": "CF900000000002",
            "name": "Demo Citizen C",
            "phone": "+256700000003",
            "email": "demo.citizen.c@example.test",
            "location": "Ntinda, Kampala",
            "status": "Information Required",
            "payment_status": "Not Required",
            "identity_status": "Requires Review",
            "sla_overdue": False,
            "channel": "SMS",
            "profile_status": "Demo Only"
        },
        {
            "id": "req_pass3_004",
            "ref": "NGS-NIRA-2026-0004",
            "profile_id": "CP-004",
            "nin": None,
            "name": "Demo Citizen D",
            "phone": "+256700000004",
            "email": "demo.citizen.d@example.test",
            "location": "Ntinda, Kampala",
            "status": "Payment Pending",
            "payment_status": "Pending",
            "identity_status": "Matched",
            "sla_overdue": False,
            "channel": "WhatsApp",
            "profile_status": "Active"
        },
        {
            "id": "req_pass3_005",
            "ref": "NGS-NIRA-2026-0005",
            "profile_id": "CP-005",
            "nin": "CF900000000004",
            "name": "Demo Citizen E",
            "phone": "+256700000005",
            "email": "demo.citizen.e@example.test",
            "location": "Ntinda, Kampala",
            "status": "Payment Verified",
            "payment_status": "Verified",
            "identity_status": "Matched",
            "sla_overdue": False,
            "channel": "Phone",
            "profile_status": "Active"
        },
        {
            "id": "req_pass3_006",
            "ref": "NGS-NIRA-2026-0006",
            "profile_id": "CP-006",
            "nin": "CF900000000005",
            "name": "Demo Citizen F",
            "phone": "+256700000006",
            "email": "demo.citizen.f@example.test",
            "location": "Ntinda, Kampala",
            "status": "Approved",
            "payment_status": "Verified",
            "identity_status": "Matched",
            "sla_overdue": False,
            "channel": "Phone",
            "profile_status": "Active"
        },
        {
            "id": "req_pass3_007",
            "ref": "NGS-NIRA-2026-0007",
            "profile_id": "CP-007",
            "nin": "CF900000000006",
            "name": "Demo Citizen G",
            "phone": "+256700000007",
            "email": "demo.citizen.g@example.test",
            "location": "Ntinda, Kampala",
            "status": "Ready for Collection",
            "payment_status": "Verified",
            "identity_status": "Matched",
            "sla_overdue": False,
            "channel": "Phone",
            "profile_status": "Active"
        },
        {
            "id": "req_pass3_008",
            "ref": "NGS-NIRA-2026-0008",
            "profile_id": "CP-008",
            "nin": "CF900000000007",
            "name": "Demo Citizen H",
            "phone": "+256700000008",
            "email": "demo.citizen.h@example.test",
            "location": "Ntinda, Kampala",
            "status": "Closed",
            "payment_status": "Verified",
            "identity_status": "Matched",
            "sla_overdue": False,
            "decision": "Approved",
            "closure_notes": "Verified against simulated backup registry. Approved for card reissue.",
            "channel": "Phone",
            "profile_status": "Active"
        },
        {
            "id": "req_pass3_009",
            "ref": "NGS-NIRA-2026-0009",
            "profile_id": "CP-009",
            "nin": "CF900000000008",
            "name": "Demo Citizen I",
            "phone": "+256700000009",
            "email": "demo.citizen.i@example.test",
            "location": "Ntinda, Kampala",
            "status": "Under Review",
            "payment_status": "Not Required",
            "identity_status": "Requires Review",
            "sla_overdue": True,
            "channel": "Phone",
            "profile_status": "Active"
        }
    ]
    
    for scene in demo_scenarios:
        # Create citizen profile if it doesn't exist
        if not frappe.db.exists("NileGov Citizen Profile", scene["profile_id"]):
            profile = frappe.new_doc("NileGov Citizen Profile")
            profile.citizen_profile_id = scene["profile_id"]
            profile.full_name = scene["name"]
            profile.phone = scene["phone"]
            profile.email = scene["email"]
            profile.location = scene["location"]
            profile.preferred_contact_channel = scene["channel"]
            profile.status = scene["profile_status"]
            profile.nin = scene["nin"]
            profile.insert(ignore_permissions=True)
            frappe.db.commit()
            
        # Seed default consent records for CP-001
        if scene["profile_id"] == "CP-001":
            purposes = [
                ("Service Request Processing", "Granted"),
                ("Simulated Identity Verification", "Granted"),
                ("Simulated Payment Verification", "Granted"),
                ("Status Notifications", "Granted"),
                ("Future MDA Integration Readiness", "Pending")
            ]
            for idx, (purpose, status) in enumerate(purposes):
                consent_id = f"CON-{scene['profile_id']}-{idx+1}"
                if not frappe.db.exists("NileGov Consent Record", consent_id):
                    consent = frappe.new_doc("NileGov Consent Record")
                    consent.consent_record_id = consent_id
                    consent.citizen_profile = scene["profile_id"]
                    consent.consent_purpose = purpose
                    consent.consent_channel = "Portal"
                    consent.consent_status = status
                    consent.consent_given_by = scene["name"]
                    consent.consent_given_at = get_datetime()
                    consent.insert(ignore_permissions=True)
                    frappe.db.commit()
                    
        # Seed withdrawn consent for CP-002
        elif scene["profile_id"] == "CP-002":
            consent_id = f"CON-{scene['profile_id']}-1"
            if not frappe.db.exists("NileGov Consent Record", consent_id):
                consent = frappe.new_doc("NileGov Consent Record")
                consent.consent_record_id = consent_id
                consent.citizen_profile = scene["profile_id"]
                consent.consent_purpose = "Service Request Processing"
                consent.consent_channel = "Email"
                consent.consent_status = "Withdrawn"
                consent.consent_given_by = scene["name"]
                consent.consent_given_at = get_datetime()
                consent.withdrawal_timestamp = get_datetime()
                consent.insert(ignore_permissions=True)
                frappe.db.commit()
                
        # Seed expired consent for CP-003
        elif scene["profile_id"] == "CP-003":
            consent_id = f"CON-{scene['profile_id']}-1"
            if not frappe.db.exists("NileGov Consent Record", consent_id):
                consent = frappe.new_doc("NileGov Consent Record")
                consent.consent_record_id = consent_id
                consent.citizen_profile = scene["profile_id"]
                consent.consent_purpose = "Service Request Processing"
                consent.consent_channel = "SMS"
                consent.consent_status = "Expired"
                consent.consent_given_by = scene["name"]
                consent.consent_given_at = get_datetime()
                consent.expiry_date = add_to_date(get_datetime(), days=-1)
                consent.insert(ignore_permissions=True)
                frappe.db.commit()

        # Create service request if it doesn't exist
        if not frappe.db.exists("NileGov Service Request", scene["id"]):
            request = frappe.new_doc("NileGov Service Request")
            request.service_request_id = scene["id"]
            request.reference_no = scene["ref"]
            request.service_type = service_code
            request.citizen_profile = scene["profile_id"]
            request.citizen_full_name = scene["name"]
            request.nin = scene["nin"] or "CF999999999999"
            request.phone = scene["phone"]
            request.email = scene["email"]
            request.location = scene["location"]
            request.reason_for_request = "My National ID is lost."
            
            request.internal_status = scene["status"]
            request.citizen_visible_status = scene["status"]
            request.payment_status = scene["payment_status"]
            request.identity_status = scene["identity_status"]
            
            # Setup SLA rule and deadlines
            request.sla_rule = "SLA-LOST-NID"
            now_dt = get_datetime()

            # Seed specific scenarios
            if scene["id"] == "req_pass3_001":
                request.sla_state = "Within SLA"
                request.response_due_at = add_to_date(now_dt, hours=4)
                request.resolution_due_at = add_to_date(now_dt, hours=48)
                request.sla_deadline = request.resolution_due_at
                
                request.assignment_status = "Unassigned"
                request.queue_name = "National ID Replacement Desk"
                request.assigned_officer = None
            elif scene["id"] == "req_pass3_002":
                # At Risk (elapsed 85%)
                creation_dt = add_to_date(now_dt, hours=-41)
                request.creation = creation_dt
                request.response_due_at = add_to_date(creation_dt, hours=4)
                request.resolution_due_at = add_to_date(creation_dt, hours=48)
                request.sla_deadline = request.resolution_due_at
                request.sla_state = "At Risk"
                request.at_risk_flag = 1
                
                request.assigned_officer = "officer_demo"
                request.assignment_status = "Assigned"
                request.queue_name = "National ID Replacement Desk"
                request.assigned_at = now_dt
            elif scene["id"] == "req_pass3_003":
                # Overdue (elapsed 110%, no escalation yet)
                creation_dt = add_to_date(now_dt, hours=-53)
                request.creation = creation_dt
                request.response_due_at = add_to_date(creation_dt, hours=4)
                request.resolution_due_at = add_to_date(creation_dt, hours=48)
                request.sla_deadline = request.resolution_due_at
                request.sla_state = "Overdue"
                request.overdue_flag = 1
                
                request.assigned_officer = "officer_review"
                request.assignment_status = "Assigned"
                request.assigned_department = "Verification Desk"
                request.queue_name = "Verification Desk"
                request.assigned_at = now_dt
            elif scene["id"] == "req_pass3_004":
                # Regular SLA setup
                request.sla_state = "Within SLA"
                request.response_due_at = add_to_date(now_dt, hours=4)
                request.resolution_due_at = add_to_date(now_dt, hours=48)
                request.sla_deadline = request.resolution_due_at
                
                request.assigned_department = "National ID Replacement Desk"
                request.queue_name = "National ID Replacement Desk"
                request.assignment_status = "Unassigned"
                request.assigned_officer = None
            elif scene["id"] == "req_pass3_005":
                # Escalation Recommended (elapsed 120%, escalation threshold exceeded)
                creation_dt = add_to_date(now_dt, hours=-58)
                request.creation = creation_dt
                request.response_due_at = add_to_date(creation_dt, hours=4)
                request.resolution_due_at = add_to_date(creation_dt, hours=48)
                request.sla_deadline = request.resolution_due_at
                request.sla_state = "Overdue"
                request.overdue_flag = 1
                request.escalation_state = "Escalation Recommended"
                
                request.assigned_officer = "officer_review"
                request.assignment_status = "Reassigned"
                request.queue_name = "National ID Replacement Desk"
                request.assigned_at = now_dt
                request.reassigned_at = now_dt
                request.reassignment_reason = "Verification workload overflow"
            elif scene["id"] == "req_pass3_006":
                # Escalated
                creation_dt = add_to_date(now_dt, hours=-58)
                request.creation = creation_dt
                request.response_due_at = add_to_date(creation_dt, hours=4)
                request.resolution_due_at = add_to_date(creation_dt, hours=48)
                request.sla_deadline = request.resolution_due_at
                request.sla_state = "Overdue"
                request.overdue_flag = 1
                request.escalation_state = "Escalated"
                request.escalated_to = "supervisor_demo"
                request.escalated_at = now_dt
                request.escalation_reason = "SLA resolution deadline breached by more than 2 hours. Routing to supervisor for workload balancing."
                
                request.assigned_supervisor = "supervisor_demo"
                request.supervisor_review_required = 1
                request.assignment_status = "Supervisor Review"
                request.queue_name = "Supervisor Review Queue"
                request.assigned_at = now_dt
                request.assigned_officer = None
            elif scene["id"] == "req_pass3_007":
                # Regular SLA setup
                request.sla_state = "Within SLA"
                request.response_due_at = add_to_date(now_dt, hours=4)
                request.resolution_due_at = add_to_date(now_dt, hours=48)
                request.sla_deadline = request.resolution_due_at
                
                request.assigned_officer = "officer_demo"
                request.assignment_status = "Returned to Officer"
                request.queue_name = "National ID Replacement Desk"
                request.assigned_at = now_dt
            elif scene["id"] == "req_pass3_008":
                # Met (closed request)
                request.sla_state = "Met"
                request.response_due_at = add_to_date(now_dt, hours=-24)
                request.resolution_due_at = add_to_date(now_dt, hours=24)
                request.sla_deadline = request.resolution_due_at
                
                request.assigned_officer = "officer_demo"
                request.assignment_status = "Closed"
                request.queue_name = "Completed Cases Queue"
                request.assigned_at = now_dt
            else:
                # Regular SLA setup
                request.sla_state = "Within SLA"
                request.response_due_at = add_to_date(now_dt, hours=4)
                request.resolution_due_at = add_to_date(now_dt, hours=48)
                request.sla_deadline = request.resolution_due_at
                
                request.assigned_officer = officer_user
                request.assignment_status = "Assigned"
                request.queue_name = "National ID Replacement Desk"
                request.assigned_at = now_dt

            if "decision" in scene:
                request.decision = scene["decision"]
            if "closure_notes" in scene:
                request.closure_notes = scene["closure_notes"]
                
            request.insert(ignore_permissions=True)
            frappe.db.commit()

    # 3. Seed Evidence Documents
    evidence_seeds = [
        {
            "id": "EVI-CP001-POL",
            "profile_id": "CP-001",
            "request_id": "req_pass3_001",
            "title": "Ntinda Police Post Letter of Loss",
            "type": "Police Letter Placeholder",
            "file": "demo-police-letter-placeholder.pdf",
            "status": "Submitted",
            "channel": "Web Form",
            "notes": None,
            "verified_by": None,
            "verified_at": None
        },
        {
            "id": "EVI-CP001-AFF",
            "profile_id": "CP-001",
            "request_id": "req_pass3_001",
            "title": "Commissioner of Oaths Statutory Declaration",
            "type": "Affidavit Placeholder",
            "file": "demo-affidavit-placeholder.pdf",
            "status": "Under Review",
            "channel": "Web Form",
            "notes": None,
            "verified_by": None,
            "verified_at": None
        },
        {
            "id": "EVI-CP001-ID",
            "profile_id": "CP-001",
            "request_id": "req_pass3_001",
            "title": "Photocopy of Fictional Driving Permit",
            "type": "Supporting ID Placeholder",
            "file": "demo-supporting-id-placeholder.pdf",
            "status": "Accepted",
            "channel": "Portal",
            "notes": "Verified against physical driving license copy.",
            "verified_by": "officer_demo",
            "verified_at": get_datetime()
        },
        {
            "id": "EVI-CP001-PAY",
            "profile_id": "CP-001",
            "request_id": "req_pass3_001",
            "title": "Mobile Money Payment Confirmation Screenshot",
            "type": "Payment Receipt Placeholder",
            "file": "demo-payment-receipt-placeholder.pdf",
            "status": "Demo Placeholder",
            "channel": "WhatsApp",
            "notes": None,
            "verified_by": None,
            "verified_at": None
        },
        {
            "id": "EVI-CP001-OTH",
            "profile_id": "CP-001",
            "request_id": "req_pass3_001",
            "title": "Utility Bill for Bukoto Address Proof",
            "type": "Other Supporting Document",
            "file": "demo-utility-bill-placeholder.pdf",
            "status": "Requires Replacement",
            "channel": "Email",
            "notes": "The uploaded image is blurry. Please upload a clear photo of the utility bill.",
            "verified_by": "officer_demo",
            "verified_at": get_datetime()
        },
        {
            "id": "EVI-CP002-REJ",
            "profile_id": "CP-002",
            "request_id": "req_pass3_002",
            "title": "Blurry Document Attachment",
            "type": "Other Supporting Document",
            "file": "demo-invalid-attachment.pdf",
            "status": "Rejected",
            "channel": "Web Form",
            "notes": "Doc mismatch: name does not match citizen profile.",
            "verified_by": "officer_demo",
            "verified_at": get_datetime()
        }
    ]

    for ev in evidence_seeds:
        if not frappe.db.exists("NileGov Evidence Document", ev["id"]):
            consent_record_id = None
            if ev["profile_id"] == "CP-001":
                consent_record_id = "CON-CP-001-1"

            doc = frappe.new_doc("NileGov Evidence Document")
            doc.evidence_document_id = ev["id"]
            doc.citizen_profile = ev["profile_id"]
            doc.service_request = ev["request_id"]
            doc.consent_record = consent_record_id
            doc.document_type = ev["type"]
            doc.document_title = ev["title"]
            doc.file = ev["file"]
            doc.upload_channel = ev["channel"]
            doc.uploaded_by = "officer_demo" if ev["status"] == "Accepted" else "Administrator"
            doc.uploaded_at = get_datetime()
            doc.verification_status = ev["status"]
            doc.visibility = "Citizen and Officer"
            if ev["verified_by"]:
                doc.verified_by = ev["verified_by"]
            if ev["verified_at"]:
                doc.verified_timestamp = ev["verified_at"]
            if ev["notes"]:
                doc.officer_notes = ev["notes"]
            doc.disclaimer = "Prototype simulation only. No live Government registry access."
            
            doc.insert(ignore_permissions=True)
            frappe.db.commit()

    # 4. Seed Simulated Notifications
    notifications_seeds = [
        {
            "id": "NOT-req_pass3_001-REC",
            "req_id": "req_pass3_001",
            "profile_id": "CP-001",
            "recipient": "+256700000001",
            "channel": "SMS",
            "msg_type": "Request Received",
            "status": "Simulated Sent",
            "sent_at": get_datetime(),
            "msg": "Dear Demo Citizen A, your Lost National ID replacement request has been successfully submitted under reference number NGS-NIRA-2026-0001. Prototype simulation only. No live email, SMS, WhatsApp or portal notification was sent."
        },
        {
            "id": "NOT-req_pass3_002-REV",
            "req_id": "req_pass3_002",
            "profile_id": "CP-002",
            "recipient": "demo.citizen.b@example.test",
            "channel": "Email",
            "msg_type": "Under Review",
            "status": "Simulated Sent",
            "sent_at": get_datetime(),
            "msg": "Dear Demo Citizen B, your request NGS-NIRA-2026-0002 has been assigned and is now under review by the Service Desk. Prototype simulation only. No live email, SMS, WhatsApp or portal notification was sent."
        },
        {
            "id": "NOT-req_pass3_003-INF",
            "req_id": "req_pass3_003",
            "profile_id": "CP-003",
            "recipient": "+256700000003",
            "channel": "SMS",
            "msg_type": "Information Required",
            "status": "Draft",
            "msg": "Dear Demo Citizen C, additional information is required for case NGS-NIRA-2026-0003. Please upload documents. Prototype simulation only."
        },
        {
            "id": "NOT-req_pass3_004-PAY",
            "req_id": "req_pass3_004",
            "profile_id": "CP-004",
            "recipient": "+256700000004",
            "channel": "WhatsApp",
            "msg_type": "Payment Pending",
            "status": "Queued",
            "msg": "Dear Demo Citizen D, a prototype processing fee of UGX 15,000.00 is pending for case NGS-NIRA-2026-0004. Prototype simulation only. No live email, SMS, WhatsApp or portal notification was sent."
        },
        {
            "id": "NOT-req_pass3_005-VER",
            "req_id": "req_pass3_005",
            "profile_id": "CP-005",
            "recipient": "+256700000005",
            "channel": "SMS",
            "msg_type": "Payment Verified",
            "status": "Simulated Sent",
            "sent_at": get_datetime(),
            "msg": "Dear Demo Citizen E, your simulated payment for case NGS-NIRA-2026-0005 has been successfully verified. Prototype simulation only. No live email, SMS, WhatsApp or portal notification was sent."
        },
        {
            "id": "NOT-req_pass3_006-APP",
            "req_id": "req_pass3_006",
            "profile_id": "CP-006",
            "recipient": "+256700000006",
            "channel": "SMS",
            "msg_type": "Approved",
            "status": "Simulated Sent",
            "sent_at": get_datetime(),
            "msg": "Dear Demo Citizen F, your Lost National ID replacement request NGS-NIRA-2026-0006 has been approved. Prototype simulation only. No live email, SMS, WhatsApp or portal notification was sent."
        },
        {
            "id": "NOT-req_pass3_007-RDY",
            "req_id": "req_pass3_007",
            "profile_id": "CP-007",
            "recipient": "+256700000007",
            "channel": "SMS",
            "msg_type": "Ready for Collection",
            "status": "Simulated Sent",
            "sent_at": get_datetime(),
            "msg": "Dear Demo Citizen G, your replacement National ID card under case NGS-NIRA-2026-0007 is ready for collection at the Ntinda Desk, Kampala. Prototype simulation only."
        },
        {
            "id": "NOT-req_pass3_008-CLO",
            "req_id": "req_pass3_008",
            "profile_id": "CP-008",
            "recipient": "+256700000008",
            "channel": "SMS",
            "msg_type": "Closed",
            "status": "Simulated Sent",
            "sent_at": get_datetime(),
            "msg": "Dear Demo Citizen H, case NGS-NIRA-2026-0008 has been closed as completed. Prototype simulation only. No live email, SMS, WhatsApp or portal notification was sent."
        },
        {
            "id": "NOT-req_pass3_002-RSK",
            "req_id": "req_pass3_002",
            "profile_id": "CP-002",
            "recipient": "demo.citizen.b@example.test",
            "channel": "Email",
            "msg_type": "SLA At Risk",
            "status": "Queued",
            "msg": "SLA warning: Case NGS-NIRA-2026-0002 has exceeded its at-risk processing threshold and requires immediate attention."
        },
        {
            "id": "NOT-req_pass3_003-OVR",
            "req_id": "req_pass3_003",
            "profile_id": "CP-003",
            "recipient": "+256700000003",
            "channel": "SMS",
            "msg_type": "SLA Overdue",
            "status": "Simulated Sent",
            "sent_at": get_datetime(),
            "msg": "SLA breach: Case NGS-NIRA-2026-0003 has exceeded allowed response/resolution limits. Prototype simulation only."
        },
        {
            "id": "NOT-req_pass3_006-ESC",
            "req_id": "req_pass3_006",
            "profile_id": "CP-006",
            "recipient": "supervisor_demo",
            "channel": "Email",
            "msg_type": "Escalated",
            "status": "Simulated Sent",
            "sent_at": get_datetime(),
            "msg": "Casework escalation: Case NGS-NIRA-2026-0006 has been escalated to supervisor_demo. Reason: SLA resolution breach. Prototype simulation only."
        }
    ]

    for ns in notifications_seeds:
        if not frappe.db.exists("NileGov Citizen Notification", ns["id"]):
            not_doc = frappe.new_doc("NileGov Citizen Notification")
            not_doc.notification_event_id = ns["id"]
            not_doc.service_request = ns["req_id"]
            not_doc.citizen_profile = ns["profile_id"]
            
            # Map consent if CP-001
            if ns["profile_id"] == "CP-001":
                not_doc.consent_record = "CON-CP-001-4" # Status Notifications consent
                not_doc.consent_checked = 1
                not_doc.consent_status_at_trigger = "Granted"
                
            not_doc.recipient = ns["recipient"]
            not_doc.recipient_type = "Supervisor" if ns["recipient"] == "supervisor_demo" else "Citizen"
            not_doc.channel = ns["channel"]
            not_doc.message_type = ns["msg_type"]
            not_doc.notification_type = "SLA Breach" if "SLA" in ns["msg_type"] else "Status Update"
            not_doc.message = ns["msg"]
            not_doc.delivery_status = ns["status"]
            not_doc.disclaimer = "Prototype simulation only. No live email, SMS, WhatsApp or portal notification was sent."
            
            if "sent_at" in ns and ns["sent_at"]:
                not_doc.simulated_sent_at = ns["sent_at"]
                not_doc.sent_at = ns["sent_at"]
                
            not_doc.insert(ignore_permissions=True)
            frappe.db.commit()

    # 5. Seed Simulated Payment Records
    payment_seeds = [
        {
            "id": "PAY-req_pass3_001",
            "req_id": "req_pass3_001",
            "profile_id": "CP-001",
            "amount": 0.0,
            "purpose": "Not Applicable",
            "channel": "Not Applicable",
            "status": "Not Required",
            "ref": "",
            "verify_status": "Not Applicable",
            "receipt": "Not Required",
            "recon": "Not Required"
        },
        {
            "id": "PAY-req_pass3_002",
            "req_id": "req_pass3_002",
            "profile_id": "CP-002",
            "amount": 50000.0,
            "purpose": "National ID Replacement Fee",
            "channel": "Simulated Mobile Money",
            "status": "Failed",
            "ref": "SIM-PAY-NIRA-2026-0002-FAIL",
            "verify_status": "Simulated Failed",
            "receipt": "Receipt Pending",
            "recon": "Mismatch"
        },
        {
            "id": "PAY-req_pass3_003",
            "req_id": "req_pass3_003",
            "profile_id": "CP-003",
            "amount": 50000.0,
            "purpose": "National ID Replacement Fee",
            "channel": "Simulated Mobile Money",
            "status": "Submitted",
            "ref": "SIM-PAY-NIRA-2026-0003-REVIEW",
            "verify_status": "Requires Review",
            "receipt": "Receipt Pending",
            "recon": "Requires Review"
        },
        {
            "id": "PAY-req_pass3_004",
            "req_id": "req_pass3_004",
            "profile_id": "CP-004",
            "amount": 50000.0,
            "purpose": "National ID Replacement Fee",
            "channel": "Simulated Mobile Money",
            "status": "Pending",
            "ref": "",
            "verify_status": "Not Checked",
            "receipt": "Receipt Pending",
            "recon": "Pending Reconciliation"
        },
        {
            "id": "PAY-req_pass3_005",
            "req_id": "req_pass3_005",
            "profile_id": "CP-005",
            "amount": 50000.0,
            "purpose": "National ID Replacement Fee",
            "channel": "Simulated Mobile Money",
            "status": "Verified",
            "ref": "SIM-PAY-NIRA-2026-0005",
            "verify_status": "Simulated Verified",
            "receipt": "Receipt Ready",
            "recon": "Reconciled"
        },
        {
            "id": "PAY-req_pass3_006",
            "req_id": "req_pass3_006",
            "profile_id": "CP-006",
            "amount": 50000.0,
            "purpose": "National ID Replacement Fee",
            "channel": "Simulated Card",
            "status": "Verified",
            "ref": "SIM-PAY-NIRA-2026-0006",
            "verify_status": "Simulated Verified",
            "receipt": "Simulated Receipt Generated",
            "receipt_ref": "SIM-RECEIPT-2026-0006",
            "recon": "Reconciled"
        },
        {
            "id": "PAY-req_pass3_007",
            "req_id": "req_pass3_007",
            "profile_id": "CP-007",
            "amount": 50000.0,
            "purpose": "National ID Replacement Fee",
            "channel": "Simulated Mobile Money",
            "status": "Verified",
            "ref": "SIM-PAY-NIRA-2026-0007",
            "verify_status": "Simulated Verified",
            "receipt": "Receipt Ready",
            "recon": "Pending Reconciliation"
        },
        {
            "id": "PAY-req_pass3_008",
            "req_id": "req_pass3_008",
            "profile_id": "CP-008",
            "amount": 50000.0,
            "purpose": "National ID Replacement Fee",
            "channel": "Simulated Bank",
            "status": "Verified",
            "ref": "SIM-PAY-NIRA-2026-0008",
            "verify_status": "Simulated Verified",
            "receipt": "Simulated Receipt Generated",
            "receipt_ref": "SIM-RECEIPT-2026-0008",
            "recon": "Reconciled"
        }
    ]

    for ps in payment_seeds:
        if not frappe.db.exists("NileGov Payment Record", ps["id"]):
            pay_doc = frappe.new_doc("NileGov Payment Record")
            pay_doc.payment_record_id = ps["id"]
            pay_doc.service_request = ps["req_id"]
            pay_doc.citizen_profile = ps["profile_id"]
            
            # Map consent if CP-001
            if ps["profile_id"] == "CP-001":
                pay_doc.consent_record = "CON-CP-001-3" # Simulated Payment Verification consent

            pay_doc.amount = ps["amount"]
            pay_doc.payment_purpose = ps["purpose"]
            pay_doc.payment_channel = ps["channel"]
            pay_doc.payment_status = ps["status"]
            pay_doc.simulated_transaction_reference = ps["ref"]
            pay_doc.verification_status = ps["verify_status"]
            pay_doc.receipt_status = ps["receipt"]
            pay_doc.reconciliation_status = ps["recon"]
            
            if "receipt_ref" in ps:
                pay_doc.receipt_reference = ps["receipt_ref"]
            if ps["status"] == "Verified":
                pay_doc.verified_by = "officer_demo"
                pay_doc.verification_timestamp = get_datetime()
                
            pay_doc.disclaimer = "Prototype simulation only. No live payment was processed."
            pay_doc.insert(ignore_permissions=True)
            frappe.db.commit()

    # 6. Seed Service Catalogue records
    catalogue_seeds = [
        {
            "id": "SVC-LOST-NID",
            "name": "Lost National ID Replacement",
            "code": "LOST_NATIONAL_ID",
            "mda": "National Identification and Registration Authority (NIRA)",
            "category": "Identity Services",
            "description": "Request replacement for a lost or damaged National Identification Card.",
            "required_docs": "Police Letter Placeholder, Affidavit Placeholder, Supporting ID Placeholder",
            "fee_required": 1,
            "fee_amount": 50000.0,
            "currency": "UGX",
            "purpose": "National ID Replacement Fee",
            "provider": "Simulated",
            "sla_rule": "SLA-LOST-NID",
            "department": "National ID Replacement Desk",
            "queue": "National ID Replacement Desk",
            "workflow": "Replacement Request Workflow",
            "status": "Active",
            "visibility": "Demo Visible"
        },
        {
            "id": "SVC-CITIZEN-COMPLAINT",
            "name": "Citizen Complaint Portal",
            "code": "CITIZEN_COMPLAINT",
            "mda": "Inspectorate of Government (IG)",
            "category": "Citizen Complaints",
            "description": "Submit a public service delivery complaint or report misconduct.",
            "required_docs": "",
            "fee_required": 0,
            "fee_amount": 0.0,
            "currency": "UGX",
            "purpose": "Not Applicable",
            "provider": "Not Applicable",
            "sla_rule": None,
            "department": "Complaints Intake Unit",
            "queue": "Citizen Complaints Desk",
            "workflow": "Complaint Resolution Workflow",
            "status": "Demo Only",
            "visibility": "Demo Visible"
        },
        {
            "id": "SVC-PERMIT-APPLICATION",
            "name": "Environmental Permit Application",
            "code": "ENVIRONMENT_PERMIT",
            "mda": "National Environment Management Authority (NEMA)",
            "category": "Permit Applications",
            "description": "Apply for environmental impact assessment certificates and permits.",
            "required_docs": "Environmental Impact Assessment Report, Land Ownership Document",
            "fee_required": 1,
            "fee_amount": 250000.0,
            "currency": "UGX",
            "purpose": "Service Processing Fee",
            "provider": "Pesapal Sandbox Ready",
            "sla_rule": None,
            "department": "Environmental Monitoring and Compliance",
            "queue": "Environmental Permits Desk",
            "workflow": "Standard Application Workflow",
            "status": "Inactive",
            "visibility": "Citizen Hidden"
        }
    ]

    for cs in catalogue_seeds:
        if not frappe.db.exists("NileGov Service Catalogue", cs["id"]):
            cat_doc = frappe.new_doc("NileGov Service Catalogue")
            cat_doc.service_catalogue_id = cs["id"]
            cat_doc.service_name = cs["name"]
            cat_doc.service_code = cs["code"]
            cat_doc.responsible_mda_placeholder = cs["mda"]
            cat_doc.service_category = cs["category"]
            cat_doc.service_description = cs["description"]
            cat_doc.required_documents = cs["required_docs"]
            cat_doc.fee_required = cs["fee_required"]
            cat_doc.default_fee_amount = cs["fee_amount"]
            cat_doc.default_currency = cs["currency"]
            cat_doc.default_payment_purpose = cs["purpose"]
            cat_doc.default_payment_provider = cs["provider"]
            cat_doc.default_sla_rule = cs["sla_rule"]
            cat_doc.responsible_department = cs["department"]
            cat_doc.responsible_queue = cs["queue"]
            cat_doc.workflow_template = cs["workflow"]
            cat_doc.active_status = cs["status"]
            cat_doc.public_visibility = cs["visibility"]
            cat_doc.disclaimer = "Prototype service catalogue only. Not connected to a live government service registry."
            cat_doc.insert(ignore_permissions=True)
            frappe.db.commit()

    # 7. Seed Reporting Snapshots conditionally (if DocType exists at runtime)
    if frappe.db.table_exists("NileGov Reporting Snapshot"):
        import json
        snapshot_seeds = [
            {
                "id": "SNAP-DAILY-001",
                "name": "Daily Operations Reporting Snapshot",
                "start": 1772539200.0,
                "end": 1772625600.0,
                "generated_at": 1772625600.0,
                "by": "officer_demo",
                "dataset": "Seeded Fictional Demo Data",
                "total_requests": 9,
                "total_services": 3,
                "active_services": 1,
                "demo_services": 1,
                "status_breakdown": {"Submitted": 1, "Under Review": 2, "Information Required": 1, "Payment Pending": 1, "Payment Verified": 1, "Approved": 1, "Ready for Collection": 1, "Closed": 1},
                "service_breakdown": {"LOST_NATIONAL_ID": 9},
                "queue_breakdown": {"National ID Replacement Desk": 7, "Verification Desk": 1, "Supervisor Review Queue": 1},
                "loc_breakdown": {"Ntinda, Kampala": 8, "Bukoto, Kampala": 1},
                "within_sla": 5,
                "at_risk": 1,
                "overdue": 3,
                "escalated": 1,
                "ev_complete": 8,
                "ev_incomplete": 1,
                "ev_rejected": 1,
                "ev_replaced": 1,
                "pay_pending": 1,
                "pay_submitted": 1,
                "pay_verified": 5,
                "pay_failed": 1,
                "pay_reversed": 0,
                "notif_draft": 1,
                "notif_queued": 2,
                "notif_sent": 8,
                "notif_failed": 1,
                "notif_cancelled": 0,
                "notif_not_req": 0,
                "workload": {"officer_demo": 3, "officer_review": 3},
                "pay_val": {"total_simulated_payment_value": 250000.0}
            },
            {
                "id": "SNAP-SERVICE-PERF-001",
                "name": "Service Performance Reporting Snapshot",
                "start": 1772539200.0,
                "end": 1772625600.0,
                "generated_at": 1772625600.0,
                "by": "officer_demo",
                "dataset": "Seeded Fictional Demo Data",
                "total_requests": 9,
                "total_services": 3,
                "active_services": 1,
                "demo_services": 1,
                "status_breakdown": {"Submitted": 1, "Under Review": 2, "Information Required": 1, "Payment Pending": 1, "Payment Verified": 1, "Approved": 1, "Ready for Collection": 1, "Closed": 1},
                "service_breakdown": {"LOST_NATIONAL_ID": 9},
                "queue_breakdown": {"National ID Replacement Desk": 7, "Verification Desk": 1, "Supervisor Review Queue": 1},
                "loc_breakdown": {"Ntinda, Kampala": 8, "Bukoto, Kampala": 1},
                "within_sla": 5,
                "at_risk": 1,
                "overdue": 3,
                "escalated": 1,
                "ev_complete": 8,
                "ev_incomplete": 1,
                "ev_rejected": 1,
                "ev_replaced": 1,
                "pay_pending": 1,
                "pay_submitted": 1,
                "pay_verified": 5,
                "pay_failed": 1,
                "pay_reversed": 0,
                "notif_draft": 1,
                "notif_queued": 2,
                "notif_sent": 8,
                "notif_failed": 1,
                "notif_cancelled": 0,
                "notif_not_req": 0,
                "workload": {"officer_demo": 3, "officer_review": 3},
                "pay_val": {"total_simulated_payment_value": 250000.0}
            },
            {
                "id": "SNAP-SLA-BACKLOG-001",
                "name": "SLA Backlog Reporting Snapshot",
                "start": 1772539200.0,
                "end": 1772625600.0,
                "generated_at": 1772625600.0,
                "by": "supervisor_demo",
                "dataset": "Seeded Fictional Demo Data",
                "total_requests": 9,
                "total_services": 3,
                "active_services": 1,
                "demo_services": 1,
                "status_breakdown": {"Submitted": 1, "Under Review": 2, "Information Required": 1, "Payment Pending": 1, "Payment Verified": 1, "Approved": 1, "Ready for Collection": 1, "Closed": 1},
                "service_breakdown": {"LOST_NATIONAL_ID": 9},
                "queue_breakdown": {"National ID Replacement Desk": 7, "Verification Desk": 1, "Supervisor Review Queue": 1},
                "loc_breakdown": {"Ntinda, Kampala": 8, "Bukoto, Kampala": 1},
                "within_sla": 5,
                "at_risk": 1,
                "overdue": 3,
                "escalated": 1,
                "ev_complete": 8,
                "ev_incomplete": 1,
                "ev_rejected": 1,
                "ev_replaced": 1,
                "pay_pending": 1,
                "pay_submitted": 1,
                "pay_verified": 5,
                "pay_failed": 1,
                "pay_reversed": 0,
                "notif_draft": 1,
                "notif_queued": 2,
                "notif_sent": 8,
                "notif_failed": 1,
                "notif_cancelled": 0,
                "notif_not_req": 0,
                "workload": {"officer_demo": 3, "officer_review": 3},
                "pay_val": {"total_simulated_payment_value": 250000.0}
            },
            {
                "id": "SNAP-PAY-NOTIF-001",
                "name": "Payment & Notification Summary Snapshot",
                "start": 1772539200.0,
                "end": 1772625600.0,
                "generated_at": 1772625600.0,
                "by": "officer_demo",
                "dataset": "Seeded Fictional Demo Data",
                "total_requests": 9,
                "total_services": 3,
                "active_services": 1,
                "demo_services": 1,
                "status_breakdown": {"Submitted": 1, "Under Review": 2, "Information Required": 1, "Payment Pending": 1, "Payment Verified": 1, "Approved": 1, "Ready for Collection": 1, "Closed": 1},
                "service_breakdown": {"LOST_NATIONAL_ID": 9},
                "queue_breakdown": {"National ID Replacement Desk": 7, "Verification Desk": 1, "Supervisor Review Queue": 1},
                "loc_breakdown": {"Ntinda, Kampala": 8, "Bukoto, Kampala": 1},
                "within_sla": 5,
                "at_risk": 1,
                "overdue": 3,
                "escalated": 1,
                "ev_complete": 8,
                "ev_incomplete": 1,
                "ev_rejected": 1,
                "ev_replaced": 1,
                "pay_pending": 1,
                "pay_submitted": 1,
                "pay_verified": 5,
                "pay_failed": 1,
                "pay_reversed": 0,
                "notif_draft": 1,
                "notif_queued": 2,
                "notif_sent": 8,
                "notif_failed": 1,
                "notif_cancelled": 0,
                "notif_not_req": 0,
                "workload": {"officer_demo": 3, "officer_review": 3},
                "pay_val": {"total_simulated_payment_value": 250000.0}
            }
        ]

        for ss in snapshot_seeds:
            if not frappe.db.exists("NileGov Reporting Snapshot", ss["id"]):
                snap_doc = frappe.new_doc("NileGov Reporting Snapshot")
                snap_doc.reporting_snapshot_id = ss["id"]
                snap_doc.snapshot_name = ss["name"]
                snap_doc.reporting_period_start = ss["start"]
                snap_doc.reporting_period_end = ss["end"]
                snap_doc.generated_at = ss["generated_at"]
                snap_doc.generated_by = ss["by"]
                snap_doc.source_dataset = ss["dataset"]
                snap_doc.total_requests = ss["total_requests"]
                snap_doc.total_services = ss["total_services"]
                snap_doc.active_services = ss["active_services"]
                snap_doc.demo_services = ss["demo_services"]
                snap_doc.requests_by_status = json.dumps(ss["status_breakdown"])
                snap_doc.requests_by_service = json.dumps(ss["service_breakdown"])
                snap_doc.requests_by_queue = json.dumps(ss["queue_breakdown"])
                snap_doc.requests_by_location = json.dumps(ss["loc_breakdown"])
                snap_doc.within_sla_count = ss["within_sla"]
                snap_doc.at_risk_count = ss["at_risk"]
                snap_doc.overdue_count = ss["overdue"]
                snap_doc.escalated_count = ss["escalated"]
                snap_doc.evidence_complete_count = ss["ev_complete"]
                snap_doc.evidence_incomplete_count = ss["ev_incomplete"]
                snap_doc.evidence_rejected_count = ss["ev_rejected"]
                snap_doc.evidence_requiring_replacement_count = ss["ev_replaced"]
                snap_doc.payment_pending_count = ss["pay_pending"]
                snap_doc.payment_verified_count = ss["pay_verified"]
                snap_doc.payment_failed_count = ss["pay_failed"]
                snap_doc.notification_draft_count = ss["notif_draft"]
                snap_doc.notification_queued_count = ss["notif_queued"]
                snap_doc.notification_simulated_sent_count = ss["notif_sent"]
                snap_doc.notification_failed_count = ss["notif_failed"]
                snap_doc.notification_cancelled_count = ss["notif_cancelled"]
                snap_doc.notification_not_required_count = ss["notif_not_req"]
                snap_doc.officer_workload_summary = json.dumps(ss["workload"])
                snap_doc.payment_value_summary = json.dumps(ss["pay_val"])
                snap_doc.disclaimer = "Prototype reporting snapshot only. Metrics are calculated from fictional demo data and are not official government statistics."
                snap_doc.insert(ignore_permissions=True)
                frappe.db.commit()




