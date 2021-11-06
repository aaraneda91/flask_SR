// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable({  
    "order": [],
    "lengthMenu": [[50, -1], [50, "Todo"]],
    "language": {
      "lengthMenu": "Mostrar _MENU_ registros por página",
      "zeroRecords": "Nada encontrado",
      "info": "Mostrando página _PAGE_ de _PAGES_",
      "infoEmpty": "No hay registros disponibles",
      "infoFiltered": "(filtered from _MAX_ total records)",
      "sSearch": "Buscar",
      "oPaginate": {
        "sFirst":    	"Primero",
        "sPrevious": 	"Anterior",
        "sNext":     	"Siguiente",
        "sLast":     	"Último"
      },
  }
  });
});

// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTableLocalContact').DataTable({  
    initComplete: function () {
      this.api().columns('.select-filter').every( function () {
        var column = this;
        var select = $('<select><option value=""></option></select>')
          .appendTo( $(column.footer()).empty() )
            .on( 'change', function () {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
                column.search( val ? '^'+val+'$' : '', true, false ).draw();
              });
          column.data().unique().sort().each( function ( d, j ) {
              select.append( '<option value="'+d+'">'+d+'</option>' )
          });
      });
    },
    "lengthMenu": [[50, -1], [50, "Todo"]],
    "language": {
      "lengthMenu": "Mostrar _MENU_ registros por página",
      "zeroRecords": "Nada encontrado",
      "info": "Mostrando página _PAGE_ de _PAGES_",
      "infoEmpty": "No hay registros disponibles",
      "infoFiltered": "(filtered from _MAX_ total records)",
      "sSearch": "Buscar",
      "oPaginate": {
        "sFirst": "Primero",
        "sPrevious": "Anterior",
        "sNext": "Siguiente",
        "sLast": "Último"
      },
    }
  });
});