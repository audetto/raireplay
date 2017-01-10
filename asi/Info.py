import re

from asi import Utils
from asi import Config
from asi import Tor

# this returns some JavaScript like
# setUserLocation("ESTERO");
userLocation = "http://mediapolis.rai.it/relinker/relinkerServlet.htm?cont=826819"

# an other use location
#http://mediapolisgs.rai.it/relinker/relinkerServlet.htm?cont=201342

# this one is from TF1
userIP = "http://api.prod.capptain.com/ip-to-country"
userIP = "https://api.ipify.org"

targets = {'it': 'ITA'}

def searchTor(grabber, width, country, attempts):
    excludes = ""

    p = re.compile('setUserLocation\("(.*)"\)')

    target = targets[country]

    for a in range(1, attempts):
        Tor.setTorExcludeNodes(excludes)

        rai = Utils.getStringFromUrl(grabber, userLocation)
        ip =  Utils.getStringFromUrl(grabber, userIP)

        detected = p.match(rai)

        if detected:
            s = detected.group(1)
            print(ip, s)
            if s == target:
                Tor.setTorExitNodes(ip)
                break

        if excludes:
            excludes = excludes + "," + ip
        else:
            excludes = ip


def display(grabber, width):

    rai = Utils.getStringFromUrl(grabber, userLocation)
    ip =  Utils.getStringFromUrl(grabber, userIP)

    exitNodes = Tor.getTorExitNodes()
    excluded = Tor.getTorExcludeNodes()

    print("=" * width)

    print("Root folder:", Config.rootFolder)
    print("Location:   ", Config.programFolder)
    print("RAI:        ", rai)
    print("IP:         ", ip)
    print("Exit:       ", exitNodes)
    print("Excluded:   ", excluded)

    print()
