# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class Admission(Document):
	def validate(self):
		self.calculate_age()
		self.validate_dob()

	def calculate_age(self):
		if self.date_of_birth:
			dob = getdate(self.date_of_birth)
			today_date = getdate(today())

			self.age = today_date.year - dob.year
			if (today_date.month, today_date.day) < (dob.month, dob.day):
				self.age -= 1

	def validate_dob(self):
		if getdate(self.admission_date) > getdate(today()):
			frappe.throw("Admission date cannot be a future date")
			
		if self.date_of_birth and self.admission_date:
			dob = getdate(self.date_of_birth)
			adm_date = getdate(self.admission_date)
			
			age_at_admission = adm_date.year - dob.year
			if (adm_date.month, adm_date.day) < (dob.month, dob.day):
				age_at_admission -= 1
				
			if age_at_admission < 3: 
				frappe.throw("Admission date must be after 3 years from date of birth")

	def on_submit(self):
		if self.status != "Approved":
			frappe.throw("Only Approved admissions can be submitted.")
		self.create_nd_enroll()

	def create_nd_enroll(self):
		if self.is_already_processed():
			return
		student = frappe.get_doc({
			"doctype": "Student",
			"full_name": self.student_name,
			"date_of_birth": self.date_of_birth,
			"age":self.age,
			"guardian_name": self.guardian_name,
			"admission_date": self.admission_date
		})
		student.insert(ignore_permissions=True)
		enroll = frappe.get_doc({
			"doctype": "Student Enrollment",
			"student": student.name,
			"academic_year": self.academic_year,
			"class_section": self.class_section,
			"join_date": self.admission_date,
			"status": "Active"
		})
		enroll.insert(ignore_permissions=True)
		self.db_set("student", student.name)
		frappe.msgprint(f"Student {student.full_name} enrolled successfully")

	def is_already_processed(self):
		return frappe.db.get_value("Admission", self.name, "student")