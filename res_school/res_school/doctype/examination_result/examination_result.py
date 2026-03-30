# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class ExaminationResult(Document):
	def validate(self):
		self.validate_duplicate()
		self.eligible_for_exams()
		self.validate_marks()
		self.student_active_check()
		self.grade = self.calculate_grade(self.marks_obtained)

	def validate_duplicate(self):
		duplicate=frappe.db.exists("Examination Result",{
			"examination":self.examination,
			"student":self.student,
			"name":("!=",self.name)
		})
		if duplicate:
			frappe.throw("Document with same student already exists")
	def before_submit(self):
		self.grade=self.calculate_grade(self.marks_obtained)
	def calculate_grade(self,marks):
		if marks >= 90: return "A+"
		elif marks >= 80: return "A"
		elif marks >= 70: return "B"
		elif marks >= 60: return "C"
		elif marks >= 40: return "D"
		else: return "F"
	def student_active_check(self):
		class_section = frappe.db.get_value(
            "Examination", self.examination, "class_section"
        )
		enrolled = frappe.db.exists("Student Enrollment", {
            "student": self.student,
            "class_section": class_section,
            "status": "Active"
        })
		if not enrolled:
			frappe.throw("There is no active students for examination result")
	def validate_marks(self):
		max_marks=frappe.db.get_value("Examination",self.examination,"max_marks")
		max_marks = float(max_marks)

		if self.marks_obtained<0:
			frappe.throw("Marks Cannot be negative.")
		if self.marks_obtained>max_marks:
			frappe.throw("Marks cannot be more than maximum marks")
	def eligible_for_exams(self):
		exam=frappe.get_doc("Examination",self.examination)
		term_start,term_end=frappe.db.get_value(
			"Academic Term",
			exam.academic_term,
			["start_date","end_date"]
		)
		total=frappe.db.count("Attendance",
			filters={
				"student":self.student,
				"class_section":exam.class_section,
				"docstatus":1,
				"date":["between",[term_start,term_end]]
			}
		)
		if not total:
			return
		present=frappe.db.count("Attendance",filters={
			"student":self.student,
			"class_section":exam.class_section,
			"docstatus":1,
			"date":["between",[term_start,term_end]],
			"status":["in",["Present","Late"]]
		})
		percentage=(present/total)*100.0
		if percentage<60.0:
			frappe.msgprint(
				f"Warning: {self.student} has only {percentage:.1f}% attendance. "
				f"Minimum 60% required.",
				title="Low Attendance Warning",
				indicator="orange"
			)
		