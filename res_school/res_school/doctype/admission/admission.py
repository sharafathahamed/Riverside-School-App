# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class Admission(Document):
	def validate(self):
		self.validate_dob()

	def validate_dob(self):
		if getdate(self.admission_date) > getdate(today()):
			frappe.throw("Admission date cannot be a future date")
		if getdate(self.admission_date) < getdate(self.date_of_birth):
			frappe.throw("Admission date cannot be before date of birth")

	def on_submit(self):
		if self.status != "Approved":
			frappe.throw("Only Approved admissions can be submitted.")
		self.create_nd_enroll()

	def create_nd_enroll(self):
		if self.is_already_processed():
			return
		student = frappe.get_doc({
			"doctype": "Student",
			"full_name": self.student_name,
			"date_of_birth": self.date_of_birth,
			"guardian_name": self.guardian_name,
			"admission_date": self.admission_date
		})
		student.insert(ignore_permissions=True)
		enroll = frappe.get_doc({
			"doctype": "Student Enrollment",
			"student": student.name,
			"academic_year": self.academic_year,
			"class_section": self.class_section,
			"join_date": self.admission_date,
			"status": "Active"
		})
		enroll.insert(ignore_permissions=True)
		self.db_set("student", student.name)
		frappe.msgprint(f"Student {student.full_name} enrolled successfully")

	def is_already_processed(self):
		return frappe.db.get_value("Admission", self.name, "student")