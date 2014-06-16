from wsgiref.simple_server import make_server
from RequestHandler import RequestHandler
from beaker.middleware import SessionMiddleware
from Config import Config

requestHandler = RequestHandler()

#Enable beaker sessions
requestHandler.requestHandler = SessionMiddleware(requestHandler.requestHandler, Config.session_opts)

#Make server
httpd = make_server('',8000,requestHandler.requestHandler)
print "Serving on port 8000"

#SERVE!!!
httpd.serve_forever()