## This code is 6 years outdated and will definitely not work. 
(Not that it worked all that great back then either :( )

README:
Aim: Make a web client for whatsapp. Do whatever you want as long as that's achieved. And rewrite this readme when you're done


NOTE: 
You need Yowsup Library copied to the same directory. ie .\Yowsup has to contain all the Yowsup library files

OTHER DEPENDENCIES:
	MySQLdb ( If you can rewrite it to have a server independent solution, Please do :) )

Usage:
	Import the webwhatsapp.sql file into a database name webwhatasapp ( or reconfigure your config.py mysql_ fields accordingly )
	adduser by running 	>py adduser.py	through the commandline ( Web interface adding users is an easy to do )
	Launch an instance using 	>py wsgi.py
	visit http://host:portnumber
	Login using the password you specified.
	That should be it

Repo: https://github.com/krishnangovindraj/webwhatsapp
Contact: krishnancmf8@gmail.com
