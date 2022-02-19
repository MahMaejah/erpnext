$.post('https://alphazen.xyz/api/method/login',
{
  usr: "recommendation@gmail.com",
  pwd: "recommendation@viewer45"
},
function(data,status){
    console.log("Data: " + data.message + "\nStatus: " + status);
    
    var recommendation = "";
    let urldata = new URLSearchParams(window.location.search);
    
    if (urldata.has('recommendation')){
        recommendation = urldata.get('recommendation');
        var url = window.location.origin + "/api/method/frappe.utils.print_format.download_pdf?doctype=Recommendation%20Letter&name=" + recommendation + "&format=Recommendation%20Letter&no_letterhead=0&letterhead=Maeja%20Academy&settings=%7B%7D&_lang=en";
        $(location).attr('href',url);
    }
});
//https://alphazen.xyz/api/method/frappe.utils.print_format.download_pdf?doctype=Recommendation%20Letter&name=Letter00002&format=Recommendation%20Letter&no_letterhead=0&letterhead=Maeja%20Academy&settings=%7B%7D&_lang=en