// Copyright (c) 2026, Sharaf and contributors
// For license information, please see license.txt


frappe.ui.form.on("Teacher Assignment", {
    refresh: function (frm) {
        if (frm.doc.status === "Active" && !frm.doc.__islocal) {
            frm.add_custom_button("Mark as Completed", function () {
                frappe.call({
                    method: "res_school.res_school.doctype.teacher_assignment.teacher_assignment.increment_completion",
                    args: {
                        teacher_assignment: frm.doc.name
                    },
                    callback: function (r) {
                        if (r.message) {
                            frm.reload_doc();
                            frappe.msgprint({
                                title: "Progress Updated",
                                message: `Completed Topics: <b>${r.message.completed_topics} / ${r.message.total_topics}</b><br>Completion: <b>${r.message.completion_percent}%</b>`,
                                indicator: "green"
                            });
                        }
                    }
                });
            }, "green");
        }
        if (frm.doc.status === "Completed") {
            frm.set_intro(
                `The assignment is already completed`, "green"
            );
        }
    }
}
)