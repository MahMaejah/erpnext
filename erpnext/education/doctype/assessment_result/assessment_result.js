// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Assessment Result', {
	refresh: function(frm) {
		// ****** NEWLY ADDED STARTS HERE ****** //

		var c = frm.doc.student + "-" + frm.doc.program + "-" + frm.doc.student_group + "-" + frm.doc.academic_year + "-" + frm.doc.academic_term;
		if(frm.doc.student !== undefined/* || frm.doc.program !== undefined || frm.doc.student_group !== undefined*/){
		//Check if report card exists
		//console.log(c)
		    if(!frm.doc.report_card_exists){
    		    frappe.call({
    		        method: 'erpnext.education.doctype.assessment_result.assessment_result.card_exists',
    		        args: {"card_name": c},
    		        callback: (res) => {
    		            //Check if card doesn't exist and create a new one
    		            if(res.message === undefined){
    		                console.log(c)
    		                console.log("Card not found, attempting to create new card")
    		                console.log("Result: " + res.message)
    		                frappe.call({
    		                    method: 'erpnext.education.doctype.assessment_result.assessment_result.generate_report_card',
    		                    args: {
    		                        "gen_student": frm.doc.student, 
    		                        "gen_grade": frm.doc.program, 
    		                        "gen_class": frm.doc.student_group, 
    		                        "gen_year": frm.doc.academic_year, 
    		                        "gen_term": frm.doc.academic_term
    		                    },
    		                    callback: (re) => {
    		                        frm.set_value("report_card_exists", 1)
    		                    }
    		                })
    		            }
    		            //Report card exists
    		            else{
    		                frm.set_value("report_card_exists", 1)
    		            }
    		        }
    		    })
    		}
		//End if
		}

		// ****** NEWLY ADDED ENDS HERE ****** //
		if (!frm.doc.__islocal) {
			frm.trigger('setup_chart');
		}

		frm.get_field('details').grid.cannot_add_rows = true;

		frm.set_query('course', function() {
			return {
				query: 'erpnext.education.doctype.program_enrollment.program_enrollment.get_program_courses',
				filters: {
					'program': frm.doc.program
				}
			};
		});

		frm.set_query('academic_term', function() {
			return {
				filters: {
					'academic_year': frm.doc.academic_year
				}
			};
		});

		var report_card = frm.doc.report_card_name;

		if(report_card != null){
			frm.add_custom_button(__("Same Page"), function(){
				console.log(frappe.utils.get_url());
				//window.location.href = frappe.utils.get_url() + '/app/report-card/' + report_card;
			}, __("Go to Report Card"));
			  
			frm.add_custom_button(__("New Page"), function(){
			window.open('https://maeja.ml/app/report-card/' + report_card);
			}, __("Go to Report Card"));
		}		
	},

	onload: function(frm) {
		frm.set_query('assessment_plan', function() {
			return {
				filters: {
					docstatus: 1
				}
			};
		});
	},

	assessment_plan: function(frm) {
		if (frm.doc.assessment_plan) {
			frappe.call({
				method: 'erpnext.education.api.get_assessment_details',
				args: {
					assessment_plan: frm.doc.assessment_plan
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.clear_table(frm.doc, 'details');
						$.each(r.message, function(i, d) {
							var row = frm.add_child('details');
							row.assessment_criteria = d.assessment_criteria;
							row.maximum_score = d.maximum_score;
						});
						frm.refresh_field('details');
					}
				}
			});
		}
	},

	setup_chart: function(frm) {
		let labels = [];
		let maximum_scores = [];
		let scores = [];
		$.each(frm.doc.details, function(_i, e) {
			labels.push(e.assessment_criteria);
			maximum_scores.push(e.maximum_score);
			scores.push(e.score);
		});

		if (labels.length && maximum_scores.length && scores.length) {
			frm.dashboard.chart_area.empty().removeClass('hidden');
			new frappe.Chart('.form-graph', {
				title: 'Assessment Results',
				data: {
					labels: labels,
					datasets: [
						{
							name: 'Maximum Score',
							chartType: 'bar',
							values: maximum_scores,
						},
						{
							name: 'Score Obtained',
							chartType: 'bar',
							values: scores,
						}
					]
				},
				colors: ['#4CA746', '#98D85B'],
				type: 'bar'
			});
		}
	}
});

frappe.ui.form.on('Assessment Result Detail', {
	score: function(frm, cdt, cdn) {
		var d  = locals[cdt][cdn];

		if (!d.maximum_score || !frm.doc.grading_scale) {
			d.score = '';
			frappe.throw(__('Please fill in all the details to generate Assessment Result.'));
		}

		if (d.score > d.maximum_score) {
			frappe.throw(__('Score cannot be greater than Maximum Score'));
		}
		else {
			frappe.call({
				method: 'erpnext.education.api.get_grade',
				args: {
					grading_scale: frm.doc.grading_scale,
					percentage: ((d.score/d.maximum_score) * 100)
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'grade', r.message);
					}
				}
			});
		}
	}
});