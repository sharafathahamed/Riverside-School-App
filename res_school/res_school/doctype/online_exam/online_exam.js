frappe.ui.form.on("Online Exam Submission", {
    refresh: function (frm) {
        if (frm.doc.status === "In Progress" && frm.doc.docstatus === 0) {
            frm.add_custom_button("Regenerate Questions", function () {
                frappe.call({
                    method: "res_school.res_school.api.get_shuffled_questions",
                    args: {
                        online_exam: frm.doc.online_exam,
                        student: frm.doc.student
                    },
                    callback: function (r) {
                        if (r.message) {
                            frm.clear_table("student_answers");
                            r.message.forEach(function (q) {
                                let row = frm.add_child("student_answers");
                                row.question = q.question;
                                row.question_text = q.question_text;
                                row.option_a = q.option_a;
                                row.option_b = q.option_b;
                                row.option_c = q.option_c;
                                row.option_d = q.option_d;
                            });
                            frm.refresh_field("student_answers");
                            frappe.msgprint("Questions reshuffled!");
                        }
                    }
                });
            }, "orange");
        }

        if (frm.doc.status === "Submitted") {
            frm.set_intro(
                `Exam submitted. You scored ${frm.doc.total_marks} marks.`,
                "green"
            );
        }
    }
});