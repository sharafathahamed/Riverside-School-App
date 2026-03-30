# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class Student(Document):
	def validate(self):
		self.validate_dob()
		self.validate_admission_date()

	def validate_dob(self):
		if getdate(self.date_of_birth) >= getdate(today()):
			frappe.throw("Date of birth cannot be today or a future date")

	def validate_admission_date(self):
		if getdate(self.admission_date) > getdate(today()):
			frappe.throw("Admission date cannot be a future date")
		if getdate(self.admission_date) < getdate(self.date_of_birth):
			frappe.throw("Admission date cannot be before date of birth")