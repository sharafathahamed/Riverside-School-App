# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FeePayment(Document):
	def validate(self):
		self.validate_amount()
		self.validate_not_already_paid()
		self.auto_fetch_student()
	
	def validate_amount(self):
		amount_due = frappe.db.get_value("Fee Assignment",self.fee_assignment,"amount_due")
		if self.amount_paid != amount_due:
			frappe.throw(
				f"Amount Paid must equal the full Amount Due. So provide the due amount"
			)

	def validate_not_already_paid(self):
		existing_payment = frappe.db.exists("Fee Payment", {
			"fee_assignment": self.fee_assignment,
			"docstatus": 1,
			"name": ("!=", self.name)
		})
		if existing_payment:
			frappe.throw("A payment has already been recorded for this ")

	def auto_fetch_student(self):
		if self.fee_assignment and not self.student:
			self.student = frappe.db.get_value("Fee Assignment",self.fee_assignment,"student")

	def on_submit(self):
		frappe.db.set_value("Fee Assignment",self.fee_assignment,"status", "Paid")
		
		frappe.db.set_value("Fee Assignment",self.fee_assignment,"payment_date", self.payment_date)

		frappe.msgprint("Fee payment recorded. Thank You!")
	def on_cancel(self):
		frappe.db.set_value("Fee Assignment",self.fee_assignment,"status", "Unpaid")

		frappe.db.set_value("Fee Assignment",self.fee_assignment,"payment_date", None)

		frappe.msgprint("Payment cancelled. Fee Assignment reverted to Unpaid.")

