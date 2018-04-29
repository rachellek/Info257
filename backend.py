
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
    # find number of vehicles for customer id
    num_vehicles = len(database_helpers.query_table_by_value(db, "vehicle", "CustomerID", input_data['CustomerID']))

    # call helper calculation functions to compute all of the new numbers
    #...

    # populate output data structure to send to front end
    report_data = {}
    report_data['customer_name'] = customer_info[0]['Name']
    report_data['customer_id'] = customer_info[0]['CustomerID']
    report_data['policy_details'] = policy_info[0]['PolicyDetails']
    report_data['deductible'] = policy_info[0]['Deductible']
    report_data['premium'] = customer_info[0]['Premium']
    report_data['customer_number_of_vehicles'] = num_vehicles
    report_data['customer_risk_score'] = customer_info[0]['']
    report_data['claim_id'] = input_data['ClaimID']
    report_data['claim_description'] = claim_info[0]['ClaimDescription']
    report_data['claim_cost_to_repair'] = 5000
    report_data['claim_vehicle_make_model'] = "{} {}".format(vehicle_type_info[0]['Make'], vehicle_type_info[0]['Model'])
    report_data['claim_vehicle_year'] = vehicle_type_info[0]['Year']
    report_data['claim_vehicle_image_url'] = vehicle_type_info[0]['ImageURL']
    report_data['claim_vehicle_value'] = vehicle_type_info[0]['BookValue']
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
