# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class FeeAssignment(Document):
	def validate(self):
		self.validate_duplicate()
		self.validate_amount_match()
		self.validate_due_date()

	def validate_duplicate(self):
		duplicate=frappe.db.exists("Fee Assignment",{
			"student":self.student,
			"academic_year":self.academic_year,
			"name":("!=",self.name)
		})
		if duplicate:
			frappe.throw("Fee Assignment is duplicate")
		
	def validate_amount_match(self):
		structure_amount = frappe.db.get_value("Fee Structure",self.fee_structure,"annual_fee_amount")
		if self.amount_due != structure_amount:
			frappe.throw("Amount Due must match the Fee Stucture amount.")
	
	def validate_due_date(self):
		if self.is_new() and getdate(self.due_date) < getdate(frappe.utils.today()):
			frappe.throw("Due Date cannot be in the past.")
	def on_update(self):
		self.sync_payment_status()

	def sync_payment_status(self):
		payment=frappe.db.exists("Fee Payment",{
			"fee_assignment": self.name,
			"docstatus": 1
		})
		if payment and self.status != "Paid":
			self.db_set("status", "Paid")
		elif not payment and self.status == "Paid":
			self.db_set("status", "Unpaid")
