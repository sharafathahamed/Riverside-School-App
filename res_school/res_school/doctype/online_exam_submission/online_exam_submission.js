frappe.ui.form.on('Online Exam Submission', {
    online_exam: function (frm) {
        if (frm.doc.online_exam) {

            let has_actual_questions = frm.doc.student_answers && frm.doc.student_answers.some(r => r.question);

            if (has_actual_questions) {
                frappe.confirm('Changing the examination will completely clear the currently loaded questions. Proceed?', function () {
                    _fetch_and_load_questions(frm);
                });
            } else {
                _fetch_and_load_questions(frm);
            }
        }
    }
});

function _fetch_and_load_questions(frm) {
    frm.clear_table("student_answers");

    frappe.call({
        method: 'res_school.res_school.doctype.online_exam_submission.online_exam_submission.get_exam_questions',
        args: {
            online_exam: frm.doc.online_exam
        },
        freeze: true,
        freeze_message: ('Fetching and shuffling exam questions...'),
        callback: function (r) {
            if (r.message && r.message.length > 0) {
                r.message.forEach(function (q) {
                    let row = frm.add_child("student_answers");
                    row.question = q.name;
                    row.question_text = q.question_text;
                    row.option_a = q.option_a;
                    row.option_b = q.option_b;
                    row.option_c = q.option_c;
                    row.option_d = q.option_d;
                    row.correct_answer = q.correct_answer;
                });
                frm.refresh_field("student_answers");
                frm.fields_dict['student_answers'].grid.refresh();

                frm.set_value("status", "In Progress");
                frm.set_value("started_on", frappe.datetime.now_datetime());

                frm.save();

            } else {
                frappe.msgprint(("No questions configured for this selected Online Exam document."));
            }
        },
        error: function (r) {
            frappe.msgprint("Error fetching questions.");
        }
    });
}