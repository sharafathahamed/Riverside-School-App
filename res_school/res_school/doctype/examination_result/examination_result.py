#Copyright (c) 2026, Sharaf and contributors
#For license information, please see license.txt

from email import message
import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class ExaminationResult(Document):
	def validate(self):
		self.validate_duplicate()
		self.eligible_for_exams()
		self.validate_marks()
		self.student_active_check()
		self.validate_fee_paid()
		self.grade = self.calculate_grade(self.marks_obtained)

	def validate_duplicate(self):
		duplicate = frappe.db.exists("Examination Result", {
			"examination": self.examination,
			"student": self.student,
			"name":("!=",self.name)
		})
		if duplicate:
			frappe.throw("Document with same student already exists")

	def before_submit(self):
		self.grade = self.calculate_grade(self.marks_obtained)

	def calculate_grade(self, marks):
		if marks>=90: return "A+"
		elif marks>=80: return "A"
		elif marks>=70: return "B"
		elif marks>=60: return "C"
		elif marks>=40: return "D"
		else: return "F"

	def student_active_check(self):
		class_section = frappe.db.get_value("Examination", self.examination, "class_section")
		enrolled = frappe.db.exists("Student Enrollment", {
			"student": self.student,
			"class_section": class_section,
			"status": "Active"
		})
		if not enrolled:
			frappe.throw("There is no active student for this examination result")

	def validate_marks(self):
		max_marks= frappe.db.get_value("Examination",self.examination, "max_marks")
		max_marks=float(max_marks)
		if self.marks_obtained<0:
			frappe.throw("Marks cannot be negative.")
		if self.marks_obtained>max_marks:
			frappe.throw("Marks cannot be more than maximum marks")

	def validate_fee_paid(self):
		exam = frappe.get_doc("Examination", self.examination)
		academic_year = frappe.db.get_value("Academic Term", exam.academic_term, "academic_year")
		fee_assignment = frappe.db.get_value(
			"Fee Assignment",{"student": self.student,"academic_year": academic_year},
			["name","status","amount_due","amount_paid"],
			as_dict=True
		)
		if not fee_assignment:
			frappe.throw("Please create a Fee Assignment first.")
		if fee_assignment.status != "Paid":
			frappe.throw("Fee must be paid before saving an Examination Result.")

	def eligible_for_exams(self):
		exam = frappe.get_doc("Examination", self.examination)
		term_start, term_end = frappe.db.get_value("Academic Term", exam.academic_term, ["start_date", "end_date"])
		total = frappe.db.count("Attendance", filters={
			"student":self.student,
			"class_section":exam.class_section,
			"docstatus":1,
			"date":["between", [term_start, term_end]]
		})
		if not total:
			return
		present = frappe.db.count("Attendance", filters={
			"student":self.student,
			"class_section":exam.class_section,
			"docstatus": 1,
			"date": ["between",[term_start, term_end]],
			"status": ["in", ["Present", "Late"]]
		})
		percentage = (present/total) * 100.0
		if percentage < 60.0:
			frappe.msgprint(
				f"Warning: {self.student} has only {percentage:.1f}% attendance. ",
				title="Low Attendance Warning",
				indicator="orange"
			)

	def on_load(self):
		self.check_result_withheld()

	def check_result_withheld(self):
		user_roles = frappe.get_roles(frappe.session.user)
		if "Student" not in user_roles:
			return

		exam = frappe.get_doc("Examination", self.examination)
		academic_year = frappe.db.get_value("Academic Term", exam.academic_term, "academic_year")

		fee_status = frappe.db.get_value(
			"Fee Assignment",
			{"student": self.student,"academic_year": academic_year},
			"status"
		)
		if fee_status != "Paid":
			frappe.throw("Results Withheld: Fee payment is pending.")

		term_start, term_end = frappe.db.get_value(
			"Academic Term",
			exam.academic_term,
			["start_date","end_date"]
		)
		total=frappe.db.count("Attendance", filters={
			"student":self.student,
			"class_section":exam.class_section,
			"docstatus":1,
			"date":["between",[term_start,term_end]]
		})
		if total:
			present=frappe.db.count("Attendance", filters={
				"student":self.student,
				"class_section":exam.class_section,
				"docstatus":1,
				"date": ["between",[term_start,term_end]],
				"status": ["in",["Present","Late"]]
			})
			percentage = (present / total) * 100.0
			if percentage < 60.0:
				frappe.throw("Minimum 60% required.")
	def on_update(self):
		self.notifyParentsonPublish()
	def notifyParentsonPublish(self):
		if not self.has_value_changed("workflow_state"):
			return
		if self.workflow_state!="Published":
			return
		student_doc=frappe.get_doc("Student",self.student)
		if not student_doc.guardian_email:
			return
		
		exam_name=frappe.db.get_value("Examination",self.examination,"exam_name")

		context={
			"student_name":student_doc.full_name,
			"guardian_name":student_doc.guardian_name,
			"exam_name":exam_name,
			"marks_obtained":self.marks_obtained,
			"grade":self.grade
		}
		subject=f"Examination Results Published — {student_doc.full_name}"
		message=frappe.render_template(
			"""Dear {{ guardian_name }},<br><br>
			The results for <b>{{ exam_name }}</b> have been published
			for <b>{{ student_name }}</b>.<br><br>
			Marks Obtained: <b>{{ marks_obtained }}</b><br>
			Grade: <b>{{ grade }}</b><br><br>
			Please log in to the school portal to view the full result.<br><br>
			Regards,<br>Riverside Academy
			""",context
		)
		frappe.sendmail(
			reciptients=[student_doc.guardian_email],
			subject=subject,
			message=message,
			reference_doctype="Examination Result",
			reference_name=self.name,
			now=True
		)