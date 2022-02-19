$.post('https://alphazen.xyz/api/method/login',
{
  usr: "testimonial@gmail.com",
  pwd: "testimonial@viewer45"
},
function(data,status){
    console.log("Data: " + data.message + "\nStatus: " + status);
    
    var testimonial_name = "";
    let urldata = new URLSearchParams(window.location.search);
    
    if (urldata.has('testimonial_name')){
        testimonial_name = urldata.get('testimonial_name');
        var url = window.location.origin + "/api/method/frappe.utils.print_format.download_pdf?doctype=Testimonial&name=" + testimonial_name + "&format=Testimonial&no_letterhead=0&letterhead=Maeja%20Academy&settings=%7B%7D&_lang=en";
        $(location).attr('href',url);
    }
});
//https://alphazen.xyz/api/method/frappe.utils.print_format.download_pdf?doctype=Testimonial&name=Testimonial00006&format=Testimonial&no_letterhead=0&letterhead=Maeja%20Academy&settings=%7B%7D&_lang=en