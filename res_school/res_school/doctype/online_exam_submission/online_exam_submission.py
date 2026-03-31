import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
import random

class OnlineExamSubmission(Document):
	def before_save(self):
		if not self.online_exam:
			return
			
		exam = frappe.get_doc("Online Exam", self.online_exam)
		allowed_count = exam.questions_per_student

		if len(self.student_answers) > allowed_count:
			frappe.throw("Questions can't be beyond Questions Per Student")
		attend_ques = set()
		for row in self.student_answers:
			if row.question:
				if row.question in attend_ques:
					frappe.throw("questions are duplicate please select another")
				attend_ques.add(row.question)

	def before_submit(self):
		self.status = "Submitted"
		if not self.submitted_on:
			self.submitted_on = now_datetime()
		self.calculate_marks()

	def calculate_marks(self):
		total_q = 0
		obtained = 0
		for answer in self.student_answers:
			total_q += 1
			real_correct_answer = frappe.db.get_value("Question Bank", answer.question, "correct_answer")
			
			if answer.selected_answer and answer.selected_answer == real_correct_answer:
				answer.is_correct = 1
				obtained += 1
			else:
				answer.is_correct = 0		
		self.total_questions = total_q
		self.total_marks = total_q
		self.marks_obtained = obtained

		if total_q > 0:
			self.percentage = (obtained / total_q) * 100
		else:
			self.percentage = 0.0

		if self.percentage >= 90: self.grade = "A+"
		elif self.percentage >= 80: self.grade = "A"
		elif self.percentage >= 70: self.grade = "B+"
		elif self.percentage >= 60: self.grade = "B"
		elif self.percentage >= 50: self.grade = "C"
		elif self.percentage >= 40: self.grade = "D"
		else: self.grade = "F"

	def on_submit(self):
		if not self.examination:
			return
		if not frappe.db.exists("Examination Result", {"examination": self.examination, "student": self.student}):
			doc = frappe.get_doc({
				"doctype": "Examination Result",
				"examination": self.examination,
				"student": self.student,
				"grade": self.grade,
				"marks_obtained": self.marks_obtained
			})
			doc.insert(ignore_permissions=True)


@frappe.whitelist()
def get_exam_questions(online_exam):
	exam = frappe.get_doc("Online Exam", online_exam)
	
	if not exam.questions_pool:
		return []
		
	required_count = exam.questions_per_student or len(exam.questions_pool)
	pool_question_ids = [row.question for row in exam.questions_pool if row.question]
	
	if len(pool_question_ids) < required_count:
		frappe.throw(f"Exam pool requires at least {required_count} questions but only has {len(pool_question_ids)}.")
		
	selected_ids = random.sample(pool_question_ids, required_count)
	random.shuffle(selected_ids)
	
	questions = []
	for q_id in selected_ids:
		question = frappe.get_doc("Question Bank", q_id)
		questions.append({
			"name": question.name,
			"question_text": question.question_text,
			"option_a": question.option_a,
			"option_b": question.option_b,
			"option_c": question.option_c,
			"option_d": question.option_d,
			"correct_answer": question.correct_answer
		})
		
	return questions