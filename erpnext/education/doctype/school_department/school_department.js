// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('School Department', {
	 refresh: function(frm) {
		frm.add_custom_button(__('Issue Learning Material'), function(){
		    frappe.msgprint("Working");
		});
		
		// your code here
		frappe.call({
            method: "erpnext.education.api.department_subject_analysis",
            args: {
                dep_name: frm.doc.name
                // name: frm.doc.library_member
            },
            callback: function (data) {
                console.log("starting analysis");
                console.log(data.message);
                console.log("ending analysis");
            }
        })
        
        frappe.db.get_list('School Asset', {fields: ['name', 'available', 'total', 'issued', 'school_department'], 
        filters: {'school_department': frm.doc.name}}).then(function(res){
            var x = 0;
            for(;res.length>x;x++){
            let row = frm.add_child('learning_materials', {
                item: res[x].name,
                total: res[x].total,
                issued: res[x].issued,
                available: res[x].available
            });
    
            frm.refresh_field('department_items');
            }
        })
        	$("#table_members_wrapper").append(
            `<table class="table">
              <thead class="thead-light">
                <tr>
                  <th scope="col">Teacher</th>
                  <th scope="col">Sex</th>
                  <th scope="col">Qualification</th>
                  <th scope="col">Position</th>
                  <th scope="col">Subjects</th>
                  <th scope="col">Total N.O of Periods<th>
                </tr>
              </thead>
              <tbody id="chick">
              </tbody>
            </table>`)
        
                frappe.db.get_list('Instructor', {
                    fields: ['instructor_name','gender','qualification','position','subjects','total_no_of_periods'],
                    filters: {
                        'school_department': frm.doc.name
                    }
                }).then(records => {
                    console.log(records);
                    $.each(records, function(i,e){
                        $("#chick").append(
                         `<tr>
                          <th scope="row">`+e["instructor_name"]+`</th>
                          <td>`+e["gender"]+`</td>
                          <td>`+e["qualification"]+`</td>
                          <td>`+e["position"]+`</td>
                          <td>`+e["subjects"]+`</td>
                        //   <td>`+e["total_no_of_periods"]+`</td>
                          </tr>`
                            
                            )
                    })
            })
	 }
});
