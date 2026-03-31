// Copyright (c) 2026, Sharaf and contributors
// For license information, please see license.txt

frappe.query_reports["Attendance Report"] = {
	"filters": [
		{
			"fieldname": "academic_term",
			"label": __("Academic Term"),
			"fieldtype": "Link",
			"options": "Academic Term",
			"reqd": 1
		},
		{
			"fieldname": "class_section",
			"label": __("Class Section"),
			"fieldtype": "Link",
			"options": "Class Section"
		},
		{
			"fieldname": "threshold",
			"label": __("Threshold %"),
			"fieldtype": "Percent",
			"default": 60
		}
	]
};
