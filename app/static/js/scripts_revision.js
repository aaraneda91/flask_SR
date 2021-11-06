/** Scripts para fase de REVISION */

$('#select_all_revision').on('click',function(){

   if(this.checked){
      $('.checkbox').each(function(){
         this.checked = true;
      });
   }else{
      $('.checkbox').each(function(){
         this.checked = false;
      });
   }
   showButtonRevision()
});

$('.checkbox').on('click',function(){
   
   if($('.checkbox:checked').length == $('.checkbox').length){
      $('#select_all_revision').prop('checked',true);
   }else{
      $('#select_all_revision').prop('checked',false);
   }
   showButtonRevision()
});

var arrayRevision = []

function showButtonRevision(){
   arrayRevision = []
   /* si hay al menos un check activado, se muestra el botón */
   count = 0
   $('.checkbox').each(function(){
      if (this.checked == true) {
         count = count + 1
         arrayRevision.push($(this).val())
      }
   })

   if (count > 0) {
      $('#btn_assign_user').show();
   } else {
      $('#btn_assign_user').hide();
   }
   /* fin validacion */
}

$('#btn_confirm_assign_user_revision').on('click',function(){
   $.ajax({
      type: 'POST',
      dataType: "json",
      data: {
         "id": arrayRevision,
         "user_id": $('#user_assign').val(),
         "to_status": 3
      },
      url: "/operacion/json/assign_user",
      success: function (data) {
         $('#assingUser').modal('toggle');
         $('#modalMsgSuccessRevision').modal('show');
      }
   })
})

$("#modalMsgSuccessRevision").on("hidden.bs.modal", function () {
   window.location.href = '/operacion/revision';
});