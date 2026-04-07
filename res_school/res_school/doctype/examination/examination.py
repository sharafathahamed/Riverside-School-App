# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class Examination(Document):
	def validate(self):
		self.validateDate()
		self.validateMark()
		self.weightage()
	def validateDate(self):
		term=frappe.db.get_value(
			"Academic Term",
			self.academic_term,
			["start_date","end_date"],
			as_dict=True
		)
		if not term:
			frappe.throw("Academic Term not found")
		if getdate(self.exam_date) > getdate(term.end_date):
			frappe.throw("Exam date cannot be after the Academic Term ")
	def validateMark(self):
		if self.max_marks<=0:
			frappe.throw("Max Marks must be greater than zero")
	def weightage(self):
		if self.weightage_percent<=0 or self.weightage_percent>100:
			frappe.throw("Weightage Must be between 1 and 100")