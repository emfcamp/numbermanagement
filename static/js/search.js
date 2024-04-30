document.addEventListener('DOMContentLoaded', function(){ 
    const searchform = document.getElementById("searchform");
    searchform.addEventListener("reset", clearSearch);
}, false);



function searchPhonebook(tableid) {

    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("search");
    filter = input.value.toUpperCase();
    table = document.getElementById(tableid);
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td");
        if (td.length > 0) {
            rowtext = tr[i].textContent
            if (rowtext.toUpperCase().includes(filter)) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}


function clearSearch() {
    table = document.getElementById("searchform").getElementsByTagName("table")[0];
    tr = table.getElementsByTagName("tr");
  
    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        tr[i].style.display = "";
    }
}