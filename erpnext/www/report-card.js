$.post('https://alphazen.xyz/api/method/login',
{
  usr: "reportcardviewer@gmail.com",
  pwd: "report@viewer45"
},
function(data,status){
    console.log("Data: " + data.message + "\nStatus: " + status);
    
    var card_name = "";
    let urldata = new URLSearchParams(window.location.search);
    
    if (urldata.has('card')){
        card_name = urldata.get('card');
        var url = window.location.origin + "/api/method/frappe.utils.print_format.download_pdf?doctype=Report%20Card&name=" + card_name + "&format=Report%20Card%20Print%20Format&no_letterhead=0&letterhead=Report Card Letter Head&settings=%7B%7D&_lang=en";
        $(location).attr('href',url);
    }
});

//https://alphazen.xyz/api/method/frappe.utils.print_format.download_pdf?doctype=Report%20Card&name=EDU-STU-2021-00015-Grade%2010-Grade%2010%20Science-2021-22-2021-22%20(Term%202)&format=Report%20Card%20Print%20Format&no_letterhead=0&letterhead=Maeja%20Academy&settings=%7B%7D&_lang=en