import frappe
from res_school.tasks import get_active_academic_year, check_and_alert
from frappe.utils import today

def run_debug():
    year = get_active_academic_year()
    print(f"Active Academic Year: {year}")
    
    active_enroll=frappe.get_all(
        "Student Enrollment",
        filters={
            "status":"Active",
            "academic_year":year
        },
        fields=["name", "student","class_section","academic_year"]
    )
    print(f"Found active enrollments: {len(active_enroll)}")
    for e in active_enroll:
        print(f"Checking enrollment for student {e.student} (Section: {e.class_section})")
        term=frappe.db.get_value(
            "Academic Term",
            {
                "academic_year": e.academic_year,
                "start_date": ["<=", today()],
                "end_date": [">=", today()]
            },
            ["name", "start_date", "end_date"],
            as_dict=True
        )
        print(f"  Term: {term}")
        if not term:
            continue
        total=frappe.db.count("Attendance", filters={
            "student": e.student,
            "class_section": e.class_section,
            "docstatus": 1,
            "date": ["between", [term.start_date, term.end_date]]
        })
        print(f"  Total Attendance Records: {total}")
        if not total:
            continue
        present=frappe.db.count("Attendance", filters={
            "student": e.student,
            "class_section": e.class_section,
            "docstatus": 1,
            "date": ["between", [term.start_date, term.end_date]],
            "status":["in",["Present","Late"]]
        })
        percentage=(present/total)*100
        print(f"  Present: {present}, Percentage: {percentage}")
        if percentage < 60.0:
            print("  ALERT WOULD TRIGGER!")
        else:
            print("  NO ALERT NEEDED.")
