// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Results Analysis', {
	 refresh: function(frm) {
		$("#analysiswrapper").append(
            `<table class="table">
              <thead class="thead-light">
                <tr>
                  <th scope="col">#</th>
                  <th scope="col">Points</th>
                  <th scope="col">Term</th>
                  <th scope="col">Class</th>
                </tr>
              </thead>
              <tbody id="analysis-content">
              
              </tbody>
            </table>`)
        
        //$("#analysiswrapper").append('<table class="table"><thead class="thead-dark"><tr><th scope="col">#</th><th scope="col">First</th><th scope="col">Last</th><th scope="col">Handle</th></tr></thead></table>')
        //$("#analysiswrapper").append("Success")
        frappe.call({
            method: "erpnext.education.api.get_current_academic_year",
            callback: function(r){
                console.log(r.message)
                $.each(r.message, function(i, e){
                    $("#analysis-content").append(
                        `<tr>
                          <th scope="row">`+e["COUNT(points_in_best_6)"]+`</th>
                          <td>`+e["points_in_best_6"]+`</td>
                          <td>`+e["term"]+`</td>
                          <td>`+e["class_name"]+`</td>
                        </tr>`
                    )
                })
            }
        })
        
		$("#year").append(
		    "<option value='1'>1</option>"+
		    "<option value='2'>2</option>"
		);
	 }
});
