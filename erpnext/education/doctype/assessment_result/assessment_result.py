# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document
from erpnext.education.api import get_grade
from erpnext.education.api import get_assessment_details
from frappe.utils.csvutils import getlink
import erpnext.education

class AssessmentResult(Document):
	def before_save(self):
		#Format for report card naming series Studentid-grade-class-year-term
		rcnformat = f'{self.student}-{self.program}-{self.student_group}-{self.academic_year}-{self.academic_term}'
		#Check if report card for term and year for particular student exists
		exists = card_exists(rcnformat)
		if exists:
			#frappe.msgprint("Card exists")
			#Call report card validation
			validate_report_cards(rcnformat, self.course, self.total_score, self.grade, self.comment)

		"""else:
			#Create card if it doesn't exist
			rc = frappe.get_doc({
					"doctype": "Report Card",
					"student": self.student,
					"grade": self.program,
					"class_name": self.student_group,
					"year": self.academic_year,
					"term": self.academic_term
			})
			rc.insert()
			#Call report card validation
			validate_report_cards(rcnformat, self.course, self.total_score, self.grade, self.comment)"""

	def validate(self):
		rcnformat = f'{self.student}-{self.program}-{self.student_group}-{self.academic_year}-{self.academic_term}'
		erpnext.education.validate_student_belongs_to_group(self.student, self.student_group)
		self.validate_maximum_score()
		self.validate_grade()
		self.validate_duplicate()
		if self.report_card_name != rcnformat:
			self.report_card_name = rcnformat

	def validate_maximum_score(self):
		assessment_details = get_assessment_details(self.assessment_plan)
		max_scores = {}
		for d in assessment_details:
			max_scores.update({d.assessment_criteria: d.maximum_score})

		for d in self.details:
			d.maximum_score = max_scores.get(d.assessment_criteria)
			if d.score > d.maximum_score:
				frappe.throw(_("Score cannot be greater than Maximum Score"))

	def validate_grade(self):
		self.total_score = 0.0
		for d in self.details:
			d.grade = get_grade(self.grading_scale, (flt(d.score)/d.maximum_score)*100)
			self.total_score += d.score
		self.grade = get_grade(self.grading_scale, (self.total_score/self.maximum_score)*100)

	def validate_duplicate(self):
		assessment_result = frappe.get_list("Assessment Result", filters={"name": ("not in", [self.name]),
			"student":self.student, "assessment_plan":self.assessment_plan, "docstatus":("!=", 2)})
		if assessment_result:
			frappe.throw(_("Assessment Result record {0} already exists.").format(getlink("Assessment Result",assessment_result[0].name)))

def validate_report_cards(rcname, subj, total_score, grade, comment):
	
	report_card = frappe.get_doc("Report Card", rcname)
	#frappe.msgprint("Get report card doctype")
	#Check if subject is already entered in report card
	subject_entry_exists = frappe.db.exists("Report Card Subject",
	{
		"subject": subj,
		"parent": rcname
	})

	if subject_entry_exists:
		validate_report_card_details(rcname, subj, total_score, grade, comment)

	else:
		#Add entry to child table if it doesn't exist
		row = report_card.append("subjects", {
			"subject": subj
		})
		row.insert()
		validate_report_card_details(rcname, subj, total_score, grade, comment)

@frappe.whitelist()
def validate_report_card_details(rcname , rcsubject, rctotal_score, grade, teachers_comment):
	#Report card being updated
	r_card = frappe.get_doc("Report Card", rcname)
	#Update number of subjects recorded
	r_card.subjects_recorded = len(r_card.get("subjects"))

	for subject in r_card.subjects:
		if subject.subject == rcsubject:
			subject.score = rctotal_score
			subject.grade = grade
			subject.teachers_comment = teachers_comment
			r_card.save()
			#frappe.msgprint("score update")
			#Call function to validate position in subject
			validate_subject_position_in_report_card(rctotal_score, r_card.name, r_card.year, r_card.term, r_card.class_name, r_card.grade, rcsubject)
	
	#Check if record subjects exceeds 6
	if r_card.subjects_recorded >= 6:
		calculate_points(rcname)

def calculate_points(points_card_name):
	points_card_name = frappe.get_doc("Report Card", points_card_name)

	#Check which points system to use
	is_senior = frappe.get_value("Program", points_card_name.grade, "senior_secondary")

	points = 0

	optional_subjects = []
	selected_optional_subjects = []

	#Get number of compulsory subjects
	num_of_compulsory_subjects = 0

	for subject in points_card_name.subjects:
		if subject.compulsory:
			points += subject.grade
			num_of_compulsory_subjects += 1
		else:
			optional_subjects.append(subject.grade)

	if is_senior:
		sorted_optional_subjects = sorted(optional_subjects, reverse=False)

	else:
		sorted_optional_subjects = sorted(optional_subjects, reverse=True)

	#frappe.msgprint(str(is_senior))

	times_to_loop = 6 - num_of_compulsory_subjects
	loop_count = 0
	for optional_subject_score in sorted_optional_subjects:
		if times_to_loop > loop_count:
			points += optional_subject_score
			#frappe.msgprint(str(points))
			loop_count += 1

	points_card_name.points_in_best_6 = float(points)
	points_card_name.save()
	validate_attendance(points_card_name.name)
	calculate_position_in_class(points_card_name.name)

def validate_attendance(attendance_card_name):
	attendance_card = frappe.get_doc("Report Card", attendance_card_name)
	academic_term = attendance_card.term
	academic_year = attendance_card.year
	class_name = attendance_card.class_name

	all_students_attendance_in_class = []
	students_in_class = frappe.get_all("Student Attendance", filters={"student_group": class_name, "academic_term": academic_term, "academic_year": academic_year}, fields=["student"])

	#Get count of attendance for every student in class. The highest is the total number of days
	for stud in students_in_class:
		#frappe.msgprint(str(stud.student))
		all_students_attendance_in_class.append(frappe.db.count("Student Attendance", filters={'student': stud.student, "student_group": class_name, 'academic_term': academic_term, 'academic_year': academic_year}))
	
	sorted_student_attendance_in_class = sorted(all_students_attendance_in_class, reverse=True)
	#frappe.throw(str(sorted_student_attendance_in_class[0]))
	attendance_card.attendance = frappe.db.count("Student Attendance", filters={'student': attendance_card.student, "status": "Present", "student_group": class_name, 'academic_term': academic_term, 'academic_year': academic_year})
	attendance_card.out_of_attendance = sorted_student_attendance_in_class[0]
	attendance_card.save()

	validate_report_card_unpaid_fees(attendance_card.name)

def validate_report_card_unpaid_fees(fees_card_name):
	fees_card = frappe.get_doc("Report Card", fees_card_name)

	all_fees = frappe.get_all("Fees", filters={"student": fees_card.student}, fields=["outstanding_amount"])
	outstanding_amount = 0.00
	for fee in all_fees:
		outstanding_amount += fee.outstanding_amount

	fees_card.amount_unpaid = outstanding_amount
	fees_card.save()

@frappe.whitelist()
def validate_subject_position_in_report_card(ptotal_score ,pcard_name, pyear, pterm, pclass, pgrade, psubject):
	cur_subject_key = frappe.db.exists("Report Card Subject", {'parent': pcard_name})
	#casted_score = int(ptotal_score)
	#frappe.throw("Current key: " + cur_subject_key)
	report_card_names = frappe.get_all("Report Card", filters={"year":pyear, "term":pterm, "class_name":pclass, "grade":pgrade})
	unsorted_report_card_doctype_list = []
	res = []
	for report_card_name in report_card_names:
		#Store name of current iteration
		card = frappe.get_doc("Report Card", report_card_name)
		#frappe.msgprint("Position update")
		#Check if subject record exists in report cards
		subject_entry_exists = frappe.db.exists("Report Card Subject",
		{
			"subject": psubject,
			"parent": report_card_name.name
		})
		#frappe.throw("Subject: " + psubject)
		if subject_entry_exists:
			for subj in card.subjects:
				if subj.subject == psubject:
					if subject_entry_exists == cur_subject_key:
						subj_dict = {
							"subj_name": subject_entry_exists,
							"score": float(ptotal_score)
						}
						res.append(subj_dict)
					else:
						subj_dict = {
							"subj_name": subject_entry_exists,
							"score": float(subj.score)
						}
						res.append(subj_dict)
			unsorted_report_card_doctype_list.append(card)
	
	#sorted_doc_list = sorted(unsorted_report_card_doctype_list, key = lambda i: i['score'], reverse=True)
	#return unsorted_report_card_doctype_list
	sorted_res = sorted(res, key = lambda i: i['score'], reverse=True)
	index = 1
	loop_index = 0
	prev_score = 0.000000
	#Update positions
	for r in sorted_res:
		#Check if is first iteration
		if loop_index == 0:
			frappe.db.sql(""" UPDATE `tabReport Card Subject` SET position=%s WHERE name=%s""", (index, r["subj_name"]))
			#index += 1
			prev_score = r["score"]
			loop_index += 1
		else:
			if r["score"] == prev_score:
				#No need to update the score position of subject because current score iteration is the same as score of previous iteration
				frappe.db.sql(""" UPDATE `tabReport Card Subject` SET position=%s WHERE name=%s""", (index, r["subj_name"]))
			else:
				index += 1
				frappe.db.sql(""" UPDATE `tabReport Card Subject` SET position=%s WHERE name=%s""", (index, r["subj_name"]))
				#need to update the score position of subject because current score iteration is not the same as score of previous iteration
				prev_score = r["score"]
	calculate_subject_score_average(sorted_res)

def calculate_position_in_class(card_name):
	position_card = frappe.get_doc("Report Card", card_name)
	class_name = position_card.class_name
	grade_name = position_card.grade
	academic_term = position_card.term
	academic_year = position_card.year

	#Check which points system to use
	is_senior = frappe.get_value("Program", grade_name, "senior_secondary")

	report_card_names_in_class = frappe.get_all("Report Card", filters={"class_name": class_name, "grade": grade_name, "term": academic_term, "year": academic_year}, fields=["name", "points_in_best_6"])
	
	sorted_report_card_names = sorted(report_card_names_in_class, key = lambda i: i['points_in_best_6'], reverse=False)

	if not is_senior:
		sorted_report_card_names = sorted(report_card_names_in_class, key = lambda i: i['points_in_best_6'], reverse=True)

	students_in_class = len(sorted_report_card_names)
	
	index = 1
	loop_index = 0
	prev_points = 0.000000

	for p in sorted_report_card_names:
		#Check if is first iteration
		if loop_index == 0:
			frappe.db.sql(""" UPDATE `tabReport Card` SET position_in_class=%s, out_of_position=%s WHERE name=%s""", (index, students_in_class, p.name))
			prev_points = p.points_in_best_6
			loop_index += 1

		else:
			if p.points_in_best_6 == prev_points:
				#No need to update the score position of subject because current score iteration is the same as score of previous iteration
				frappe.db.sql(""" UPDATE `tabReport Card` SET position_in_class=%s, out_of_position=%s WHERE name=%s""", (index, students_in_class, p.name))
			else:
				index += 1
				frappe.db.sql(""" UPDATE `tabReport Card` SET position_in_class=%s, out_of_position=%s WHERE name=%s""", (index, students_in_class, p.name))
				prev_points = p.points_in_best_6

def calculate_subject_score_average(subject_data):
	score_sum = 0.000000
	num_of_elements = 0
	for score in subject_data:
		score_sum += score["score"]
		num_of_elements += 1
	score_average = score_sum / num_of_elements
	for subject_db_name in subject_data:
		frappe.db.sql(""" UPDATE `tabReport Card Subject` SET average=%s WHERE name=%s""", (score_average, subject_db_name["subj_name"]))

@frappe.whitelist()
def card_exists(card_name):
	return frappe.db.exists("Report Card", card_name)

@frappe.whitelist()
def generate_report_card(gen_student, gen_grade, gen_class, gen_year, gen_term):
	#Create card if it doesn't exist
	rc = frappe.get_doc({
			"doctype": "Report Card",
			"student": gen_student,
			"grade": gen_grade,
			"class_name": gen_class,
			"year": gen_year,
			"term": gen_term
	})
	rc.insert()