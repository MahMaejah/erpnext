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
		mid_term_score = 0.00
		end_term_score = 0.00

		# Check mid-term
		mid_term_exists = False
		for criteria in self.details:
			if criteria.assessment_criteria.lower() == "Mid Term".lower():
				mid_term_exists = True
				mid_term_score = criteria.score

			elif criteria.assessment_criteria.lower() == "End of Term".lower():
				end_term_score = criteria.score
		
		#Grading Scale Comments (Auto comments)
		grading_scale = frappe.get_doc("Grading Scale", self.grading_scale)
		for interval in grading_scale.intervals:
			if interval.grade_code == self.grade:
				self.comment = interval.grade_description

		#Format for report card naming series Studentid-grade-class-year-term
		rcnformat = f'{self.student}-{self.program}-{self.student_group}-{self.academic_year}-{self.academic_term}'
		#Check if report card for term and year for particular student exists
		exists = card_exists(rcnformat)
		
		if exists:
			#Call report card validation
			validate_report_cards(rcnformat, self.course, mid_term_score, end_term_score, self.total_score, self.grade, self.comment)

		get_scores_for_previous_term(self.student, self.program, self.student_group, self.course, rcnformat)
		
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

# AUTO_COMMENTS
def add_auto_comments(current_report_card):
	# Teachers Comments on Subjects
	# Report Card Being Commented
	current_report_card = frappe.get_doc("Report Card", current_report_card)
	points = current_report_card.points_in_best_6

	# if sub_score >= 85:
	# 	print("Excellent Results")
	# elif (sub_score >= 75) and (sub_score < 85):
	# 	print("Very Good Results")
	# elif sub_score >= 60 and sub_score < 75:
	# 	print("Good Results")
	# elif sub_score >= 50 and sub_score < 60:
	# 	print("Fair Results")	
	# elif sub_score >= 0 and sub_score < 50:
	# 	print("fail")
	
	# Head Teachers/Class Teachers Comments on overall points
	
	if current_report_card.class_teacher_comment == "":
		frappe.msgprint("i am called")
		if points >= 6 and points < 10:
			current_report_card.class_teacher_comment = "Excellent Results"
			#print("Excellent Results")
		elif points >= 10 and points < 15:
			current_report_card.class_teacher_comment = "Very Good Results"
			#print("Very Good Results")
		elif points >= 15 and points < 25:
			current_report_card.class_teacher_comment = "Good Results"
			#print("Good Results")
		elif points >= 25 and points < 33:
			current_report_card.class_teacher_comment = "Fair Results"
			#print("Fair Results")
		elif points >= 33:
			current_report_card.class_teacher_comment = "Work Hard"
			#print("Work Hard")
		current_report_card.save()
		


def validate_report_cards(rcname, subj, mid_term_score, end_term_score, total_score, grade, comment):
	
	report_card = frappe.get_doc("Report Card", rcname)
	#frappe.msgprint("Get report card doctype")
	#Check if subject is already entered in report card
	subject_entry_exists = frappe.db.exists("Report Card Subject",
	{
		"subject": subj,
		"parent": rcname
	})

	if subject_entry_exists:
		validate_report_card_details(rcname, subj, mid_term_score, end_term_score, total_score, grade, comment)

	else:
		#Add entry to child table if it doesn't exist
		row = report_card.append("subjects", {
			"subject": subj
		})
		row.insert()
		validate_report_card_details(rcname, subj, mid_term_score, end_term_score, total_score, grade, comment)

@frappe.whitelist()
def validate_report_card_details(rcname , rcsubject, mid_term_score, end_term_score, rctotal_score, grade, grade_comment):
	#Report card being updated
	r_card = frappe.get_doc("Report Card", rcname)
	#Update number of subjects recorded
	r_card.subjects_recorded = len(r_card.get("subjects"))

	for subject in r_card.subjects:
		if subject.subject == rcsubject:
			subject.mid_term = mid_term_score
			subject.end_of_term = end_term_score
			subject.score = rctotal_score
			subject.grade = grade
			subject.grade_comment = grade_comment
			r_card.save()
			#frappe.msgprint("score update")
			#Call function to validate position in subject
			validate_subject_position_in_report_card(rctotal_score, r_card.name, r_card.year, r_card.term, r_card.class_name, r_card.grade, rcsubject)
			validate_subject_position_in_grade_in_report_card(rctotal_score, r_card.name, r_card.year, r_card.term, r_card.grade, rcsubject)
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
			if not is_senior:
				points += subject.score

			num_of_compulsory_subjects += 1
		else:
			optional_subjects.append(subject.grade)
			if not is_senior:
				optional_subjects.append(subject.score)

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
	add_auto_comments(points_card_name.name)

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

@frappe.whitelist()
def validate_subject_position_in_grade_in_report_card(ptotal_score ,pcard_name, pyear, pterm, pgrade, psubject):
	cur_subject_key = frappe.db.exists("Report Card Subject", {'parent': pcard_name})
	#casted_score = int(ptotal_score)
	#frappe.throw("Current key: " + cur_subject_key)
	report_card_names = frappe.get_all("Report Card", filters={"year":pyear, "term":pterm, "grade":pgrade})
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
			frappe.db.sql(""" UPDATE `tabReport Card Subject` SET position_in_grade=%s WHERE name=%s""", (index, r["subj_name"]))
			#index += 1
			prev_score = r["score"]
			loop_index += 1
		else:
			if r["score"] == prev_score:
				#No need to update the score position of subject because current score iteration is the same as score of previous iteration
				frappe.db.sql(""" UPDATE `tabReport Card Subject` SET position_in_grade=%s WHERE name=%s""", (index, r["subj_name"]))
			else:
				index += 1
				frappe.db.sql(""" UPDATE `tabReport Card Subject` SET position_in_grade=%s WHERE name=%s""", (index, r["subj_name"]))
				#need to update the score position of subject because current score iteration is not the same as score of previous iteration
				prev_score = r["score"]

def get_scores_for_previous_term(student, grade, class_name, subject,current_report_card):
	current_academic_year = frappe.db.get_single_value('Education Settings', 'current_academic_year')
	current_term = frappe.db.get_single_value('Education Settings', 'current_academic_term')
	current_term_name = frappe.db.get_value('Academic Term',current_term, 'term_name')
	current_term_number = current_term_name[5]
	previous_academic_term = 0
	previous_academic_year_number1 = int(current_academic_year[3])-1
	previous_academic_year_number2 = int(current_academic_year[6])-1
	previous_academic_year = str(current_academic_year[0:3]) + str(previous_academic_year_number1)+ "-" + str(current_academic_year[5]) + str(previous_academic_year_number2) 
	#frappe.msgprint(str(previous_academic_term))
	previous_academic_term = str(current_academic_year) + " (Term " + str(int(current_term_number)-1) + ")"
	
	if current_term_number == 1:
		current_academic_year = previous_academic_year
		previous_academic_term = str(previous_academic_year) + " (Term 3)"
	else:
		previous_academic_term = str(current_academic_year) + " (Term " + str(int(current_term_number)-1) + ")"

	previous_report_card = f'{student}-{grade}-{class_name}-{current_academic_year}-{previous_academic_term}'
	
	if frappe.db.exists('Report Card', previous_report_card):
		report_card_previous = frappe.get_doc('Report Card', previous_report_card)
		for subj in report_card_previous.subjects:
			if subj.subject == subject:
				previous_score = subj.score
				sub = frappe.db.exists('Report Card Subject', {"subject":subject,"parent":current_report_card})
				if sub:
					frappe.db.sql(""" UPDATE `tabReport Card Subject` SET score_last_term = %s WHERE name = %s """, (subj.score, sub))
					
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

	calculate_position_in_grade_best_6(card_name)

def calculate_position_in_grade_best_6(card_name):
	position_card = frappe.get_doc("Report Card", card_name)
	# class_name = position_card.class_name
	grade_name = position_card.grade
	academic_term = position_card.term
	academic_year = position_card.year

	#Check which points system to use
	is_senior = frappe.get_value("Program", grade_name, "senior_secondary")

	report_card_names_in_grade = frappe.get_all("Report Card", filters={"grade": grade_name, "term": academic_term, "year": academic_year}, fields=["name", "points_in_best_6"])
	
	sorted_report_card_names = sorted(report_card_names_in_grade, key = lambda i: i['points_in_best_6'], reverse=False)

	if not is_senior:
		sorted_report_card_names = sorted(report_card_names_in_grade, key = lambda i: i['points_in_best_6'], reverse=True)

	students_in_grade = len(sorted_report_card_names)
	
	index = 1
	loop_index = 0
	prev_points = 0.000000

	for p in sorted_report_card_names:
		#Check if is first iteration
		if loop_index == 0:
			frappe.db.sql(""" UPDATE `tabReport Card` SET position_in_grade=%s, out_of_position_in_grade=%s WHERE name=%s""", (index, students_in_grade, p.name))
			prev_points = p.points_in_best_6
			loop_index += 1

		else:
			if p.points_in_best_6 == prev_points:
				#No need to update the score position of subject because current score iteration is the same as score of previous iteration
				frappe.db.sql(""" UPDATE `tabReport Card` SET position_in_grade=%s, out_of_position_in_grade=%s WHERE name=%s""", (index, students_in_grade, p.name))
			else:
				index += 1
				frappe.db.sql(""" UPDATE `tabReport Card` SET position_in_grade=%s, out_of_position_in_grade=%s WHERE name=%s""", (index, students_in_grade, p.name))
				prev_points = p.points_in_best_6

	# calculate_position_in_grade_best_6(card_name)

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