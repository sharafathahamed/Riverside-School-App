import frappe
from res_school.tasks import send_low_alert

def run():
    doc = frappe.get_doc({
        "doctype": "Attendance",
        "student": "Arjun Sharma",
        "class_section": "Grade 8",
        "date": "2026-03-17",
        "status": "Absent",
        "docstatus": 1
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Added 1 more Absent! Now calculating alert again...")

    # Force run the email alert sequence
    send_low_alert()
    frappe.db.commit()
    print("Done executing send_low_alert! It should be sent to the inbox since percentage is < 60%.")
