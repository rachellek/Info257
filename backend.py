
import dataset
from stuf import stuf
import pprint

#Given a new insurance claim, determine whether to increase a customer's premium
def premium_change(db, CustomerID):
    claims = db.query("Select ClaimID, Severity from claims WHERE CustomerID==" + CustomerID)
    pprint.pprint("Customer claims {}".format(claims))

    New_RiskScore = (sum(1 if claims ==1 else 0 for claim in claims) *.2 + \
    sum(1 if claims ==2 else 0 for claim in claims) *.4 + \
    sum(1 if claims ==3 else 0 for claim in claims) *.8)
    print("Customer new Risk Score {}".format(New_RiskScore))

    RiskScore = db.query("Select RiskScore from customer WHERE CustomerID==" + CustomerID)
    print("Customer original Risk Score {}".format(RiskScore))

    if New_RiskScore > (RiskScore * 1.5):
        print("The customer's premium has increased")
    else:
        print("The customer's premium has not changed")

if __name__ == "__main__":
    db = dataset.connect('sqlite:///AutoInsurace.db', row_type=stuf)
    premium_change(db, "100420")
