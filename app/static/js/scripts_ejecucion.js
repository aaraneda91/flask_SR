/** Scripts para fase de REVISION */

$('#select_all_ejecucion').on('click',function(){

   if(this.checked){
      $('.checkbox').each(function(){
         this.checked = true;
      });
   }else{
      $('.checkbox').each(function(){
         this.checked = false;
      });
   }
   showButtonEjecucion()
});

$('.checkbox').on('click',function(){
   
   if($('.checkbox:checked').length == $('.checkbox').length){
      $('#select_all_ejecucion').prop('checked',true);
   }else{
      $('#select_all_ejecucion').prop('checked',false);
   }
   showButtonEjecucion()
});

var arrayEjecucion = []

function showButtonEjecucion(){
   arrayEjecucion = []
   /* si hay al menos un check activado, se muestra el botón */
   count = 0
   $('.checkbox').each(function(){
      if (this.checked == true) {
         count = count + 1
         arrayEjecucion.push($(this).val())
      }
   })

   if (count > 0) {
      $('#btn_assign_user_ejecucion').show();
   } else {
      $('#btn_assign_user_ejecucion').hide();
   }
   /* fin validacion */
}

$('#btn_confirm_assign_user').on('click',function(){
   $.ajax({
      type: 'POST',
      dataType: "json",
      data: {
         "id": arrayEjecucion,
         "user_id": $('#user_assign').val(),
         "to_status": 15
      },
      url: "/operacion/json/assign_user",
      success: function (data) {
         $('#assingUser').modal('toggle');
         $('#modalMsgSuccess').modal('show');
      }
   })
})

$("#modalMsgSuccess").on("hidden.bs.modal", function () {
   window.location.href = '/operacion/ejecucion';
});