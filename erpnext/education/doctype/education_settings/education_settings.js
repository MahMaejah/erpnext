// Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Education Settings', {
	refresh: function(frm) {
		frm.add_custom_button('Forward', () => {
			frappe.confirm('Are you sure you want to proceed?',
			() => {
				// action to perform if Yes is selected
				console.log("Going to next year");
				frappe.call({
					method: "erpnext.education.api.migrate_forward"
				})
			})
		}, 'Progression');
		frm.add_custom_button('Reverse', () => {
			frappe.confirm('Are you sure you want to proceed?',
			() => {
				// action to perform if Yes is selected
				console.log("Going to previous year");
				frappe.call({
					method: "erpnext.education.api.migrate_reverse"
				})
			})
		}, 'Progression');
	}
});
