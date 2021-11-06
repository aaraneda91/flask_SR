/** Scripts para fase de GESTION */

$('#select_all_gestion').on('click',function(){

   if(this.checked){
      $('.checkbox').each(function(){
         this.checked = true;
      });
   }else{
      $('.checkbox').each(function(){
         this.checked = false;
      });
   }
   showButtonGestion()
});

$('.checkbox').on('click',function(){
   
   if($('.checkbox:checked').length == $('.checkbox').length){
      $('#select_all_gestion').prop('checked',true);
   }else{
      $('#select_all_gestion').prop('checked',false);
   }
   showButtonGestion()
});

var arrayGestion = []

function showButtonGestion(){
   arrayGestion = []
   /* si hay al menos un check activado, se muestra el botón */
   count = 0
   $('.checkbox').each(function(){
      if (this.checked == true) {
         count = count + 1
         arrayGestion.push($(this).val())
      }
   })

   if (count > 0) {
      $('#btn_send_revision').show();
      $('#btn_send_coordinacion').show();
   } else {
      $('#btn_send_revision').hide();
      $('#btn_send_coordinacion').hide();
   }
   /* fin validacion */
}

$('#btn_send_revision').on('click',function(){
   $.ajax({
      type: 'POST',
      dataType: "json",
      data: {
         "id": arrayGestion
      },
      url: "/operacion/json/send_revision",
      success: function (data) {
         $("#resultMsg").html("Los establecimientos fueron enviados a revisión.");
         $('#modalMsgSuccessGestion').modal('show');
      }
   })
})

$('#btn_send_coordinacion').on('click',function(){
   $.ajax({
      type: 'POST',
      dataType: "json",
      data: {
         "id": arrayGestion
      },
      url: "/operacion/json/send_coordinacion",
      success: function (data) {
         $("#resultMsg").html("Los establecimientos fueron enviados a coordinación.");
         $('#modalMsgSuccessGestion').modal('show');
      }
   })
})

$("#modalMsgSuccessGestion").on("hidden.bs.modal", function () {
   window.location.href = '/operacion/gestion';
});

/** Fin scripts - GESTION */