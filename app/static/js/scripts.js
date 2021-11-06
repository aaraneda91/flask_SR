$('.file-upload').change(function (e) {
   $(this).css('border', '3px solid #00CC99'); 
});

function eventCheckBox() {
   let checkboxs = document.getElementsByTagName("input");
   selectall = document.getElementById("selectall");
   for(let i = 0; i < checkboxs.length ; i++) { //zero-based array
      checkboxs[i].checked = !checkboxs[i].checked;
   }

   if (selectall.checked == true) {
      selectall.checked = false
   } else {
      selectall.checked = true
   }
}