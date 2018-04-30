
import dataset
from stuf import stuf
import pprint
import database_helpers

#Given a new insurance claim, determine whether to increase a customer's premium
def risk_score_change(db, CustomerID):
    claims = list(db.query("Select * from claims WHERE CustomerID==" + CustomerID))

    New_RiskScore = ( \
    sum(1 if float(claim['Severity']) == 0 else 0 for claim in claims) *.3 + \
    sum(1 if float(claim['Severity']) == 1 else 0 for claim in claims) *.4 + \
    sum(1 if float(claim['Severity']) == 2 else 0 for claim in claims) *.5 + \
    sum(1 if float(claim['Severity']) == 3 else 0 for claim in claims) *.7 + \
    sum(1 if float(claim['Severity']) == 5 else 0 for claim in claims) *.9 + \
    sum(1 if float(claim['Severity']) == 5 else 0 for claim in claims) *1.2)

    print("Customer new Risk Score {}".format(New_RiskScore))

    RiskScore = float(list(db.query("Select RiskScore from customer WHERE CustomerID==" + CustomerID))[0]['RiskScore'])
    #RiskScore = list(db.query("Select RiskScore from customer WHERE CustomerID==" + CustomerID))[0]['RiskScore']
    print("Customer original Risk Score {}".format(RiskScore))

    if New_RiskScore > (RiskScore * 1.5):
        return (True, New_RiskScore)
    else:
        return (False, RiskScore)

def claim_cost_to_repair(Severity, BookValue):
    claim_cost_to_repair = 0

    if Severity == 0:
        claim_cost_to_repair = BookValue * .2
    if Severity == 1:
        claim_cost_to_repair = BookValue * .3
    if Severity == 2:
        claim_cost_to_repair = BookValue * .3
    if Severity == 3:
        claim_cost_to_repair = BookValue * .5
    if Severity == 4:
        claim_cost_to_repair = BookValue * .8
    if Severity == 5:
        claim_cost_to_repair = BookValue * 1

    print("The cost to repair is {} for a car worth {}".format(claim_cost_to_repair, BookValue))
    return claim_cost_to_repair

def update_premium(db, old_premium, customer_id):
    # update premium by 20%
    new_premium = round((float(old_premium) * 1.2), 0)
    database_helpers.update_table(db, [{"CustomerID": customer_id, "Premium": str(new_premium)}], "customer", "CustomerID")
    return new_premium

def update_risk_score(db, new_risk_score, customer_id):
    # update risk score
    database_helpers.update_table(db, [{"CustomerID": customer_id, "RiskScore": new_risk_score}], "customer", "CustomerID")

def claims_toward_deductible(db, customer_id):
    claims = database_helpers.query_table_by_value(db, "claims", "CustomerID", customer_id)
    no_old_claims = len(claims)-1
    total_paid = 0
    print("Total claims {}".format(len(claims)))
    if len(claims) >1:
        for claim in claims[:-1]:
            vehicle_id = claim['VehicleID']
            severity = claim['Severity']
            vehicle =  database_helpers.query_table_by_value(db, "vehicle", "VehicleID", vehicle_id)[0]
            vehicle_type_id = vehicle['VehicleTypeID']
            vehicle_type =  database_helpers.query_table_by_value(db, "vehicletype", "VehicleTypeID", vehicle_type_id)[0]
            book_value = vehicle_type['BookValue']
            total_paid += claim_cost_to_repair(int(severity), float(book_value))
    return (total_paid, no_old_claims)

def coverage(claim_amount, deductible_total, deductible_paid):
    out_of_pocket = min(claim_amount - deductible_paid, deductible_total)
    covered = claim_amount - out_of_pocket
    remaining_deductible = max(0, (deductible_total - deductible_paid))
    return (out_of_pocket, covered, remaining_deductible)

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
    print(customer_info)
    print(vehicle_type_info)

    # Cost to repair
    customer_claim_cost_to_repair = claim_cost_to_repair(int(claim_info[0]["Severity"]), float(vehicle_type_info[0]["BookValue"]))
    new_risk_score = risk_score_change(db, input_data['CustomerID'])

    new_premium = -1
    if new_risk_score[0]:
        # update the databases
        update_risk_score(db, new_risk_score[1], customer_info[0]['CustomerID'])
        new_premium = round((update_premium(db, customer_info[0]['Premium'], customer_info[0]['CustomerID'])), 0)
    print("The new premuim is {}".format(new_premium))

    total_paid_into_deductible = claims_toward_deductible(db, customer_info[0]['CustomerID'])[0]
    total_prior_claims = claims_toward_deductible(db, customer_info[0]['CustomerID'])[1]


    print("total paid {}".format(total_paid_into_deductible))
    claim_remaining_deductible = max(0, (float(policy_info[0]['Deductible']) - total_paid_into_deductible))
    claim_covered_repair_value = max(0, customer_claim_cost_to_repair - claim_remaining_deductible)
    claim_out_of_pocket_expense = customer_claim_cost_to_repair - claim_covered_repair_value

    print("Total exisitng claims {}".format(total_prior_claims))

    # populate output data structure to send to front end
    report_data = {}
    report_data['customer_name'] = customer_info[0]['Name']
    report_data['customer_id'] = customer_info[0]['CustomerID']
    report_data['policy_details'] = policy_info[0]['PolicyDetails']
    report_data['deductible'] = policy_info[0]['Deductible']
    report_data['premium'] = customer_info[0]['Premium']
    report_data['customer_number_of_vehicles'] = num_vehicles
    report_data['customer_risk_score'] = customer_info[0]['RiskScore']
    report_data['claim_id'] = input_data['ClaimID']
    report_data['claim_description'] = claim_info[0]['ClaimDescription']
    report_data['claim_cost_to_repair'] = customer_claim_cost_to_repair
    report_data['claim_vehicle_make_model'] = "{} {}".format(vehicle_type_info[0]['Make'], vehicle_type_info[0]['Model'])
    report_data['claim_vehicle_year'] = vehicle_type_info[0]['Year']
    report_data['claim_vehicle_image_url'] = vehicle_type_info[0]['ImageURL']
    report_data['claim_vehicle_value'] = vehicle_type_info[0]['BookValue']
    report_data['claim_out_of_pocket_expense'] = claim_out_of_pocket_expense
    report_data['claim_covered_repair_value'] = claim_covered_repair_value
    report_data['claim_deductible_contributions'] = total_paid_into_deductible
    report_data['claim_remaining_deductible'] = claim_remaining_deductible
    report_data['claim_new_risk_score'] = round(new_risk_score[1], 1)
    report_data['claim_new_premium'] = round(new_premium, 0)
    report_data['no_prior_claims'] = total_prior_claims
    return report_data


if __name__ == "__main__":
    db = dataset.connect('sqlite:///AutoInsurace.db', row_type=stuf)
    #risk_score_change(db, "100420")
    #claim_cost_to_repair(1, 7000)
