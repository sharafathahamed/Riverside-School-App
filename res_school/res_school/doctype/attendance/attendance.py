# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class Attendance(Document):
	def validate(self):
		self.validate_not_future()
		self.validate_enrolled()
		self.validate_duplicate()

	def validate_not_future(self):
		if getdate(self.date) > getdate(today()):
			frappe.throw("Attendance cannot be marked for a future date")

	def validate_enrolled(self):
		enrolled = frappe.db.exists("Student Enrollment", {
			"student": self.student,
			"class_section": self.class_section,
			"status": "Active"
		})
		if not enrolled:
			frappe.throw(f"Student {self.student} does not have an active ")

	def validate_duplicate(self):
		duplicate = frappe.db.exists("Attendance", {
			"student": self.student,
			"date": self.date,
			"name": ("!=", self.name)
		})
		if duplicate:
			frappe.throw(f"Attendance for {self.student} on {self.date} is already marked")