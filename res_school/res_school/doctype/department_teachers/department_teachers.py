# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet


class DepartmentTeachers(NestedSet):
	def autoname(self):
		if self.is_group:
			namin=self.department_name.strip().replace(" ", "-")
			self.name=f"DEPT-{namin}"
		else:
			slug = self.teacher.strip().replace(" ", "-")
			self.name=f"{self.employee_id}-{slug}"
			
	def on_update(self):
		if not self.is_group and self.teacher and self.parent_department_teachers:
			frappe.db.set_value(
				"Teacher", 
				self.teacher, 
				"department", 
				self.parent_department_teachers
			)