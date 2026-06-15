import frappe

def rollback_data():
    batch_marker = "DEMO-L2-2026"
    
    frappe.logger().info("Starting L2 Demo Data Rollback...")
    print("Rolling back 7,500 demo records...")
    
    try:
        # Delete Policy Compliance
        frappe.db.sql(f"DELETE FROM `tabNileGov Policy Compliance` WHERE batch_marker = %s", (batch_marker,))
        
        # Delete Service Requests
        frappe.db.sql(f"DELETE FROM `tabNileGov Service Request` WHERE batch_marker = %s", (batch_marker,))
        
        # Delete Payment Records
        frappe.db.sql(f"DELETE FROM `tabNileGov Payment Record` WHERE batch_marker = %s", (batch_marker,))
        
        # Delete Escalation Records
        frappe.db.sql(f"DELETE FROM `tabNileGov Escalation Record` WHERE batch_marker = %s", (batch_marker,))
        
        frappe.db.commit()
        frappe.logger().info("L2 Demo Data Rollback Complete.")
        print("Successfully rolled back all L2 demo records.")
    except Exception as e:
        frappe.db.rollback()
        print(f"Error rolling back data: {str(e)}")

if __name__ == "__main__":
    rollback_data()
