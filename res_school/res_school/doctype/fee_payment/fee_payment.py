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
		amount_due = frappe.db.get_value(
			"Fee Assignment", self.fee_assignment, "amount_due"
		)
		if self.amount_paid != amount_due:
			frappe.throw(
				f"Amount Paid must equal the full Amount Due of {amount_due}."
			)

	def validate_not_already_paid(self):
		existing = frappe.db.get_value(
			"Fee Assignment", self.fee_assignment, "status"
		)
		if existing == "Paid":
			frappe.throw(
				"This Fee Assignment is already marked as Paid. "
				"Cannot record another payment."
			)

	def auto_fetch_student(self):
		if self.fee_assignment and not self.student:
			self.student = frappe.db.get_value(
				"Fee Assignment", self.fee_assignment, "student"
			)

	def on_submit(self):
		self.update_fee_assignment()

	def update_fee_assignment(self):
		frappe.db.set_value("Fee Assignment", self.fee_assignment, {
			"status": "Paid",
			"amount_paid": self.amount_paid,
			"payment_date": self.payment_date
		})
		frappe.msgprint("Fee payment recorded. Fee Assignment updated to Paid.")

	def on_cancel(self):
		frappe.db.set_value("Fee Assignment", self.fee_assignment, {
			"status": "Unpaid",
			"amount_paid": 0,
			"payment_date": None
		})
		frappe.msgprint("Payment cancelled. Fee Assignment reverted to Unpaid.")