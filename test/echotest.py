from Examples.EchoClient import WhatsappEchoClient

import base64

login = "919496889970"
password = "kXI2JIsolXD2p+Mk84DF6Kpn1uc="
password = base64.b64decode(bytes(password.encode('utf-8')))


echoClient = WhatsappEchoClient("919975199490", "I SAID: ECHO CLIENT SAYS HI!", True)

echoClient.login(login,password)