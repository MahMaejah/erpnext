frappe.ui.form.on("Academic Year", {
    refresh: function(frm) {
       
          frm.add_custom_button(__('Extend Years'), function(){
            frappe.call({
                method: "erpnext.education.api.extendAcadmicYearDocType", //dotted path to server method
                callback: function(r) {
                    console.log(r.message);
                }
            })
        }, __("Utilities"));
       
      }
});