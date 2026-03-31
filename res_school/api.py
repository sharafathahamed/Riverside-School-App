@frappe.whitelist()
def get_online_exam_for_student(student):
    # get class section of the student
    enrollment = frappe.db.get_value(
        "Student Enrollment",
        {"student": student, "status": "Active"},
        "class_section"
    )
    if not enrollment:
        frappe.throw("No active enrollment found")

    # get active exams allocated to this student's section
    exams = frappe.get_all(
        "Online Exam",
        filters={
            "class_section": enrollment,
            "status": "Active",
            "docstatus": 1
        },
        fields=["name", "exam_name", "subject", "total_questions"]
    )

    # filter out already submitted exams
    available = []
    for exam in exams:
        already_submitted = frappe.db.exists("Online Exam Submission", {
            "online_exam": exam.name,
            "student": student,
            "status": "Submitted"
        })
        if not already_submitted:
            available.append(exam)

    return available


@frappe.whitelist()
def get_shuffled_questions(online_exam, student):
    import random
    submitted = frappe.db.exists("Online Exam Submission", {
        "online_exam": online_exam,
        "student": student,
        "status": "Submitted"
    })
    if submitted:
        frappe.throw("You have already submitted this exam.")

    exam = frappe.get_doc("Online Exam", online_exam)

    pool = [row.question for row in exam.question_pool]

    selected = random.sample(pool, min(exam.total_questions, len(pool)))

    random.shuffle(selected)

    questions = []
    for q_name in selected:
        q = frappe.get_doc("Question Bank", q_name)
        options = [
            {"key": "A", "text": q.option_a},
            {"key": "B", "text": q.option_b},
            {"key": "C", "text": q.option_c},
            {"key": "D", "text": q.option_d},
        ]
        random.shuffle(options)

        correct_text = {
            "A": q.option_a, "B": q.option_b,
            "C": q.option_c, "D": q.option_d
        }[q.correct_answer]

        new_correct = next(
            o["key"] for o in options if o["text"] == correct_text
        )

        questions.append({
            "question": q.name,
            "question_text": q.question_text,
            "option_a": options[0]["text"],
            "option_b": options[1]["text"],
            "option_c": options[2]["text"],
            "option_d": options[3]["text"],
            "shuffled_correct": new_correct
        })

    return questions


@frappe.whitelist()
def submit_online_exam(online_exam, student, answers):
    import json

    if isinstance(answers, str):
        answers = json.loads(answers)

    submitted = frappe.db.exists("Online Exam Submission", {
        "online_exam": online_exam,
        "student": student,
        "status": "Submitted"
    })
    if submitted:
        frappe.throw("You have already submitted this exam.")

    existing = frappe.db.exists("Online Exam Submission", {
        "online_exam": online_exam,
        "student": student,
        "status": "In Progress"
    })

    if existing:
        submission = frappe.get_doc("Online Exam Submission", existing)
        submission.student_answers = []
    else:
        submission = frappe.get_doc({
            "doctype": "Online Exam Submission",
            "online_exam": online_exam,
            "student": student,
            "status": "In Progress"
        })

    for ans in answers:
        q = frappe.get_doc("Question Bank", ans["question"])
        submission.append("student_answers", {
            "question": ans["question"],
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "selected_answer": ans["selected_answer"]
        })

    if existing:
        submission.save(ignore_permissions=True)
    else:
        submission.insert(ignore_permissions=True)

    submission.submit()

    return {
        "total_marks": submission.total_marks,
        "total_questions": len(answers),
        "message": "Exam submitted successfully"
    }