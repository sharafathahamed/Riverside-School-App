frappe.ui.form.on("Admission", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0 && frm.doc.status === "Waiting List") {
            frm.add_custom_button("Approve", function() {
                frappe.confirm(
                    "Are you sure you want to Approve this admission?",
                    function() {
                        frm.set_value("status", "Approved");
                        frm.save().then(function() {
                            frm.savesubmit();
                        });
                    }
                );
            }, "Action");

            frm.add_custom_button("Reject", function() {
                frappe.prompt(
                    {
                        label: "Rejection Reason",
                        fieldname: "reason",
                        fieldtype: "Small Text",
                        reqd: 1
                    },
                    function(values) {
                        frm.set_value("status", "Rejected");
                        frm.set_value("remarks", values.reason);
                        frm.save();
                    },
                    "Reason for Rejection",
                    "Reject"
                );
            }, "Action");
        }
        if (frm.doc.docstatus === 1) {
            frm.set_intro(
                `This admission is Approved. Student ${frm.doc.student} has been enrolled.`,
                "green"
            );
        }
        if (frm.doc.status === "Rejected") {
            frm.set_intro(
                "This admission has been Rejected.",
                "red"
            );
        }
    }
});