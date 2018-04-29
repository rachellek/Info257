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
          $('#claim_customer').selectpicker('refresh');
        });
    },
    error : function(request,error)
    {
        alert("Request: "+JSON.stringify(request));
    }
  });


  $("#claim_customer").on("changed.bs.select", function(e, clickedIndex, newValue, oldValue) {
    
    $.ajax({
      url : 'http://localhost:8888/vehicles/bycustomer/' + this.value,
      type : 'GET',
      dataType:'json',
      success : function(data) {              
          $.each(data, function() {
            $('#claim_vehicle').append($('<option>', { 
              value: this['VehicleID'],
              text : this['VehicleID']
            }));
            $('#claim_vehicle').selectpicker('refresh');
          });
      },
      error : function(request,error)
      {
          alert("Request: "+JSON.stringify(request));
      }
    });

  });

});