#Database tools
import sqlite3 as lite
import sys

#Tornado tools
import tornado.ioloop
import tornado.web
import os

# Define MainHandler to render the web
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

# Create my app
if __name__ == "__main__":
    app = tornado.web.Application(
        [
            (r"/", MainHandler)
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
