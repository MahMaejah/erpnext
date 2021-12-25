// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Testimonial', {
	refresh: function(frm) {
		var chrts=[
		    "Character and general behavior",
            "Initiative, common sense and leadership quality",
            "Sense of duty and punctuality",
            "Co-operation with others",
            "Attitude towards work",
            "Intelligence and judgement",
            "Dependability and Reliability"
		    ];
		    //console.log(frm.doc.testimonial_tb.length);
			if(frm.doc.testimonial_tb.length <=1){
				for(let td of chrts){
				let row = frm.add_child('testimonial_tb',{
					characters: td
				});
			}
		}
	}
});
