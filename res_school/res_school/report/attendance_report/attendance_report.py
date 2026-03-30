# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"fieldname": "student", "label": "Student", "fieldtype": "Link", "options": "Student", "width": 160},
		{"fieldname": "full_name", "label": "Full Name", "fieldtype": "Data", "width": 160},
		{"fieldname": "class_section", "label": "Class Section", "fieldtype": "Link", "options": "Class Section", "width": 140},
		{"fieldname": "total_days", "label": "Total Days", "fieldtype": "Int", "width": 100},
		{"fieldname": "present_days", "label": "Present", "fieldtype": "Int", "width": 90},
		{"fieldname": "absent_days", "label": "Absent", "fieldtype": "Int", "width": 90},
		{"fieldname": "late_days", "label": "Late", "fieldtype": "Int", "width": 80},
		{"fieldname": "attendance_percent", "label": "Attendance %", "fieldtype": "Float", "width": 120},
		{"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 120},
		{"fieldname": "guardian_name", "label": "Guardian", "fieldtype": "Data", "width": 140},
		{"fieldname": "guardian_email", "label": "Guardian Email", "fieldtype": "Data", "width": 180},
	]

def get_data(filters):
	threshold = filters.get("threshold") or 60
	academic_term = filters.get("academic_term")
	class_section = filters.get("class_section")

	if not academic_term:
		return []

	term = frappe.db.get_value(
		"Academic Term",
		{"name": academic_term},
		["name", "start_date", "end_date"],
		as_dict=True
	)

	if not term:
		frappe.throw(f"Academic Term '{academic_term}' not found.")

	enrollment_filters = {"status": "Active"}
	if class_section:
		enrollment_filters["class_section"] = class_section

	enrollments = frappe.get_all(
		"Student Enrollment",
		filters=enrollment_filters,
		fields=["student", "class_section"]
	)

	data = []

	for enrollment in enrollments:
		student = enrollment.student
		section = enrollment.class_section

		total = frappe.db.count("Attendance", filters={
			"student": student,
			"class_section": section,
			"docstatus": 1,
			"date": ["between", [term.start_date, term.end_date]]
		})

		if not total:
			continue

		present = frappe.db.count("Attendance", filters={
			"student": student, "class_section": section, "docstatus": 1,
			"date": ["between", [term.start_date, term.end_date]], "status": "Present"
		})
		absent = frappe.db.count("Attendance", filters={
			"student": student, "class_section": section, "docstatus": 1,
			"date": ["between", [term.start_date, term.end_date]], "status": "Absent"
		})
		late = frappe.db.count("Attendance", filters={
			"student": student, "class_section": section, "docstatus": 1,
			"date": ["between", [term.start_date, term.end_date]], "status": "Late"
		})

		percentage = ((present + late) / total) * 100.0

		if percentage < threshold:
			student_doc = frappe.get_doc("Student", student)
			if percentage < 40:
				status = "Critical"
			elif percentage < 60:
				status = "At Risk"
			else:
				status = "Warning"

			data.append({
				"student": student,
				"full_name": student_doc.full_name,
				"class_section": section,
				"total_days": total,
				"present_days": present,
				"absent_days": absent,
				"late_days": late,
				"attendance_percent": round(percentage, 1),
				"status": status,
				"guardian_name": student_doc.guardian_name,
				"guardian_email": student_doc.guardian_email or "Not Available"
			})

	data.sort(key=lambda x: x["attendance_percent"])
	return data