# Copyright (c) 2026, Sharaf and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Teacher(Document):
    def after_insert(self):
        if self.email and not frappe.db.exists("User", self.email):
            user = frappe.get_doc({
                "doctype": "User",
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name or "",
				"send_welcome_email":1,
                "user_type": "System User",
                "role_profiles": [{
                    "doctype": "User Role Profile",
                    "role_profile": "Teacher"
                }]
            })
            user.insert(ignore_permissions=True)
            self.db_set("user", self.email)
            frappe.msgprint(
                f"User account created for {self.first_name}"
            )