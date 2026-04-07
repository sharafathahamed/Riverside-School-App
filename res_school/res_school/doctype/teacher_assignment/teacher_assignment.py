# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class TeacherAssignment(Document):
	def validate(self):
		self.validate_dates()
		self.validate_duplicate()
		self.validate_not_reopen()


	def validate_dates(self):
		if getdate(self.assignment_from)>=getdate(self.assignment_till):
			frappe.throw("Effective To must be after Effective From")

	def validate_duplicate(self):
		duplicate =frappe.db.exists("Teacher Assignment", {
			"teacher":self.teacher,
			"subject":self.subject,
			"class_section":self.class_section,
			"academic_term":self.academic_term,
			"name": ("!=",self.name)
		})
		if duplicate:
			frappe.throw(
				f"{self.teacher} is already assigned to teach "
				f"{self.subject} in {self.class_section} for {self.academic_term}"
			)
	def validate_not_reopen(self):
		if self.has_value_changed("status"):
			old_status=frappe.db.get_value(
				"Teacher Assignment", self.name, "status"
			)
			if old_status == "Completed" and self.status == "Active":
				frappe.throw(
					"A Completed Teacher Assignment cannot be reopened. "
					"Create a new assignment instead."
				)

@frappe.whitelist()
def increment_completion(teacher_assignment):
	sp_name = frappe.db.get_value(
		"Syllabus Progress",
		{"teacher_assignment": teacher_assignment},
		"name"
	)
	if not sp_name:
		frappe.throw("No Syllabus Progress record found for this assignment.")

	sp_doc = frappe.get_doc("Syllabus Progress", sp_name)

	if sp_doc.completed_topics >= sp_doc.total_topics:
		frappe.throw("All topics are already completed.")

	sp_doc.completed_topics += 1
	sp_doc.save(ignore_permissions=True)

	return {
		"completed_topics": sp_doc.completed_topics,
		"total_topics": sp_doc.total_topics,
		"completion_percent": sp_doc.completion_percent
	}