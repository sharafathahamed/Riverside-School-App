# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class Student(Document):
	def validate(self):
		self.calculate_age()
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

	def calculate_age(self):
		if self.date_of_birth:
			dob = getdate(self.date_of_birth)
			today_date = getdate(today())

			self.age = today_date.year - dob.year
			if (today_date.month, today_date.day) < (dob.month, dob.day):
				self.age -= 1
			
	def after_insert(self):
		if not frappe.db.exists("User", {"email": self.guardian_email}):
			user = frappe.get_doc({
				"doctype": "User",
				"email": self.guardian_email,
				"first_name": self.full_name,
				"user_type": "System User",
				"role_profiles": [{
					"doctype": "User Role Profile",
					"role_profile": "Student"
				}]
			})
			user.insert(ignore_permissions=True)
			frappe.db.set_value("Student", self.name, "user", self.guardian_email)