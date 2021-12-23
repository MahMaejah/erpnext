// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('School Asset', {
	 refresh: function(frm) {
		frm.set_value("available", frm.doc.total - frm.doc.issued);
	 }
});
