
import dataset
from stuf import stuf
import pprint

#Given a new insurance claim, determine whether to increase a customer's premium
def premium_change(db, CustomerID):
    claims = list(db.query("Select * from claims WHERE CustomerID==" + CustomerID))

    New_RiskScore = (sum(1 if int(claim['Severity']) == 1 else 0 for claim in claims) *1.2 + \
    sum(1 if int(claim['Severity']) == 2 else 0 for claim in claims) *1.4 + \
    sum(1 if int(claim['Severity']) == 3 else 0 for claim in claims) *1.8)
    print("Customer new Risk Score {}".format(New_RiskScore))

    RiskScore = int(list(db.query("Select RiskScore from customer WHERE CustomerID==" + CustomerID))[0]['RiskScore'])
    print("Customer original Risk Score {}".format(RiskScore))

    if New_RiskScore > (RiskScore * 1.5):
        print("The customer's premium has increased")
        return (True, New_RiskScore)
    else:
        print("The customer's premium has not changed")
        return (False, RiskScore)

if __name__ == "__main__":
    db = dataset.connect('sqlite:///AutoInsurace.db', row_type=stuf)
    premium_change(db, "100420")
