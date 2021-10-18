# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ItemTransaction(Document):
	def validate(self):
		pass

	def before_save(self):
		#Check if there's nothing available and prevent submission
		if self.available == 0:
			frappe.throw("Selected item not available")
		
		#Check if quantity to be issued is more than what's available
		elif self.quantity > self.available:
			frappe.throw("Can not issue more than what's available")
		
		#Process transaction
		else:
			#Fetch selected item
			item = frappe.get_doc("School Item", self.item)
			
			#Fetch selected student
			student = frappe.get_doc("Student", self.student)

			#Check transaction type
			if self.status == "Returned":
				#Check if student has something else not returned
				owes = frappe.db.exists(
					"Item Transaction",
					{
						"student": self.student,
						"status": ("!=", "Returned"),
						"name": ("!=", self.name)
					}
				)
				#frappe.msgprint(owes)
				if owes:
					if student.cleared:
						student.cleared = 0
						student.save()
				
				else:
					student.cleared = 1
					student.save()

				#Add the returned items to item inventory
				item.issued = item.issued - self.quantity
				item.available = item.total - item.issued
				item.save()

			elif self.status == "Open":
				#Add to issued quantity of item
				item.issued = item.issued + self.quantity
				#Update number of available for item
				item.available = item.total - item.issued
				item.save()

				#Update student status
				if student.cleared:
					student.cleared = 0
					student.save()

				else:
					student.cleared = 0
					student.save()
