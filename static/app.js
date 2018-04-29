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
          $('#claim_customer').val(1);
        });
    },
    error : function(request,error)
    {
        alert("Request: "+JSON.stringify(request));
    }
  });


});