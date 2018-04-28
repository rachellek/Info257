import argparse
import logging
import sqlite3 as lite
import sys

#Tornado tools
import tornado.ioloop
import tornado.web
import os

logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.INFO)

# Define MainHandler to render the web
class MainHandler(tornado.web.RequestHandler):
    def init(self, logger):
        self.logger = logger

    def get(self):
        self.render("index.html")

# Create my app
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=8888, help="Port that the service runs on (default: 8888)")
    args = parser.parse_args()
    logger = logging.getLogger("AutoInsurace")

    app = tornado.web.Application(
        [
            (r"/", MainHandler, dict(logger=logger))
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
