
import dataset
from stuf import stuf
import pprint
import database_helpers

#Given a new insurance claim, determine whether to increase a customer's premium
def premium_change(db, CustomerID):
    claims = list(db.query("Select * from claims WHERE CustomerID==" + CustomerID))

    New_RiskScore = (sum(1 if float(claim['Severity']) == 1 else 0 for claim in claims) *.5 + \
    sum(1 if float(claim['Severity']) == 2 else 0 for claim in claims) *.7 + \
    sum(1 if float(claim['Severity']) == 3 else 0 for claim in claims) *.9)
    print("Customer new Risk Score {}".format(New_RiskScore))

    RiskScore = float(list(db.query("Select RiskScore from customer WHERE CustomerID==" + CustomerID))[0]['RiskScore'])
    #RiskScore = list(db.query("Select RiskScore from customer WHERE CustomerID==" + CustomerID))[0]['RiskScore']
    print("Customer original Risk Score {}".format(RiskScore))

    if New_RiskScore > (RiskScore * 1.5):
        print("The customer's premium has increased")
        dict_data = [dict(CustomerID=CustomerID, RiskScore=New_RiskScore)]
        database_helpers.update_table(db, dict_data, "customer", ['CustomerID'])

    else:
        print("The customer's premium has not changed")


def generate_report(db, input_data):
    # query database to gather all of the info we need to make calculations for the report
    # get customer info from table
    customer_info = database_helpers.query_table_by_value(db, "customer", "CustomerID", input_data['CustomerID'])
    # get claim info from table
    claim_info = database_helpers.query_table_by_value(db, "claims", "id", input_data['ClaimID'])
    # get vehicle info from table
    vehicle_info = database_helpers.query_table_by_value(db, "vehicle", "VehicleID", input_data['VehicleID'])
    # get vehicle type info from table (assumes one element in vehicle_info)
    vehicle_type_info = database_helpers.query_table_by_value(db, "vehicletype", "VehicleTypeID", vehicle_info[0]['VehicleTypeID'])
    # get policy info from table (assumes one element in customer_info)
    policy_info = database_helpers.query_table_by_value(db, "policy", "PolicyID", customer_info[0]['PolicyID'])

    # call helper calculation functions to compute all of the new numbers
    #...

    # populate output data structure to send to front end
    report_data = {}
    report_data['customer_name'] = "Rachelle Kresch"
    report_data['customer_id'] = input_data['CustomerID']
    report_data['policy_details'] = "Some text about the policy"
    report_data['deductible'] = "1000"
    report_data['premium'] = "1000"
    report_data['customer_number_of_vehicles'] = 2
    report_data['customer_risk_score'] = 1.0
    report_data['claim_id'] = 10024
    report_data['claim_description'] = "This is some text"
    report_data['claim_cost_to_repair'] = 5000
    report_data['claim_vehicle_make_model'] = "Toyota Camry"
    report_data['claim_vehicle_year'] = 2015
    report_data['claim_vehicle_image_url'] = "http://st.motortrend.com/uploads/sites/10/2016/07/2017-toyota-camry-se-hybrid-sedan-angular-front.png"
    report_data['claim_vehicle_value'] = 10000
    report_data['claim_covered_repair_value'] = 4500
    report_data['claim_out_of_pocket_expense'] = 500
    report_data['claim_deductible_contributions'] = 500
    report_data['claim_remaining_deductible'] = 0
    report_data['claim_new_risk_score'] = 2.4
    report_data['claim_new_premium'] = 2000
    return report_data


if __name__ == "__main__":
    db = dataset.connect('sqlite:///AutoInsurace.db', row_type=stuf)
    premium_change(db, "100420")
