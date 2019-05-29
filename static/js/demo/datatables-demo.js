// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable( {
      "order": [],
      "language": {
          "lengthMenu":   "Prikaži _MENU_ vnosov",
          "info":           "Prikazujem _START_ do _END_ od _TOTAL_ zadetkov",
          "zeroRecords":  "Ni zadetkov",
          "search":       "Iskanje:",
          "paginate": {
              "first":      "Prva",
              "last":       "Zadnja",
              "next":       "Naslednja",
              "previous":   "Prejšnja"
          },
      }
  } );
});