$(document).ready(function() {
    
  $.ajax({
    url : 'http://localhost:8888/customers',
    type : 'GET',
    dataType:'json',
    success : function(data) {              
        $.each(data, function() {
          $('#claim_customer').append($('<option>', { 
            value: this['CustomerID'],
            text : this['Name']
          }));
          $("#claim_customer").prop("selectedIndex", 0);
          $('#claim_customer').selectpicker('refresh');
        });
    },
    error : function(request,error)
    {
        alert("Request: "+JSON.stringify(request));
    }
  });


  $("#claim_customer").on("changed.bs.select", function(e, clickedIndex, newValue, oldValue) {
    
    // remove all options every time the customer selectchanges
    $('#claim_vehicle').find('option').remove().end();

    $.ajax({
      url : 'http://localhost:8888/vehicles/bycustomer/' + this.value,
      type : 'GET',
      dataType:'json',
      success : function(data) {              
          $.each(data, function() {
            $('#claim_vehicle').append($('<option>', { 
              value: this[0]['VehicleID'],
              text : this[1]['Year'] + " " + this[1]['Make'] + " " + this[1]['Model']
            }));
          });
          $('#claim_vehicle').selectpicker('refresh');
      },
      error : function(request,error)
      {
          console.log("Request: "+JSON.stringify(request));
      }
    });
    $('#claim_vehicle').selectpicker('refresh');

  });

  $("#claim_submit").click(function() {

    output = {
      CustomerID: $('#claim_customer').val(),
      VehicleID: $('#claim_vehicle').val(),
      Severity: $('#claim_severity').val(),
      ClaimDescription: $('#claim_description').val()
    };

    // submit claim data to server
    $.ajax({
      url : 'http://localhost:8888/claims/submit',
      type: "POST",
      dataType:'json',
      data: JSON.stringify(output),
      success: function(data){
        $('#claim_report_modal').modal('show');
      },
      error: function(errMsg) {
        $('#claim_submit_alert_content').html("There was an error submitting the claim.");
        $('#claim_submit_alert').slideDown();
      }
    });
  });

});