from __future__ import print_function

from asi import Config

# this returns some JavaScript like
# setUserLocation("ESTERO");
userLocation = "http://mediapolis.rai.it/relinker/relinkerServlet.htm?cont=826819"

# this one is from TF1
userIP = "http://api.prod.capptain.com/ip-to-country"

def display(grabber, width):

    rai = grabber.urlread(userLocation)
    ip = grabber.urlread(userIP)

    print("=" * width)

    print("Root folder:", Config.rootFolder)
    print("Location:   ", Config.programFolder)
    print("RAI:        ", rai)
    print("IP:         ", ip)

    print()
