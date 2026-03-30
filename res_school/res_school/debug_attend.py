import frappe

def run_debug():
    records = frappe.db.get_all('Attendance', fields=['name', 'student', 'class_section', 'date', 'status', 'docstatus'])
    print(f"Total attendance records: {len(records)}")
    for r in records:
        print(f"[{r.name}] Student: {r.student}, Class: {r.class_section}, Date: {r.date}, Status: {r.status}, DocStatus: {r.docstatus}")
