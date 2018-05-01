#!/usr/bin/env python

import argparse
import json
import logging
import sys

#Tornado tools
import tornado.ioloop
import tornado.web
import os

import database_helpers
import backend

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.INFO)

# Define MainHandler to render the web
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class CustomersHandler(tornado.web.RequestHandler):
    def initialize(self, database):
        self.db = database
    def get(self):
        customers = database_helpers.read_table(self.db, "customer")
        self.write(json.dumps(customers))

class StatsHandler(tornado.web.RequestHandler):
    def initialize(self, database):
        self.db = database
    def get(self):
        customers = database_helpers.read_table(self.db, "customer")
        vehicles = database_helpers.read_table(self.db, "vehicle")
        vehicle_types = database_helpers.read_table(self.db, "vehicletype")
        policies = database_helpers.read_table(self.db, "policy")
        claims = database_helpers.read_table(self.db, "claims")
        reply = {"customers": len(customers), "vehicles": len(vehicles), "vehicle_types": len(vehicle_types), "policies": len(policies), "claims": len(claims)}
        self.write(json.dumps(reply))

class VehiclesByCustomerIdHandler(tornado.web.RequestHandler):
    def initialize(self, database):
        self.db = database
    def get(self, customer_id):
        vehicles = database_helpers.query_table_by_value(self.db, "vehicle", "CustomerID", customer_id)
        out = []
        try:
            for v in vehicles:
                vehicle_type = database_helpers.query_table_by_value(self.db, "vehicletype", "VehicleTypeID", v['VehicleTypeID'])
                out.append((v, vehicle_type[0]))
        except:
            pass
        # returns list of tuples containing vehicle and vehicletype
        self.write(json.dumps(out))

class CustomerByIdHandler(tornado.web.RequestHandler):
    def initialize(self, database):
        self.db = database
    def get(self, customer_id):
        customer = database_helpers.query_table_by_value(self.db, "customer", "CustomerID", customer_id)
        claims = database_helpers.query_table_by_value(self.db, "claims", "CustomerID", customer_id)
        vehicles = database_helpers.query_table_by_value(self.db, "vehicle", "CustomerID", customer_id)
        policy = database_helpers.query_table_by_value(self.db, "policy", "PolicyID", customer[0]['PolicyID'])
        vehicles_list = []
        for v in vehicles:
            vehicle_type = database_helpers.query_table_by_value(self.db, "vehicletype", "VehicleTypeID", v['VehicleTypeID'])
            vehicles_list.append(vehicle_type[0])
        reply = {
            "customer_name": customer[0]['Name'], 
            "customer_id": customer_id, 
            "premium": customer[0]['Premium'],
            "deductible": policy[0]['Deductible'],
            "policy_details": policy[0]['PolicyDetails'],
            "number_vehicles": len(vehicles),
            "number_claims": len(claims),
            "risk_score": customer[0]['RiskScore'],
            "vehicles": vehicles_list
        }
        self.write(json.dumps(reply))

class ClaimSubmitHandler(tornado.web.RequestHandler):
    def initialize(self, database, logger):
        self.db = database
        self.logger = logger
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        keys = database_helpers.append_table(self.db, [data], "claims")
        self.logger.info("Added claim id {} | {}".format(keys[0], data))
        # since the db assigns the claim id, append it to our package for report generation
        data['ClaimID'] = keys[0]
        report_data = backend.generate_report(self.db, data)
        self.write(json.dumps({"status": "success", "report": report_data}))

# Create my app
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=8888, help="Port that the service runs on (default: 8888)")
    parser.add_argument("-d", "--db_name", default="AutoInsurace.db", help="Path to the database file (default: AutoInsurace.db")
    args = parser.parse_args()
    logger = logging.getLogger("AutoInsurace")

    # Open the database
    db = database_helpers.open_db(args.db_name)

    # Establish handlers for various db io
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/customers", CustomersHandler, dict(database=db)),
            (r"/customer/([0-9]+)", CustomerByIdHandler, dict(database=db)),
            (r"/vehicles/bycustomer/([0-9]+)", VehiclesByCustomerIdHandler, dict(database=db)),
            (r"/claims/submit", ClaimSubmitHandler, dict(database=db, logger=logger)),
            (r"/stats", StatsHandler, dict(database=db))
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    app.listen(args.port)

    logger.info("Starting server on port: {}".format(args.port))

    try:
        # start the ioloop
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        # ensure that the event loop stops cleanly on interrupt
        tornado.ioloop.IOLoop.instance().stop()
