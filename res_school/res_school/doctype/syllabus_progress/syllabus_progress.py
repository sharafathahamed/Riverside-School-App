# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SyllabusProgress(Document):
	def validate(self):
		self.validateTopics()
		self.calculateCompletion()
	def validateTopics(self):
		if self.total_topics<=0:
			frappe.throw("Total topics should be more than one")
		if self.completed_topics<0:
			frappe.throw("Completed Topics cannot be negative")
		if self.completed_topics>self.total_topics:
			frappe.throw("Completed topics cannot be more than Total Topics")
	def calculateCompletion(self):
		self.completion_percent=round(
			(self.completed_topics / self.total_topics) *100,1
		)
		if self.completion_percent<50:
			self.status="Behind Schedule"
		elif self.completion_percent<80:
			self.status="On Track"
		else:
			self.status="Completed"