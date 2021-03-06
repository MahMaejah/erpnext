# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from warnings import filters
import frappe
import json
import datetime
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, cstr, getdate
from frappe.email.doctype.email_group.email_group import add_subscribers

@frappe.whitelist()
def report_card_disbursement(class_name):
	#Get acdemic year and term
	year = frappe.db.get_single_value("Education Settings", "current_academic_year")
	term = frappe.db.get_single_value("Education Settings", "current_academic_term")
	
	#Get class doctype
	class_doc = frappe.get_doc("Student Group", class_name)

	#Get all students in class
	for student in class_doc.current_students:
		#Get report cards and trigger release
		report_card_exists = frappe.db.exists("Report Card", {"student": student.student, "year": year, "term": term})

		if report_card_exists:
			report_card = frappe.get_doc("Report Card", report_card_exists)
			report_card.is_released = 1
			report_card.save()

def assign_next_class(class_doc,student):
	previous_class_enrollment = frappe.get_doc("Student Group",str(class_doc.next_class))
	
	previous_class_enrollment.append("students",{
	"student": student.student,
	"student_name": student.student_name,
	"active": student.active
	}
	)
	#frappe.set_value("Program Enrollmenrt",student_enrollment,'student_batch_name',next_class.b
	previous_class_enrollment.save()

@frappe.whitelist()
def migrate_forward():
	# region Chipos Solution
	
	c_room = "Grade 10 Science"
	c_grade = "Grade 10"

	#Get all students and change the Grade and Class
	class_doc = frappe.get_doc("Student Group", c_room)
	for student in class_doc.students:
		if class_doc.next_class != None and class_doc.next_class != "":
			#frappe.msgprint(f'{student.student}')
			student_doc = frappe.get_doc("Student", student.student)
			student_doc.grade = class_doc.next_grade
			student_doc.class_name = class_doc.next_class
			student_doc.save()

			#Get student program enrollment doctype and change the academic term and year to current, and student batch
			program_enrollment_doc_name = frappe.db.exists("Program Enrollment", {"student": student.student})
			program_enrollment_doc = frappe.get_doc("Program Enrollment", program_enrollment_doc_name)
			#frappe.msgprint(f'{program_enrollment_doc.name}')

			##
			#program_enrollment_doc.student_batch_name = f'{class_doc.next_grade} Section'
			#program_enrollment_doc.db_set('student_batch_name', f'{class_doc.next_grade} Section')
			#st = frappe.db.sql("""SELECT * FROM `tabProgram Enrollment` WHERE student=%s""", (student.student), as_dict=1)
			#frappe.errprint(st)
			frappe.db.sql("""UPDATE `tabProgram Enrollment` SET student_batch_name=%s, program=%s WHERE student=%s """, (f'{class_doc.next_grade} Section', class_doc.next_grade, student.student))
			#frappe.errprint("""UPDATE `tabProgram Enrollment` SET student_batch_name=%s, program=%s WHERE student=%s """, (f'{class_doc.next_grade} Section', class_doc.next_grade, student))""")

			##

			#frappe.errprint(f'Next Section: {class_doc.next_grade} Section')
			#program_enrollment_doc.program = class_doc.next_grade
			#program_enrollment_doc.save()
			#program_enrollment_doc.submit()

	return

	#endregion

	groupList = frappe.get_all("Student Group")
	enrollmentList = frappe.get_all('Program Enrollment')
	GradeList = []
	studentEnrolls = []


	for group in groupList:
		doc = frappe.get_doc("Student Group",group['name'])
		GradeList.append(int(str(doc.program)[6:].replace(" ","")))
	for enroll in enrollmentList:
		doc = frappe.get_doc("Program Enrollment",enroll['name'])
		studentEnrolls.append(doc)
	
	#? shift year and term

	eduSettings = frappe.get_single("Education Settings")	
	frappe.msgprint(str(eduSettings.current_academic_year))
	#? academic year
	new_academic_year = frappe.new_doc("Academic Year")
	current_year = str(eduSettings.current_academic_year)
	# to_year = str(current_year)[5:7]			
	# from_year = str(current_year)[2:4]			
	# new_to_year = str(int(to_year)+1)			
	# new_academic_year.academic_year_name = str(eduSettings.current_academic_year).replace(to_year,new_to_year).replace(from_year,to_year)
	splitYear = str(current_year).split('-')
	new_academic_year.academic_year_name = f'{int(splitYear[0])+1}-{int(splitYear[1])+1}'
	new_academicYear = f'{int(splitYear[0])+1}-{int(splitYear[1])+1}'
	# # new_academic_year.year_start_date = f"01-01-{str(new_academic_year.academic_year_name)[0:4]}"
	# new_academic_year.year_end_date = f"31-12-{str(new_academic_year.academic_year_name)[0:4]}"
	exists =  frappe.db.exists("Academic Year",new_academic_year)
	eduSettings.current_academic_year = new_academic_year.academic_year_name
	if exists:
		name = new_academic_year.academic_year_name
		new_academic_year = frappe.get_doc('Academic Year',name)
	else:
		try:
			new_academic_year.insert()
		except:
			frappe.msgprint("---")
	

	frappe.msgprint(str(eduSettings.current_academic_year))

	termName = ""
	#? academic term
	for i in range(1,4):
		termDoc = frappe.new_doc('Academic Term')
		termDoc.academic_year = new_academic_year.academic_year_name
		termDoc.term_name = f'Term {i}'
		termDoc.title = f'{termDoc.academic_year} ({termDoc.term_name})'
		term_exists = frappe.db.exists('Academic Term',termDoc.title)
		if i == 1:
			termName = f'{termDoc.academic_year} ({termDoc.term_name})'
			eduSettings.current_academic_term = termDoc.title
			frappe.msgprint(str(eduSettings.current_academic_term))
		if term_exists:
			continue
		else:
			termDoc.insert()

	eduSettings.save()
	#? end shifting year
	GradeList.sort(reverse=True)
	for gradeNum in GradeList:
		for group in groupList:
			class_doc = frappe.get_doc("Student Group", group['name'])
			class_doc.academic_term = termName
			class_doc.academic_year = new_academicYear
			if str(gradeNum) in str(class_doc.program):
				groupList.remove(group)
				frappe.msgprint(f'Program {class_doc.program}')
				#class_doc.previous_students = class_doc.students
				class_doc.previous_students.clear()
				for student in class_doc.students:
					if class_doc.next_class != None and class_doc.next_class != "":
						frappe.msgprint(f'{student.student}')
						student_doc = frappe.get_doc("Student", student.student)
						student_doc.grade = class_doc.next_grade
						student_doc.class_name = class_doc.next_class
						student_doc.save()

						#Get student program enrollment doctype and change the academic term and year to current, and student batch
						program_enrollment_doc_name = frappe.db.exists("Program Enrollment", {"student": student.student})
						program_enrollment_doc = frappe.get_doc("Program Enrollment", program_enrollment_doc_name)
						program_enrollment_doc.student_batch_name = f'{class_doc.next_grade} Section'
						program_enrollment_doc.save()
						previous_class_enrollment = frappe.get_doc("Student Group",str(class_doc.next_class))
						class_doc.append("previous_students",{
						"student": student.student,
						"student_name": student.student_name,
						"active": student.active
						})
						
						previous_class_enrollment = frappe.get_doc("Student Group",str(class_doc.next_class))
						
						previous_class_enrollment.append("current_students",{
						"student": student.student,
						"student_name": student.student_name,
						"active": student.active
						}
						)
						#program_class_enrollment.student_batch_name = f'{class_doc.next_grade} Section'
						#frappe.set_value("Program Enrollmenrt",student_enrollment,'student_batch_name',next_class.batch)
						previous_class_enrollment.save()

				#region oldcode
					"""
					class_doc.append("previous_students",{
						"student": student.student,
						"student_name": student.student_name,
						"active": student.active
						})
					
					if class_doc.next_class != None:
						student_enrollment = None
						for stu in studentEnrolls:
							if stu.student == student.student:
								student_enrollment = stu
								break
						if student_enrollment:
							# frappe.msgprint("Enrollment: " + str(student_enrollment))
							next_class = frappe.get_doc("Student Group",str(class_doc.next_class))
							# frappe.msgprint("Next Class: " + str(next_class.batch))
							# frappe.msgprint(f'Previous enrollment: {student_enrollment.student_batch_name}')
							student_enrollment.student_batch_name=next_class.batch
							# frappe.msgprint(f'New enrollment: {student_enrollment.student_batch_name}')
							student_enrollment.save()
							student.save()
							frappe.db.commit()

							enrolled = frappe.db.exists("Program Enrollment", {
								"student_batch_name": student_enrollment.student_batch_name
							})
							# assign_next_class(class_doc,student)
							# frappe.msgprint("Enrolled is: " + str(enrolled))

							previous_class_enrollment = frappe.get_doc("Student Group",str(class_doc.next_class))
							
							previous_class_enrollment.append("current_students",{
							"student": student.student,
							"student_name": student.student_name,
							"active": student.active
							}
							)
							program_class_enrollment.student_batch_name = f'{class_doc.next_grade} Section'
							#frappe.set_value("Program Enrollmenrt",student_enrollment,'student_batch_name',next_class.batch)

							previous_class_enrollment.save()
					"""
					#endregion
				
				# class_doc.current_students.clear()
				class_doc.save()
				frappe.msgprint(f'{len(class_doc.previous_students)}')

				"""
				else:
					if len(class_doc.previous_students) > 0:
						for student in class_doc.previous_students:
							class"""
	
	#?region ExtendYears
	highest_year = getHighestYear()
	diff = int(str(highest_year.academic_year_name)[0:4]) - int(str(new_academic_year.academic_year_name)[0:4]) 
	if(diff <= 3):
		extendAcadmicYearDocType();
	#?endregion

@frappe.whitelist()
def migrate_reverse():
	"""
	c_room = "Grade 11 Science"
	c_grade = "Grade 11"

	#Get all students and change the Grade and Class
	class_doc = frappe.get_doc("Student Group", c_room)
	for student in class_doc.students:
		if class_doc.previous_class != None and class_doc.previous_class != "":
			frappe.msgprint(f'{student.student}')
			student_doc = frappe.get_doc("Student", student.student)
			student_doc.grade = class_doc.previous_grade
			student_doc.class_name = class_doc.previous_class
			student_doc.save()

	#students = frappe.get_all("Student", filters={})
	return
"""
	groupList = frappe.get_all("Student Group")
	enrollmentList = frappe.get_all('Program Enrollment')
	GradeList = []
	studentEnrolls = []


	for group in groupList:
		doc = frappe.get_doc("Student Group",group['name'])
		GradeList.append(int(str(doc.program)[6:].replace(" ","")))
	for enroll in enrollmentList:
		doc = frappe.get_doc("Program Enrollment",enroll['name'])
		studentEnrolls.append(doc)
		#? shift year and term

	eduSettings = frappe.get_single("Education Settings")	
	frappe.msgprint(str(eduSettings.current_academic_year))
	#? academic year
	new_academic_year = frappe.new_doc("Academic Year")
	current_year = str(eduSettings.current_academic_year)
	# to_year = str(current_year)[5:7]			#22
	# from_year = str(current_year)[2:4]			#21
	# new_from_year = str(int(from_year)-1)			#20
	# ogFront = str(current_year)[0:2]
	splitYear = str(current_year).split('-')
	new_academic_year.academic_year_name = f'{int(splitYear[0])-1}-{int(splitYear[1])-1}'
	new_academicYear = f'{int(splitYear[0])-1}-{int(splitYear[1])-1}'
	# new_academic_year.year_start_date = f"01-01-{str(new_academic_year.academic_year_name)[0:4]}"
	# new_academic_year.year_end_date = f"31-12-{str(new_academic_year.academic_year_name)[0:4]}"
	exists =  frappe.db.exists("Academic Year",new_academic_year)
	eduSettings.current_academic_year = new_academic_year.academic_year_name
	if exists:
		name = new_academic_year.academic_year_name
		new_academic_year = frappe.get_doc('Academic Year',name)
	else:
		try:
			new_academic_year.insert()
		except:
			frappe.msgprint("---")
	

	frappe.msgprint(str(eduSettings.current_academic_year))
	termName = ""

	#? academic term
	for i in range(1,4):
		termDoc = frappe.new_doc('Academic Term')
		termDoc.academic_year = new_academic_year.academic_year_name
		termDoc.term_name = f'Term {i}'
		termDoc.title = f'{termDoc.academic_year} ({termDoc.term_name})'
		term_exists = frappe.db.exists('Academic Term',termDoc.title)
		
		if i == 1:
			termName = f'{termDoc.academic_year} ({termDoc.term_name})'
			eduSettings.current_academic_term = termDoc.title
			frappe.msgprint(str(eduSettings.current_academic_term))
		if term_exists:
			continue
		else:
			termDoc.insert()

	eduSettings.save()
	# ? end shifting
	GradeList.sort(reverse=False)
	for gradeNum in GradeList:
		for group in groupList:
			class_doc = frappe.get_doc("Student Group", group['name'])
			class_doc.academic_term = termName
			class_doc.academic_year = new_academicYear
			if str(gradeNum) in str(class_doc.program):
				groupList.remove(group)
				frappe.msgprint(f'Program {class_doc.program}')
				#class_doc.previous_students = class_doc.students
				class_doc.current_students.clear()
				for student in class_doc.previous_students:
					if class_doc.previous_class != None and class_doc.previous_class != "":
						frappe.msgprint(f'{student.student}')
						student_doc = frappe.get_doc("Student", student.student)
						student_doc.grade = class_doc.previous_grade
						student_doc.class_name = class_doc.previous_class
						student_doc.save()
						"""
					class_doc.append("current_students",{
						"student": student.student,
						"student_name": student.student_name,
						"active": student.active
						})
					
					if class_doc.previous_class != None:
						student_enrollment = None
						for stu in studentEnrolls:
							if stu.student == student.student:
								student_enrollment = stu
								break
						if student_enrollment:
							frappe.msgprint("Enrollment: " + str(student_enrollment))
							previous_class = frappe.get_doc("Student Group",str(class_doc.previous_class))
							frappe.msgprint("Next Class: " + str(previous_class.batch))
							frappe.msgprint(f'Previous enrollment: {student_enrollment.student_batch_name}')
							student_enrollment.student_batch_name=previous_class.batch
							frappe.msgprint(f'New enrollment: {student_enrollment.student_batch_name}')
							student_enrollment.save()
							student.save()
							frappe.db.commit()
							# assign_next_class(class_doc,student)
							# frappe.msgprint("Enrolled is: " + str(enrolled))

							previous_class_enrollment = frappe.get_doc("Student Group",str(class_doc.previous_class))
							
							previous_class_enrollment.append("previous_students",{
							"student": student.student,
							"student_name": student.student_name,
							"active": student.active
							}
							)
							#frappe.set_value("Program Enrollmenrt",student_enrollment,'student_batch_name',next_class.batch)

							previous_class_enrollment.save()
					
				class_doc.previous_students.clear()
							"""
				class_doc.save()
				frappe.msgprint(f'{len(class_doc.previous_students)}')

	

@frappe.whitelist()
def get_current_academic_year():
	current_year = frappe.db.get_single_value("Education Settings", "current_academic_year")
	current_year_analysis = frappe.db.sql("""SELECT COUNT(points_in_best_6), class_name, points_in_best_6, year, term FROM `tabReport Card` WHERE year = %s GROUP BY points_in_best_6, class_name""", (current_year), as_dict=1)
	return current_year_analysis

@frappe.whitelist()
def department_subject_analysis(dep_name):
	if frappe.db.count('Course', {'department': dep_name}) > 0:
		subject_list = frappe.get_list('Course', filters={'department': dep_name}, fields=['name'])
		#  arr = []
		#  for sub in subject_list:
		# 	 arr.append(sub)

		default_subject = subject_list[0].name
		current_year = frappe.db.get_single_value("Education Settings", "current_academic_year")
		current_year_analysis = frappe.db.sql("""SELECT COUNT(total_score), student_group, total_score, academic_year, academic_term FROM `tabAssessment Result` WHERE academic_year = %s AND course = %s GROUP BY student_group""", (current_year, default_subject), as_dict=1)
		return current_year_analysis 
	else: 
		return "nothing" 


def get_course(program):
	'''Return list of courses for a particular program
	:param program: Program
	'''
	courses = frappe.db.sql('''select course, course_name from `tabProgram Course` where parent=%s''',
			(program), as_dict=1)
	return courses


@frappe.whitelist()
def enroll_student(source_name):
	"""Creates a Student Record and returns a Program Enrollment.

	:param source_name: Student Applicant.
	"""
	frappe.publish_realtime('enroll_student_progress', {"progress": [1, 4]}, user=frappe.session.user)
	student = get_mapped_doc("Student Applicant", source_name,
		{"Student Applicant": {
			"doctype": "Student",
			"field_map": {
				"name": "student_applicant"
			}
		}}, ignore_permissions=True)
	student.save()
	program_enrollment = frappe.new_doc("Program Enrollment")
	program_enrollment.student = student.name
	program_enrollment.student_category = student.student_category
	program_enrollment.student_name = student.title
	program_enrollment.program = frappe.db.get_value("Student Applicant", source_name, "program")
	frappe.publish_realtime('enroll_student_progress', {"progress": [2, 4]}, user=frappe.session.user)
	return program_enrollment


@frappe.whitelist()
def check_attendance_records_exist(course_schedule=None, student_group=None, date=None):
	"""Check if Attendance Records are made against the specified Course Schedule or Student Group for given date.

	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""
	if course_schedule:
		return frappe.get_list("Student Attendance", filters={"course_schedule": course_schedule})
	else:
		return frappe.get_list("Student Attendance", filters={"student_group": student_group, "date": date})


@frappe.whitelist()
def mark_attendance(students_present, students_absent, course_schedule=None, student_group=None, date=None):
	"""Creates Multiple Attendance Records.

	:param students_present: Students Present JSON.
	:param students_absent: Students Absent JSON.
	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""

	if student_group:
		academic_year = frappe.db.get_value('Student Group', student_group, 'academic_year')
		if academic_year:
			year_start_date, year_end_date = frappe.db.get_value('Academic Year', academic_year, ['year_start_date', 'year_end_date'])
			if getdate(date) < getdate(year_start_date) or getdate(date) > getdate(year_end_date):
				frappe.throw(_('Attendance cannot be marked outside of Academic Year {0}').format(academic_year))

	present = json.loads(students_present)
	absent = json.loads(students_absent)

	for d in present:
		make_attendance_records(d["student"], d["student_name"], "Present", course_schedule, student_group, date)

	for d in absent:
		make_attendance_records(d["student"], d["student_name"], "Absent", course_schedule, student_group, date)

	frappe.db.commit()
	frappe.msgprint(_("Attendance has been marked successfully."))


def make_attendance_records(student, student_name, status, course_schedule=None, student_group=None, date=None):
	"""Creates/Update Attendance Record.

	:param student: Student.
	:param student_name: Student Name.
	:param course_schedule: Course Schedule.
	:param status: Status (Present/Absent)
	"""
	cur_academic_term = frappe.db.get_single_value("Education Settings", "current_academic_term")
	cur_academic_year = frappe.db.get_single_value("Education Settings", "current_academic_year")

	student_attendance = frappe.get_doc({
		"doctype": "Student Attendance",
		"student": student,
		"course_schedule": course_schedule,
		"student_group": student_group,
		"date": date
	})
	if not student_attendance:
		student_attendance = frappe.new_doc("Student Attendance")
	student_attendance.student = student
	student_attendance.student_name = student_name
	student_attendance.course_schedule = course_schedule
	student_attendance.student_group = student_group
	student_attendance.date = date
	student_attendance.status = status
	student_attendance.academic_term = cur_academic_term
	student_attendance.academic_year = cur_academic_year
	student_attendance.save()
	student_attendance.submit()


@frappe.whitelist()
def get_student_guardians(student):
	"""Returns List of Guardians of a Student.

	:param student: Student.
	"""
	guardians = frappe.get_list("Student Guardian", fields=["guardian"] ,
		filters={"parent": student})
	return guardians


@frappe.whitelist()
def get_student_group_students(student_group, include_inactive=0):
	"""Returns List of student, student_name in Student Group.

	:param student_group: Student Group.
	"""
	if include_inactive:
		students = frappe.get_list("Student Group Student", fields=["student", "student_name"] ,
			filters={"parent": student_group}, order_by= "group_roll_number")
	else:
		students = frappe.get_list("Student Group Student", fields=["student", "student_name"] ,
			filters={"parent": student_group, "active": 1}, order_by= "group_roll_number")
	return students


@frappe.whitelist()
def get_fee_structure(program, academic_term=None):
	"""Returns Fee Structure.

	:param program: Program.
	:param academic_term: Academic Term.
	"""
	fee_structure = frappe.db.get_values("Fee Structure", {"program": program,
		"academic_term": academic_term}, 'name', as_dict=True)
	return fee_structure[0].name if fee_structure else None


@frappe.whitelist()
def get_fee_components(fee_structure):
	"""Returns Fee Components.

	:param fee_structure: Fee Structure.
	"""
	if fee_structure:
		fs = frappe.get_list("Fee Component", fields=["fees_category", "description", "amount"] , filters={"parent": fee_structure}, order_by= "idx")
		return fs


@frappe.whitelist()
def get_fee_schedule(program, student_category=None):
	"""Returns Fee Schedule.

	:param program: Program.
	:param student_category: Student Category
	"""
	fs = frappe.get_list("Program Fee", fields=["academic_term", "fee_structure", "due_date", "amount"] ,
		filters={"parent": program, "student_category": student_category }, order_by= "idx")
	return fs


@frappe.whitelist()
def collect_fees(fees, amt):
	paid_amount = flt(amt) + flt(frappe.db.get_value("Fees", fees, "paid_amount"))
	total_amount = flt(frappe.db.get_value("Fees", fees, "total_amount"))
	frappe.db.set_value("Fees", fees, "paid_amount", paid_amount)
	frappe.db.set_value("Fees", fees, "outstanding_amount", (total_amount - paid_amount))
	return paid_amount


@frappe.whitelist()
def get_course_schedule_events(start, end, filters=None):
	"""Returns events for Course Schedule Calendar view rendering.

	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Course Schedule", filters)

	data = frappe.db.sql("""select name, course, color,
			timestamp(schedule_date, from_time) as from_datetime,
			timestamp(schedule_date, to_time) as to_datetime,
			room, student_group, 0 as 'allDay'
		from `tabCourse Schedule`
		where ( schedule_date between %(start)s and %(end)s )
		{conditions}""".format(conditions=conditions), {
			"start": start,
			"end": end
			}, as_dict=True, update={"allDay": 0})

	return data


@frappe.whitelist()
def get_assessment_criteria(course):
	"""Returns Assessmemt Criteria and their Weightage from Course Master.

	:param Course: Course
	"""
	return frappe.get_list("Course Assessment Criteria", \
		fields=["assessment_criteria", "weightage"], filters={"parent": course}, order_by= "idx")


@frappe.whitelist()
def get_assessment_students(assessment_plan, student_group):
	student_list = get_student_group_students(student_group)
	for i, student in enumerate(student_list):
		result = get_result(student.student, assessment_plan)
		if result:
			student_result = {}
			for d in result.details:
				student_result.update({d.assessment_criteria: [cstr(d.score), d.grade]})
			student_result.update({
				"total_score": [cstr(result.total_score), result.grade],
				"comment": result.comment
			})
			student.update({
				"assessment_details": student_result,
				"docstatus": result.docstatus,
				"name": result.name
			})
		else:
			student.update({'assessment_details': None})
	return student_list


@frappe.whitelist()
def get_assessment_details(assessment_plan):
	"""Returns Assessment Criteria  and Maximum Score from Assessment Plan Master.

	:param Assessment Plan: Assessment Plan
	"""
	return frappe.get_list("Assessment Plan Criteria", \
		fields=["assessment_criteria", "maximum_score", "docstatus"], filters={"parent": assessment_plan}, order_by= "idx")


@frappe.whitelist()
def get_result(student, assessment_plan):
	"""Returns Submitted Result of given student for specified Assessment Plan

	:param Student: Student
	:param Assessment Plan: Assessment Plan
	"""
	results = frappe.get_all("Assessment Result", filters={"student": student,
		"assessment_plan": assessment_plan, "docstatus": ("!=", 2)})
	if results:
		return frappe.get_doc("Assessment Result", results[0])
	else:
		return None


@frappe.whitelist()
def get_grade(grading_scale, percentage):
	"""Returns Grade based on the Grading Scale and Score.

	:param Grading Scale: Grading Scale
	:param Percentage: Score Percentage Percentage
	"""
	grading_scale_intervals = {}
	if not hasattr(frappe.local, 'grading_scale'):
		grading_scale = frappe.get_all("Grading Scale Interval", fields=["grade_code", "threshold"], filters={"parent": grading_scale})
		frappe.local.grading_scale = grading_scale
	for d in frappe.local.grading_scale:
		grading_scale_intervals.update({d.threshold:d.grade_code})
	intervals = sorted(grading_scale_intervals.keys(), key=float, reverse=True)
	for interval in intervals:
		if flt(percentage) >= interval:
			grade = grading_scale_intervals.get(interval)
			break
		else:
			grade = ""
	return grade


@frappe.whitelist()
def mark_assessment_result(assessment_plan, scores):
	student_score = json.loads(scores);
	assessment_details = []
	for criteria in student_score.get("assessment_details"):
		assessment_details.append({
			"assessment_criteria": criteria,
			"score": flt(student_score["assessment_details"][criteria])
		})
	assessment_result = get_assessment_result_doc(student_score["student"], assessment_plan)
	assessment_result.update({
		"student": student_score.get("student"),
		"assessment_plan": assessment_plan,
		"comment": student_score.get("comment"),
		"total_score":student_score.get("total_score"),
		"details": assessment_details
	})
	assessment_result.save()
	details = {}
	for d in assessment_result.details:
		details.update({d.assessment_criteria: d.grade})
	assessment_result_dict = {
		"name": assessment_result.name,
		"student": assessment_result.student,
		"total_score": assessment_result.total_score,
		"grade": assessment_result.grade,
		"details": details
	}
	return assessment_result_dict


@frappe.whitelist()
def submit_assessment_results(assessment_plan, student_group):
	total_result = 0
	student_list = get_student_group_students(student_group)
	for i, student in enumerate(student_list):
		doc = get_result(student.student, assessment_plan)
		if doc and doc.docstatus==0:
			total_result += 1
			doc.submit()
	return total_result


def get_assessment_result_doc(student, assessment_plan):
	assessment_result = frappe.get_all("Assessment Result", filters={"student": student,
			"assessment_plan": assessment_plan, "docstatus": ("!=", 2)})
	if assessment_result:
		doc = frappe.get_doc("Assessment Result", assessment_result[0])
		if doc.docstatus == 0:
			return doc
		elif doc.docstatus == 1:
			frappe.msgprint(_("Result already Submitted"))
			return None
	else:
		return frappe.new_doc("Assessment Result")


@frappe.whitelist()
def update_email_group(doctype, name):
	if not frappe.db.exists("Email Group", name):
		email_group = frappe.new_doc("Email Group")
		email_group.title = name
		email_group.save()
	email_list = []
	students = []
	if doctype == "Student Group":
		students = get_student_group_students(name)
	for stud in students:
		for guard in get_student_guardians(stud.student):
			email = frappe.db.get_value("Guardian", guard.guardian, "email_address")
			if email:
				email_list.append(email)
	add_subscribers(name, email_list)

@frappe.whitelist()
def get_current_enrollment(student, academic_year=None):
	current_academic_year = academic_year or frappe.defaults.get_defaults().academic_year
	program_enrollment_list = frappe.db.sql('''
		select
			name as program_enrollment, student_name, program, student_batch_name as student_batch,
			student_category, academic_term, academic_year
		from
			`tabProgram Enrollment`
		where
			student = %s and academic_year = %s
		order by creation''', (student, current_academic_year), as_dict=1)

	if program_enrollment_list:
		return program_enrollment_list[0]
	else:
		return None

@frappe.whitelist()
def extendAcadmicYearDocType():
	'''' Grading Scale-Percentage Grading
		3. Academic year and Term Format has to be strict
		4. Assesment Criteria - End of Term and Midterm
		5. Autocomments inculding the data inside the doctype'''

	current_year = datetime.datetime.now().year
	
	current_year_pre = int(str(current_year)[0:2])

	current_year_sur = int(str(current_year)[2:])

	end_year = current_year_sur + 51
	
	for x in range(current_year_sur,end_year):
		used_current_year = current_year_pre;
		used_x = x
		if x >= 100:
			used_current_year += 1
			used_x = x -100;

		new_academic_year = frappe.new_doc("Academic Year")
		new_academic_year.academic_year_name = str(used_current_year)+str(used_x)+'-'+str(used_x+1 if used_x + 1 <100 else x-100)
		new_academic_year.year_start_date = f'{str(new_academic_year.academic_year_name)[0:4]}-01-01'
		new_academic_year.year_end_date = f'{str(new_academic_year.academic_year_name)[0:4]}-12-31'
	
		try:
			exists =  frappe.db.exists("Academic Year",new_academic_year.academic_year_name)
			if exists:
			# name = new_academic_year.academic_year_name
			# new_academic_year = frappe.get_doc('Academic Year',name)
				new_acadamic_year = frappe.get_doc("Academic Year",new_academic_year.academic_year_name)
				new_academic_year.year_start_date = f'{str(new_academic_year.academic_year_name)[0:4]}-01-01'
				new_academic_year.year_end_date = f'{str(new_academic_year.academic_year_name)[0:4]}-12-31'
				new_academic_year.save()
				frappe.msgprint("exists")
				continue
			else:
				new_academic_year.insert()
		except:
			continue
			#try:
			# except:
			# 	frappe.msgprint("---")


	 	#new_academic_year.save()
		for i in range(1,4):
			termDoc = frappe.new_doc('Academic Term')
			termDoc.academic_year = new_academic_year.academic_year_name
			termDoc.term_name = f'Term {i}'
			termDoc.title = f'{termDoc.academic_year} ({termDoc.term_name})'
			term_exists = frappe.db.exists('Academic Term',termDoc.title)
			if term_exists:
				continue
			else:
				termDoc.insert()

def getHighestYear():
	year_list = frappe.get_all("Academic Year")
	# frappe.msgprint(str(year_list))
	# return
	largest_year = 0;
	current_index = 0
	for x in year_list:
		temp = x['name'][2:4]
		if str(temp).isnumeric():
			if int(temp) > largest_year:
				largest_year = int(temp)
				current_index = year_list.index(x)
	year = frappe.get_doc("Academic Year",year_list[current_index]['name'])
	return year


@frappe.whitelist()
def insertAcadmicYearDocType():

	'''' Grading Scale-Percentage Grading
		3. Academic year and Term Format has to be strict
		4. Assesment Criteria - End of Term and Midterm
		5. Autocomments inculding the data inside the doctype'''

	current_year = datetime.datetime.now().year
	current_year_pre = int(str(current_year)[0:2])
	current_year_sur = int(str(current_year)[2:])

	for x in range(current_year_sur,51):
		used_current_year = current_year_pre;
		used_x = x
		if x >= 100:
			used_current_year += 1
			used_x = x -100;

		new_academic_year = frappe.new_doc("Academic Year")
		new_academic_year.academic_year_name = str(used_current_year)+str(used_x)+'-'+str(used_x+1 if used_x + 1 <100 else x-100)
		new_academic_year.year_start_date = f'{str(new_academic_year.academic_year_name)[0:4]}-01-01'
		new_academic_year.year_end_date = f'{str(new_academic_year.academic_year_name)[0:4]}-12-31'
	
		try:
			exists =  frappe.db.exists("Academic Year",new_academic_year.academic_year_name)
			if exists:
			# name = new_academic_year.academic_year_name
			# new_academic_year = frappe.get_doc('Academic Year',name)
				new_acadamic_year = frappe.get_doc("Academic Year",new_academic_year.academic_year_name)
				new_academic_year.year_start_date = f'{str(new_academic_year.academic_year_name)[0:4]}-01-01'
				new_academic_year.year_end_date = f'{str(new_academic_year.academic_year_name)[0:4]}-12-31'
				new_academic_year.save()
				frappe.msgprint("exists")
				continue
			else:
				new_academic_year.insert()
		except:
			continue
			#try:
			# except:
			# 	frappe.msgprint("---")


	 	#new_academic_year.save()
		for i in range(1,4):
			termDoc = frappe.new_doc('Academic Term')
			termDoc.academic_year = new_academic_year.academic_year_name
			termDoc.term_name = f'Term {i}'
			termDoc.title = f'{termDoc.academic_year} ({termDoc.term_name})'
			term_exists = frappe.db.exists('Academic Term',termDoc.title)
			if term_exists:
				continue
			else:
				termDoc.insert()

