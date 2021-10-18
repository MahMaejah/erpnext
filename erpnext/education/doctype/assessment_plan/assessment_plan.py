# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe import _

class AssessmentPlan(Document):
	def before_save(self):
		sic = frappe.get_doc("Student Group", self.student_group)
		for student in sic.students:
			rcnformat = f'{student.student}-{self.program}-{self.student_group}-{self.academic_year}-{self.academic_term}'
			#Check if report card record doesn't exist for each pupil in class and create one
			if not frappe.db.exists("Report Card", rcnformat):
				#Create report card
				rc = frappe.get_doc({
					"doctype": "Report Card",
					"student": student.student,
					"grade": self.program,
					"class_name": self.student_group,
					"year": self.academic_year,
					"term": self.academic_term
				})
				rc.insert()
			#frappe.msgprint(student.student)
		#Get list of students in selected class
		#students_in_class = frappe.db.get_all('Student', filters={''})
		#students = frappe.db.get_all('Report Card', filters={'year': self.academic_year, 'term': self.academic_term, 'grade': self.student_group}, fields=['student'])

	def validate(self):
		self.validate_overlap()
		self.validate_max_score()
		self.validate_assessment_criteria()

	def validate_overlap(self):
		"""Validates overlap for Student Group, Instructor, Room"""

		from erpnext.education.utils import validate_overlap_for

		#Validate overlapping course schedules.
		if self.student_group:
			validate_overlap_for(self, "Course Schedule", "student_group")

		validate_overlap_for(self, "Course Schedule", "instructor")
		validate_overlap_for(self, "Course Schedule", "room")

		#validate overlapping assessment schedules.
		if self.student_group:
			validate_overlap_for(self, "Assessment Plan", "student_group")

		validate_overlap_for(self, "Assessment Plan", "room")
		validate_overlap_for(self, "Assessment Plan", "supervisor", self.supervisor)

	def validate_max_score(self):
		max_score = 0
		for d in self.assessment_criteria:
			max_score += d.maximum_score
		if self.maximum_assessment_score != max_score:
			frappe.throw(_("Sum of Scores of Assessment Criteria needs to be {0}.").format(self.maximum_assessment_score))

	def validate_assessment_criteria(self):
		assessment_criteria_list = frappe.db.sql_list(''' select apc.assessment_criteria
			from `tabAssessment Plan` ap , `tabAssessment Plan Criteria` apc
			where ap.name = apc.parent and ap.course=%s and ap.student_group=%s and ap.assessment_group=%s
			and ap.name != %s and ap.docstatus=1''', (self.course, self.student_group, self.assessment_group, self.name))
		for d in self.assessment_criteria:
			if d.assessment_criteria in assessment_criteria_list:
				frappe.throw(_("You have already assessed for the assessment criteria {}.")
					.format(frappe.bold(d.assessment_criteria)))
