// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Testimonial', {
	characters_template: function(frm) {
		if (frm.doc.characters_template != null ){
			frappe.db.exists("Testimonial Characters Template",frm.doc.characters_template)
				.then(exists => {
					console.log(exists)
					if (exists == true){
						console.log("Running")
						frappe.db.get_doc("Testimonial Characters Template",frm.doc.characters_template)
						.then(doc => {
							var ch = []
							var chrts = doc.characters
							$.each(chrts,function(i,d){
								var ch = d.characters
								console.log(ch)
								let row = frm.add_child('testimonial_tb',{
									characters: ch
								});
								frm.refresh_field('testimonial_tb');
							})
						})
					}
				})
		}
		
		// frappe.db.get_doc("Testimonial Characters Template",frm.doc.characters_template)
		// 	.then(doc => {
		// 		var ch = []
		// 		var chrts = doc.characters
		// 		$.each(chrts,function(i,d){
		// 			var ch = d.characters
		// 			console.log(ch)
		// 			let row = frm.add_child('testimonial_tb',{
		// 				characters: ch
		// 			});
		// 			frm.refresh_field('testimonial_tb');
		// 		})
		// 	})
	}
});
