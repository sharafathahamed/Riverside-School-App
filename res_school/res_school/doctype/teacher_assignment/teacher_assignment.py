# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class TeacherAssignment(Document):
	def validate(self):
		self.validate_dates()
		self.validate_duplicate()

	def validate_dates(self):
		if getdate(self.effective_from) >= getdate(self.effective_to):
			frappe.throw("Effective To must be after Effective From")

	def validate_duplicate(self):
		duplicate = frappe.db.exists("Teacher Assignment", {
			"teacher": self.teacher,
			"subject": self.subject,
			"class_section": self.class_section,
			"academic_term": self.academic_term,
			"name": ("!=", self.name)
		})
		if duplicate:
			frappe.throw(
				f"{self.teacher} is already assigned to teach "
				f"{self.subject} in {self.class_section} for {self.academic_term}"
			)