import os
class PidLock:
	def __init__(self):
		self.pid =os.getpid()
		self.filename="wsgi_pid.lock"
		
	def __enter__(self):	
		print "writing lock file with pid=%s"%(self.pid)
		f=open(self.filename, "w")	
		f.write("%s"%(self.pid))
		f.close()
	
	def __exit__(self,type, value, tb):
		print "Resetting lock file"
		f=open(self.filename, "w")	
		f.write("0")
		f.close()
	
	def __del__(self):
		self.__exit__()