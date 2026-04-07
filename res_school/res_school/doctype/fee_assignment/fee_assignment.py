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
		duplicate = frappe.db.exists("Fee Assignment", {
			"student": self.student,
			"academic_year": self.academic_year,
			"name":("!=",self.name)
		})
		if duplicate:
			frappe.throw("Fee Assignment is duplicate")

	def validate_amount_match(self):
		structure_amount = frappe.db.get_value("Fee Structure", self.fee_structure, "annual_fee_amount")
		if self.amount_due != structure_amount:
			frappe.throw("Amount Due must match the Fee Structure amount.")

	def validate_due_date(self):
		if self.is_new() and getdate(self.due_date) < getdate(frappe.utils.today()):
			frappe.throw("Due Date cannot be in the past.")

	def after_insert(self):
		fee_payment = frappe.new_doc("Fee Payment")
		fee_payment.fee_assignment = self.name
		fee_payment.student = self.student
		fee_payment.academic_year = self.academic_year
		fee_payment.amount_paid = self.amount_due
		fee_payment.insert(ignore_permissions=True)
		frappe.msgprint(f"Fee Payment Draft Created for {self.student}")