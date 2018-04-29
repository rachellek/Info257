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

class VehiclesByCustomerIdHandler(tornado.web.RequestHandler):
    def initialize(self, database):
        self.db = database
    def get(self, customer_id):
        vehicles = database_helpers.query_table_by_value(self.db, "vehicle", "CustomerID", customer_id)
        out = []
        for v in vehicles:
            vehicle_type = database_helpers.query_table_by_value(self.db, "vehicletype", "VehicleTypeID", v['VehicleTypeID'])
            out.append((v, vehicle_type[0]))
        # returns list of tuples containing vehicle and vehicletype
        self.write(json.dumps(out))

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
            (r"/vehicles/bycustomer/([0-9]+)", VehiclesByCustomerIdHandler, dict(database=db))
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
