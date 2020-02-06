import tornado.ioloop
import tornado.web
from coronadash.handlers.powhandler import PowHandler
from coronadash.lib.application import app, route

@app.make_routes()
class HelloHandler(PowHandler):
    @route(r'/hello', dispatch=["get"])
    def hello(self):
        self.write("Hello world!")