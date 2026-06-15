import frappe
from frappe.utils import add_days, getdate, nowdate
import random

def seed_data():
    batch_marker = "DEMO-L2-2026"
    
    frappe.logger().info("Starting L2 Demo Data Seeding...")
    
    # 1. Seed Policy Compliance
    policies = [
        {"policy_name": "Citizen Service SLA Compliance", "adherence_rate": 88.5, "violations": 12},
        {"policy_name": "Fund Allocation Transparency", "adherence_rate": 95.0, "violations": 2},
        {"policy_name": "Public Infrastructure Standards", "adherence_rate": 76.2, "violations": 34},
        {"policy_name": "Healthcare Facility Operational Readiness", "adherence_rate": 91.0, "violations": 5},
    ]
    
    for p in policies:
        if not frappe.db.exists("NileGov Policy Compliance", {"policy_name": p["policy_name"]}):
            doc = frappe.get_doc({
                "doctype": "NileGov Policy Compliance",
                "policy_name": p["policy_name"],
                "adherence_rate": p["adherence_rate"],
                "violations": p["violations"],
                "batch_marker": batch_marker
            })
            doc.insert(ignore_permissions=True)
            
    # 2. Seed 7,500 Service Requests
    service_types = ["Trade License", "Building Permit", "Water Connection", "Medical Certification", "Tax Clearance"]
    locations = ["Kampala", "Wakiso", "Mukono", "Jinja", "Mbarara", "Gulu", "Lira", "Arua", "Mbale", "Soroti"]
    officers = ["John Doe", "Jane Smith", "Alice Johnson", "Bob Williams", "Charlie Brown"]
    statuses = ["Submitted", "Under Review", "Pending", "Closed", "Rejected"]
    sla_states = ["On Time", "Overdue"]
    
    start_date = getdate("2026-01-01")
    
    # Due to time constraints in a demo script, we use direct DB inserts for speed
    # since creating 7,500 docs via ORM can take a few minutes.
    
    frappe.logger().info("Seeding 7,500 Service Requests...")
    
    records = []
    payments = []
    escalations = []
    
    for i in range(7500):
        creation_date = add_days(start_date, random.randint(0, 160))
        srv = random.choice(service_types)
        loc = random.choice(locations)
        officer = random.choice(officers)
        status = random.choice(statuses)
        sla = "Overdue" if random.random() < 0.15 else "On Time" # 15% SLA breach
        
        req_name = f"REQ-DEMO-{i:05d}"
        
        records.append({
            "name": req_name,
            "creation": creation_date,
            "modified": creation_date,
            "service_type": srv,
            "location": loc,
            "assigned_officer": officer,
            "internal_status": status,
            "sla_state": sla,
            "batch_marker": batch_marker
        })
        
        # Payment generation (70% of requests need payment)
        if random.random() < 0.7:
            pay_status = random.choice(["Verified", "Pending", "Failed"])
            amount = random.randint(50, 500) * 1000
            payments.append({
                "name": f"PAY-DEMO-{i:05d}",
                "service_request": req_name,
                "payment_status": pay_status,
                "reconciliation_status": "Reconciled" if pay_status == "Verified" else "Pending",
                "amount": amount,
                "creation": creation_date,
                "modified": creation_date,
                "batch_marker": batch_marker
            })
            
        # Escalation generation (5% of requests escalated)
        if random.random() < 0.05:
            esc_status = random.choice(["Open", "Resolved"])
            escalations.append({
                "name": f"ESC-DEMO-{i:05d}",
                "service_request": req_name,
                "status": esc_status,
                "creation": creation_date,
                "modified": creation_date,
                "batch_marker": batch_marker
            })
            
    # Need to verify table exists, if so insert
    try:
        if records:
            frappe.db.bulk_insert("NileGov Service Request", list(records[0].keys()), [list(r.values()) for r in records], ignore_duplicates=True)
        if payments:
            frappe.db.bulk_insert("NileGov Payment Record", list(payments[0].keys()), [list(p.values()) for p in payments], ignore_duplicates=True)
        if escalations:
            frappe.db.bulk_insert("NileGov Escalation Record", list(escalations[0].keys()), [list(e.values()) for e in escalations], ignore_duplicates=True)
            
        frappe.db.commit()
        frappe.logger().info("L2 Demo Data Seeding Complete.")
        print("Successfully seeded 7,500 records.")
    except Exception as e:
        frappe.db.rollback()
        print(f"Error seeding data: {str(e)}")

if __name__ == "__main__":
    seed_data()
