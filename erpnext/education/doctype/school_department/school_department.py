# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

class SchoolDepartment(Document):
	def before_save(self):
		exists = frappe.db.exists("Project",{"project_name": self.name})
		if exists:
			frappe.msgprint("exist")
			for item in self.activity_list:
				check = frappe.db.exists("Task",{"subject": item.activity,"project": exists,"exp_start_date": item.from_date,"exp_end_date": item.to_date,"priority": item.priority})
				if not check:
					frappe.msgprint(str(item.activity))
					doc = frappe.get_doc({
					"doctype": "Task",
					"subject": item.activity,
					"project": exists,
					"status": "Open",
					"exp_start_date": item.from_date,
					"exp_end_date": item.to_date,
					"priority": item.priority
					})
					doc.insert()

		else:
			frappe.msgprint("does not exist")
			doc = frappe.get_doc({
			"doctype": "Project",
			"title": self.name,
			"project_name": self.name,
			"status": "Open"
			})
			doc.insert()

			for item in self.activity_list:
				check = frappe.db.exists("Task",{"subject": item.activity,"project": exists,"exp_start_date": item.from_date,"exp_end_date": item.to_date,"priority": item.priority})
				if not check:
					frappe.msgprint(str(item.activity))
					doc = frappe.get_doc({
					"doctype": "Task",
					"subject": item.activity,
					"project": exists,
					"status": "Open",
					"exp_start_date": item.from_date,
					"exp_end_date": item.to_date,
					"priority": item.priority
					})
					doc.insert()





