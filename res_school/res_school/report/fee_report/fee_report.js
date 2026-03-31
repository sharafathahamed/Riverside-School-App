// Copyright (c) 2026, Sharaf and contributors
// For license information, please see license.txt

frappe.query_reports["Fee Report"] = {
	"filters": [
		{
			"fieldname": "academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year",
			"reqd": 1
		},
		{
			"fieldname": "class_section",
			"label": __("Class Section"),
			"fieldtype": "Link",
			"options": "Class Section"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nUnpaid\nPaid\nWaived"
		}
	]
};
