const numberWithCommas = (x) => {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function fill_report(data) {
  $("#report_customer_name").text(data.customer_name);
  $("#report_customer_id").text(data.customer_id);
  $("#report_policy_details").text(data.policy_details);
  $("#report_policy_premium").text(numberWithCommas(data.premium));
  $("#report_policy_deductable").text(numberWithCommas(data.deductible));
  $("#report_customer_num_vehicles").text(data.customer_number_of_vehicles);
  $("#report_customer_risk_score").text(data.customer_risk_score);
  $("#report_claim_id").text(data.claim_id);
  $("#report_claim_description").text(data.claim_description);
  $("#report_claim_cost_to_repair").text(numberWithCommas(data.claim_cost_to_repair));
  $("#report_claim_vehicle_make_model").text(data.claim_vehicle_make_model);
  $("#report_claim_vehicle_year").text(data.claim_vehicle_year);
  $("#report_claim_vehicle_value").text(numberWithCommas(data.claim_vehicle_value));
  $("#report_claim_vehicle_image_url").attr("src", data.claim_vehicle_image_url);
  $("#report_claim_covered_repair_value").text(numberWithCommas(data.claim_covered_repair_value));
  $("#report_claim_out_of_pocket_expense").text(numberWithCommas(data.claim_out_of_pocket_expense));
  $("#report_claim_existing_deductible").text(numberWithCommas(data.claim_deductible_contributions));
  $("#report_no_prior_claims").text(data.no_prior_claims);
  $("#report_claim_remaining_deductible").text(numberWithCommas(data.claim_remaining_deductible));
  $("#report_claim_new_risk_score").text(data.claim_new_risk_score);
  $("#report_claim_covered_repair_value2").text(numberWithCommas(data.claim_covered_repair_value));
  $("#report_new_premium").text(numberWithCommas(data.claim_new_premium));

  // only show the alert specific to the risk/premium changing
  if(data.claim_new_premium > data.premium) {
    $("#report_claim_new_premium").show();
    $("#report_claim_no_new_premium").hide();
  }
  else {
    $("#report_claim_new_premium").hide();
    $("#report_claim_no_new_premium").show();
  }

};

function fill_customer(data) {
  $("#customer_customer_name").text(data.customer_name);
  $("#customer_customer_id").text(data.customer_id);
  $("#customer_policy_details").text(data.policy_details);
  $("#customer_policy_premium").text(data.premium);
  $("#customer_policy_deductable").text(data.deductible);
  $("#customer_num_vehicles").text(data.number_vehicles);
  $("#customer_num_claims").text(data.number_claims);
  $("#customer_risk_score").text(data.risk_score);

  $("#customer_cars").empty();

  $.each(data.vehicles, function() {
    console.log(this);
    var content = `
      <div class="card bg-light mb-3">
        <div class="card-header">${this.Make} ${this.Model}</div>
          <img class="card-img-top" src="${this.ImageURL}" alt="Vehicle image">
          <div class="card-body">
            <p class="card-text">
              <b>Year</b>: ${this.Year}<br />
              <b>Value</b>: ${numberWithCommas(this.BookValue)}
            </p>
          </div>
        </div>
      `;
    $("#customer_cars").append(content);
  });
}

function fill_stats(data) {
  $("#stats_customers").text(data.customers);
  $("#stats_policies").text(data.policies);
  $("#stats_vehicles").text(data.vehicles);
  $("#stats_vehicle_types").text(data.vehicle_types);
  $("#stats_claims").text(data.claims);
}

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

    if($("#claim_customer").val() == "") {
      return;
    }

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
        fill_report(data.report);
        $('#claim_report_modal').modal('show');
      },
      error: function(errMsg) {
        $('#claim_submit_alert_content').html("There was an error submitting the claim.");
        $('#claim_submit_alert').slideDown();
      }
    });
  });

  $("#view_statistics").click(function() {
    // query the newest stats
    $.ajax({
      url : 'http://localhost:8888/stats',
      type : 'GET',
      dataType:'json',
      success : function(data) {
          fill_stats(data);
          $('#statistics_modal').modal('show');
      },
      error : function(request,error)
      {
          alert("Stats request: "+JSON.stringify(request));
      }
    });

  });

  $("#show_customer_btn").click(function() {
    if($("#claim_customer").val() == "") {
      return;
    }

    // query the customer data
    $.ajax({
      url : 'http://localhost:8888/customer/' + $("#claim_customer").val(),
      type : 'GET',
      dataType:'json',
      success : function(data) {
          fill_customer(data);
          $('#customer_modal').modal('show');
      },
      error : function(request,error)
      {
          alert("Stats request: "+JSON.stringify(request));
      }
    });

    $("#customer_modal").modal('show');
  });

});
