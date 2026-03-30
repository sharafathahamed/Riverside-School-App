# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate,today


class StudentEnrollment(Document):
	def validate(self):
		self.validate_join_date()
		self.validate_duplicate()
		self.validate_section()

	def validate_join_date(self):
		year = frappe.get_doc("Academic Year", self.academic_year)
		if getdate(self.join_date) < getdate(year.start_date):
			frappe.throw(
				"Join Date cannot be before the Academic Year start date."
			)
		if getdate(self.join_date) > getdate(year.end_date):
			frappe.throw(
				"Join Date cannot be after the Academic Year end date."
			)

	def validate_duplicate(self):
		existing = frappe.db.exists("Student Enrollment",{
			"student":self.student,
			"academic_year": self.academic_year,
			"status": "Active",
			"name":("!=",self.name)
		})
		if existing:
			frappe.throw(
				f"Student already exists"
			)

	def validate_section(self):
		section_year = frappe.db.get_value(
			"Class Section", self.class_section, "academic_year"
		)
		if section_year != self.academic_year:
			frappe.throw(
				"Class Section is not in academic year"
			)
