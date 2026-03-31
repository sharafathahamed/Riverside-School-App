# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OnlineExam(Document):
	def validate(self):
		self.set_pool_size()
		self.validate_question_count()
		self.validate_enough_questions()

	def set_pool_size(self):
		self.total_questions_in_pool = len(self.questions_pool or [])

	def validate_question_count(self):
		if self.questions_per_student <= 0:
			frappe.throw("Questions Per Student must be greater than zero")

	def validate_enough_questions(self):
		pool_size = self.total_questions_in_pool
		if pool_size < self.questions_per_student:
			frappe.throw(
				f"Add more questions to the pool till {self.questions_per_student}"
			)