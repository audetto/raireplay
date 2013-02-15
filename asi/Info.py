

from asi import Config

# this returns some JavaScript like
# setUserLocation("ESTERO");
userLocation = "http://mediapolis.rai.it/relinker/relinkerServlet.htm?cont=826819"

# this one is from TF1
userIP = "http://api.prod.capptain.com/ip-to-country"

def display(grabber, width):

    rai = grabber.open(userLocation).read().decode("ascii")
    ip = grabber.open(userIP).read().decode("ascii")

    print("=" * width)

    print("Root folder:", Config.rootFolder)
    print("Location:   ", Config.programFolder)
    print("RAI:        ", rai)
    print("IP:         ", ip)

    print()
