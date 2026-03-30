# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FeeStructure(Document):
	def validate(self):
		self.validate_amount()
		self.validate_duplicate()
	def validate_amount(self):
		if self.annual_fee_amount<=0:
			frappe.throw("Annual Fee Amount must be greater than zero.")
	
	def validate_duplicate(self):
		duplicate=frappe.db.exists("Fee Structure",{
			"academic_year":self.academic_year,
			"grade_level":self.grade_level,
			"name":("!=",self.name)
		})
		if duplicate:
			frappe.throw("Fee structure is duplicate")