// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Administrator', {
	 refresh: function(frm) {
		// your code here
		$("#member_wrapper").append(
            `<table class="table">
            <thead class="thead-light">
                <tr>
                    <th rowspan="2">SURNAME</th>
                    <th rowspan="2">OTHERNAMES</th>
                    <th rowspan="2">SEX</th>
                    <th rowspan="2">NRC NO.</th>
                    <th rowspan="2">MAN NO.</th>
                    <th rowspan="2">EMP NO.</th>
                    <th rowspan="2">DOFA</th>
                    <th rowspan="2">DOPA</th>
                    <th rowspan="2">DOB</th>
                    <th rowspan="2">DOR</th>
                    <th rowspan="2">POSITION</th>
                    <th rowspan="2">APPOINTMENT STATUS</th>
                    <th rowspan="2">QUALIFICATION</th>
                    <th rowspan="2">OTHER QUALIFICATION</th>
                    <th rowspan="2">INSTITUTION</th>
                    <th rowspan="2">SALARY SCALE</th>
                    <th colspan="2">SUBJECTS TRAINED TO TEACH</th>
                    <th colspan="2">SUBJECTS CURRENTLY</th>
                    <th rowspan="2">HOUSE (RENTED / GRZ)</th>
                    <th rowspan="2">PAYPOINT</th>
                    <th rowspan="2">EMPLOYMENT STATUS</th>
                    <th rowspan="2">TCZ NUMBER</th>
                    <th rowspan="2">CONTACT NUMBER</th>
                </tr>
                <tr>
                    <td>MAJOR</td>
                    <td>MINOR</td>
                    <td>MAJOR</td>
                    <td>MINOR</td>
                </tr>
            </thead>
            <tbody id="chick">
    
            </tbody>
        </table>`)
        $("#member_wrapper").css({"overflow":"auto", "width": "100%"})
        
                frappe.db.get_list('Instructor', {
                    fields: ['instructor_name','other_name','gender','nrc_no','man_no','employee','date_first_appointed','date_first_appointed_on_the_current_position','date_of_birth','date_of_retirement','position','appointment_status','qualification','other_qualification','institution','salary_scale','subjects','subjects_currently_teaching','house_rentedgrz','pay_point','status','tcz_no','contact_no'],
                    filters: {
                      status: 'active'
                    }
                }).then(records => {
                    console.log(records);
                    $.each(records, function(i,e){
                        $("#chick").append(
                         `<tr>
                          <th scope="row">`+e["instructor_name"]+`</th>
                          <td>`+e["other_name"]+`</td>
                          <td>`+e["gender"]+`</td>
                          <td>`+e["nrc_no"]+`</td>
                          <td>`+e["man_no"]+`</td>
                          <td>`+e["employee"]+`</td>
                          <td>`+e["date_first_appointed"]+`</td>
                          <td>`+e["date_first_appointed_on_the_current_position"]+`</td>
                          <td>`+e["date_of_birth"]+`</td>
                          <td>`+e["date_of_retirement"]+`</td>
                          <td>`+e["position"]+`</td>
                          <td>`+e["appointment_status"]+`</td>
                          <td>`+e["qualification"]+`</td>
                          <td>`+e["other_qualification"]+`</td>
                          <td>`+e["institution"]+`</td>
                          <td>`+e["salary_scale"]+`</td>
                          <td>`+e["subjects"]+`</td>
                          <td>`+e["subjects"]+`</td>
                          <td>`+e["subjects_currently_teaching"]+`</td>
                          <td>`+e["subjects_currently_teaching"]+`</td>
                          <td>`+e["house_rentedgrz"]+`</td>
                          <td>`+e["pay_point"]+`</td>
                          <td>`+e["status"]+`</td>
                          <td>`+e["tcz_no"]+`</td>
                          <td>`+e["contact_no"]+`</td>
                          </tr>`
                            )
                    })
            })
	 }
});
