from asi import Utils
from asi import Config

# this returns some JavaScript like
# setUserLocation("ESTERO");
userLocation = "http://mediapolis.rai.it/relinker/relinkerServlet.htm?cont=826819"

# this one is from TF1
userIP = "http://api.prod.capptain.com/ip-to-country"

def display(grabber, width, password):

    rai = Utils.getStringFromUrl(grabber, userLocation)
    ip = Utils.getStringFromUrl(grabber, userIP)
    tor = Utils.getTorExitNodes(password)

    print("=" * width)

    print("Root folder:", Config.rootFolder)
    print("ExitNodes:  ", tor)
    print("Location:   ", Config.programFolder)
    print("RAI:        ", rai)
    print("IP:         ", ip)

    print()
