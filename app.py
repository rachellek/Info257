import argparse
import logging
import sqlite3
import sys

#Tornado tools
import tornado.ioloop
import tornado.web
import os


conn = sqlite3.connect('AutoInsurace.db')


logging.basicConfig(
    format="[%(asctime)s][%(name)s](%(levelname)s) %(message)s", level=logging.INFO)

def get_customers():
    c = conn.cursor()

    # Query database
    c.execute('SELECT * FROM customer')
    print(c.fetchone())

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


# Define MainHandler to render the web
class MainHandler(tornado.web.RequestHandler):
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
            (r"/", MainHandler)
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    app.listen(args.port)

    logger.info("Starting server on port: {}".format(args.port))

    get_customers()

    try:
        # start the ioloop
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        # ensure that the event loop stops cleanly on interrupt
        tornado.ioloop.IOLoop.instance().stop()
