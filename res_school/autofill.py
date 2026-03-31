import frappe
from frappe.utils import add_days, today

def run():
    student = "Arjun Sharma"
    class_section = "Grade 8"
    
    # Check if student exists
    if not frappe.db.exists("Student", student):
        frappe.msgprint(f"Student {student} not found.")
        return
        
    # We will create 5 Present records
    for i in range(5):
        date = add_days(today(), -(i + 1))
        doc = frappe.get_doc({
            "doctype": "Attendance",
            "student": student,
            "class_section": class_section,
            "date": date,
            "status": "Present",
            "docstatus": 1 
        })
        try:
            doc.insert(ignore_permissions=True)
            print(f"Created Present record for {date}")
        except Exception as e:
            print(f"Could not create for {date}: {e}")

    # We will create 4 Absent records
    for i in range(4):
        date = add_days(today(), -(i + 6))
        doc = frappe.get_doc({
            "doctype": "Attendance",
            "student": student,
            "class_section": class_section,
            "date": date,
            "status": "Absent",
            "docstatus": 1 # 1 means Submitted
        })
        try:
            doc.insert(ignore_permissions=True)
            print(f"Created Absent record for {date}")
        except Exception as e:
            print(f"Could not create for {date}: {e}")

    frappe.db.commit()
    print("Done generating 9 attendance records within the current term dates!")
