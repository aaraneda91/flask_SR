/** Scripts para fase de GESTION */

$('#select_all_coordinacion').on('click',function(){

   if(this.checked){
      $('.checkbox').each(function(){
         this.checked = true;
      });
   }else{
      $('.checkbox').each(function(){
         this.checked = false;
      });
   }
   showButtonCoordinacion()
});

$('.checkbox').on('click',function(){
   
   if($('.checkbox:checked').length == $('.checkbox').length){
      $('#select_all_coordinacion').prop('checked',true);
   }else{
      $('#select_all_coordinacion').prop('checked',false);
   }
   showButtonCoordinacion()
});

var arrayCoordinacion = []

function showButtonCoordinacion(){
   arrayCoordinacion = []
   /* si hay al menos un check activado, se muestra el botón */
   count = 0
   $('.checkbox').each(function(){
      if (this.checked == true) {
         count = count + 1
         arrayCoordinacion.push($(this).val())
      }
   })

   if (count > 0) {
      $('#btn_send_coord_to_revision').show();
      $('#btn_send_coord_to_ejecucion').show();
   } else {
      $('#btn_send_coord_to_revision').hide();
      $('#btn_send_coord_to_ejecucion').hide();
   }
   /* fin validacion */
}

$('#btn_send_coord_to_revision').on('click',function(){
   $.ajax({
      type: 'POST',
      dataType: "json",
      data: {
         "id": arrayCoordinacion,
         "from_coord": true
      },
      url: "/operacion/json/send_revision",
      success: function (data) {
         $("#resultMsg").html("Los establecimientos seleccionados fueron enviados a revisión.");
         $('#modalMsgSuccessCoordinacion').modal('show');
      }
   })
})

$('#btn_send_coord_to_ejecucion').on('click',function(){
   $.ajax({
      type: 'POST',
      dataType: "json",
      data: {
         "id": arrayCoordinacion,
         "from_coord": true
      },
      url: "/operacion/json/send_ejecucion",
      success: function (data) {
         if (data.count_failed > 0) {
            $("#resultMsg").html("Establecimientos que no pudieron ser enviados a ejecución: <ul>");
            $("#resultMsg").append(data.itt_failed);
            $("#resultMsg").append("</ul><br><font size='2'><i><b><u>Nota:</u> Para ser enviados a ejecución, los establecimientos deben tener un contacto local y estar coordinados.</b></i></font>");
         } else {
            $("#resultMsg").html("Los establecimientos fueron enviados a ejecución.");
         }
         $('#modalMsgSuccessCoordinacion').modal('show');
      }
   })
})

$("#modalMsgSuccessCoordinacion").on("hidden.bs.modal", function () {
   window.location.href = '/operacion/coordinacion';
});