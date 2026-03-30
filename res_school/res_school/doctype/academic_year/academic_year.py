# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class AcademicYear(Document):
	def validate(self):
		self.validate_date()
		self.validate_single_active_year()

	def validate_date(self):
		if getdate(self.start_date) >= getdate(self.end_date):
			frappe.throw("End date should be after start date")

	def validate_single_active_year(self):
		if self.is_active:
			existing = frappe.db.exists("Academic Year", {
				"is_active": 1,
				"name": ("!=", self.name)
			})
			if existing:
				frappe.throw(f"Academic Year {existing} is already active.")