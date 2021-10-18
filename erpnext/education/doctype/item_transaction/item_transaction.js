// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Transaction', {
	// refresh: function(frm) {

	// }

	//Make sure ToDate is not less than FromDate
	before_save: function(frm){
		if(frm.doc.to_date < frm.doc.from_date){
			frappe.throw("To date must not be less than from date");
		}
	},

	item: function(frm){
		var ga = frappe.db.get_value("School Item", frm.doc.item, "available", (r) => {
			frm.set_value("available", r.available);
		});
	}
});
