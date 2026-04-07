# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(data)
    return columns, data, None, None, summary


def get_columns():
    return [
        {
            "fieldname": "student",
            "label": "Student",
            "fieldtype": "Link",
            "options": "Student",
            "width": 140
        },
        {
            "fieldname": "full_name",
            "label": "Full Name",
            "fieldtype": "Data",
            "width": 160
        },
        {
            "fieldname": "class_section",
            "label": "Class Section",
            "fieldtype": "Link",
            "options": "Class Section",
            "width": 140
        },
        {
            "fieldname": "academic_year",
            "label": "Academic Year",
            "fieldtype": "Link",
            "options": "Academic Year",
            "width": 110
        },
        {
            "fieldname": "amount_due",
            "label": "Amount Due",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "due_date",
            "label": "Due Date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "payment_date",
            "label": "Payment Date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "guardian_name",
            "label": "Guardian",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "fieldname": "guardian_email",
            "label": "Guardian Email",
            "fieldtype": "Data",
            "width": 180
        },
    ]


def get_data(filters):
    academic_year = filters.get("academic_year")
    status_filter = filters.get("status")
    class_section = filters.get("class_section")
    if not academic_year:
        return []
    assignment_filters = {"academic_year": academic_year}
    if status_filter:
        assignment_filters["status"] = status_filter
    assignments = frappe.get_all(
        "Fee Assignment",
        filters=assignment_filters,
        fields=[
            "student",
            "academic_year",
            "amount_due",
            "due_date",
            "status",
            "payment_date"
        ]
    )
    data = []

    for a in assignments:
        student_doc = frappe.get_doc("Student", a.student)

        if class_section:
            enrolled = frappe.db.exists("Student Enrollment", {
                "student": a.student,
                "class_section": class_section,
                "academic_year": academic_year
            })
            if not enrolled:
                continue
            section = class_section
        else:
            section = frappe.db.get_value(
                "Student Enrollment",
                {
                    "student": a.student,
                    "academic_year": academic_year
                },
                "class_section"
            ) or "Not Enrolled"

        if a.status == "Paid":
            display_status = "Paid"
        elif a.status == "Unpaid":
            display_status = "Unpaid"
        elif a.status == "Waived":
            display_status = "Waived"
        else:
            display_status = a.status

        data.append({
            "student": a.student,
            "full_name": student_doc.full_name,
            "class_section": section,
            "academic_year": a.academic_year,
            "amount_due": a.amount_due,
            "due_date": a.due_date,
            "status": display_status,
            "payment_date": a.payment_date or "Not Paid",
            "guardian_name": student_doc.guardian_name,
            "guardian_email": student_doc.guardian_email or "Not Available"
        })

    status_order = {"Unpaid": 0, "Paid": 1, "Waived": 2}
    data.sort(key=lambda x: status_order.get(x["status"], 3))

    return data


def get_summary(data):
    if not data:
        return []

    total_due = sum(r["amount_due"] for r in data)

    paid_rows= [r for r in data if r["status"] == "Paid"]
    unpaid_rows= [r for r in data if r["status"] == "Unpaid"]

    total_paid   = sum(r["amount_due"] for r in paid_rows)
    total_unpaid = sum(r["amount_due"] for r in unpaid_rows)

    return [
        {
            "label": "Total Students",
            "value": len(data),
            "datatype": "Int",
            "indicator": "blue"
        },
        {
            "label": "Total Amount Due",
            "value": total_due,
            "datatype": "Currency",
            "indicator": "blue"
        },
        {
            "label": "Total Collected",
            "value": total_paid,
            "datatype": "Currency",
            "indicator": "green"
        },
        {
            "label": "Total Outstanding",
            "value": total_unpaid,
            "datatype": "Currency",
            "indicator": "red"
        },
        {
            "label": "Paid Count",
            "value": len(paid_rows),
            "datatype": "Int",
            "indicator": "green"
        },
        {
            "label": "Unpaid Count",
            "value": len(unpaid_rows),
            "datatype": "Int",
            "indicator": "red"
        },
    ]