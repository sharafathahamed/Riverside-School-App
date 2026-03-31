import frappe

def update_enroll(doc,method):
    if doc.has_value_changed("status"):
        frappe.log_error(f"Student {doc.student} enrollment status changed to {doc.status}","Enrollment Audit")

def prevent_attendance_cancel(doc, method):
    if frappe.session.user != "Administrator":
        frappe.throw("Submitted Attendance cannot be cancelled. Contact Administrator.")

def prevent_result_cancel(doc, method):
    if frappe.session.user != "Administrator":
        frappe.throw("Submitted Examination Result cannot be cancelled. Contact Administrator.")