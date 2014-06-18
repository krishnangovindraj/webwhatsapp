#addUserTest
from Core import WWMCore
import argparse,time

core = WWMCore()
core.initDBI()
'''
phone ='919975199490' #country code followed by 10 digit
name = 'Krishnan Govindraj'
password = 'weakpass'
email = 'f2012207@goa.bits-pilani.ac.in'
whatsapp_pass='GwpsEyeo4PwqMT8hRXY2tpQnb88='
#AESKey = core.genAESKey(password)
'''


parser = argparse.ArgumentParser(description='WWM Add user option')
loginInfo = parser.add_argument_group("loginInfo")

loginInfo.add_argument('-n','--name', help='name (Wrap in quotes if you have a space)', action="store", required=True ,nargs=1, default=False)
loginInfo.add_argument('-e','--email', help='email', action="store", required=True , nargs=1, default=False)
loginInfo.add_argument('-f','--phone', help='phone number', action="store", required=True ,nargs=1, default=False)
loginInfo.add_argument('-p','--pass', help='password for the site to use', action="store", required=True , nargs=1, default=False)
loginInfo.add_argument('-w','--wapass', help='whatsapp password ( get using wart/from your phone )', action="store", required=True , nargs=1, default=False)


args = vars(parser.parse_args())

print "\n adding:\n"
print args

phone = args["phone"][0]
name = args["name"][0]
email = args["email"][0]
sitepass = args["pass"][0]
wapass = args["wapass"][0]

core.addUser(phone,email, name,sitepass,wapass)
print "Done,probably"