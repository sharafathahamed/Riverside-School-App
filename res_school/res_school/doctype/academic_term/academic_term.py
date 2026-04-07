# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class AcademicTerm(Document):
	def validate(self):
		self.validate_dates()
		self.validate_year()
		self.overlapping_yrs()

	def validate_dates(self):
		if getdate(self.start_date) >= getdate(self.end_date):
			frappe.throw("Start date must be before end date")

	def validate_year(self):
		year=frappe.get_doc("Academic Year", self.academic_year)
		if getdate(self.start_date) < getdate(year.start_date):
			frappe.throw("Term Start Date cannot be before Academic Year start date")
		if getdate(self.end_date) > getdate(year.end_date):
			frappe.throw("Term End date cannot be after Academic Year end date")

	def overlapping_yrs(self):
		overlapping = frappe.db.exists("Academic Term", [
			["name", "!=", self.name],
			["academic_year", "=", self.academic_year],
			["start_date", "<=", self.end_date],
			["end_date", ">=", self.start_date],
		])
		if overlapping:
			frappe.throw("The dates are overlapping with another term in the same year")