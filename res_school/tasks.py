# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, getdate

def send_low_alert():
	active_enroll = frappe.get_all(
		"Student Enrollment",
		filters={
			"status": "Active",
			"academic_year": get_active_academic_year()
		},
		fields=["student", "class_section", "academic_year"]
	)
	for enrollment in active_enroll:
		check_and_alert(enrollment)

def get_active_academic_year():
	return frappe.db.get_value("Academic Year", {"is_active": 1}, "name")

def check_and_alert(enroll):
	student = enroll.student
	class_section = enroll.class_section
	term = frappe.db.get_value(
		"Academic Term",
		{
			"academic_year": enroll.academic_year,
			"start_date": ["<=", today()],
			"end_date": [">=", today()]
		},
		["name", "start_date", "end_date"],
		as_dict=True
	)
	if not term:
		return
	total = frappe.db.count("Attendance", filters={
		"student": student,
		"class_section": class_section,
		"docstatus": 1,
		"date": ["between", [term.start_date, term.end_date]]
	})
	if not total:
		return
	present = frappe.db.count("Attendance", filters={
		"student": student,
		"class_section": class_section,
		"docstatus": 1,
		"date": ["between", [term.start_date, term.end_date]],
		"status": ["in", ["Present", "Late"]]
	})
	percentage = (present / total) * 100.0
	if percentage < 60.0:
		send_alert_email(student, class_section, percentage, present, total)

def send_alert_email(student, class_section, percentage, present, total):
	student_doc = frappe.get_doc("Student", student)
	if not student_doc.guardian_email:
		frappe.log_error(
			f"No guardian email for {student}",
			"Attendance Alert"
		)
		return
	context = {
		"student_name": student_doc.full_name,
		"guardian_name": student_doc.guardian_name,
		"class_section": class_section,
		"attendance_percent": f"{percentage:.1f}",
		"present": present,
		"total": total
	}
	template = frappe.get_doc("Email Template", "Low Attendance Alert")
	subject = frappe.render_template(template.subject, context)
	message = frappe.render_template(template.response, context)
	frappe.sendmail(
		recipients=[student_doc.guardian_email],
		subject=subject,
		message=message,
		reference_doctype="Student",
		reference_name=student,
		now=True
	)
def fee_overdue_alert():
		overdue=frappe.get_all(
			"Fee Assignment",
			filters={
				"status":"Unpaid",
				"due_date":["<",today()]
			},
			fields=["name","student","amount_due","due_date","academic_year"]
		)
		for fee in overdue:
			student_doc=frappe.get_doc("Student",fee.student)
			if not student_doc.guardian_email:
				continue
			context={
				"student_name":student_doc.full_name,
				"guardian_name": student_doc.guardian_name,
				"amount_due":fee.amount_due,
				"due_date":str(fee.due_date),
				"academic_year":fee.academic_year
			}
			subject = f"Fee Overdue — {student_doc.full_name}"
			message = frappe.render_template(
				"""Dear {{ guardian_name }},<br><br>
				This is a reminder that the fee of <b>₹{{ amount_due }}</b>
				for <b>{{ student_name }}</b> was due on <b>{{ due_date }}</b>
				and is still unpaid.<br><br>
				Please clear the dues at the earliest.<br><br>
				Regards,<br>Riverside Academy""",
				context
			)
			frappe.sendmail(
				recipients=[student_doc.guardian_email],
				subject=subject,
				message=message,
				reference_doctype="Fee Assignment",
				reference_name=fee.name,
				now=True
			)