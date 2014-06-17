'''
	authtest.py
'''
from Core import WWMCore
from Session import Session
import argparse,time

parser = argparse.ArgumentParser(description='yowsup-cli Command line options')
loginInfo = parser.add_argument_group("loginInfo")
loginInfo.add_argument('-u','--userId', help='phone number', action="store", required=True ,nargs=1, default=False)
loginInfo.add_argument('-k','--key', help='security key', action="store", required=True , nargs=1, default=False)

args = vars(parser.parse_args())
userId = args["userId"][0]
AESkey = args["key"][0]



core = WWMCore(False,False)
core.initDBI()
session = Session(core, userId,AESkey)
session.getAuthData()
session.login()
timeLeft = 30
while timeLeft:
	time.sleep(1)
	print "%d\n"%timeLeft 
	timeLeft = timeLeft-1
'''
from Listener import Listener
import time

Listener = Listener(core)
time = 1
while time<10:
	time.sleep(2)
'''