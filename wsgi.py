from wsgiref.simple_server import make_server
from RequestHandler import RequestHandler
from beaker.middleware import SessionMiddleware
from Config import Config
from PidLock import PidLock
import threading



try:
	#requestHandler = RequestHandler()

	#Enable beaker sessions
	#RequestHandler= SessionMiddleware(RequestHandler, Config.session_opts)
	#RequestHandler.__init__ = SessionMiddleware(RequestHandler.__init__, Config.session_opts)

	RequestHandler.handleNewRequest = SessionMiddleware(RequestHandler.handleNewRequest, Config.session_opts)
	

	
	#Make a file to show we're running
	with PidLock() as lockFile:
		#Make server
		
		httpd = make_server('',8000,RequestHandler.handleNewRequest)
		print "Serving on port 8000"

		#Create and set the shutdown thread for the wsgi server
		RequestHandler.initializeStatics( httpd, threading.Thread(target=RequestHandler.shutdown) )
		

		#SERVE!!!
		print "Serving forever!"
		httpd.serve_forever(5) 	#poll_interval as arg
		
	print "Bye!"
except Exception, e:
	print "An exception occured while trying to launch wsgi:",e
finally:
	f=open("wsgi_pid.lock", "w")	
	f.write("0")
	f.close()
	