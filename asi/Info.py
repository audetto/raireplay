import re
import json

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

geoIP = "https://freegeoip.net/json/"

targets = {'it': 'ITA'}

def searchTor(grabber, width, country, attemptsAndSkip):
    args = attemptsAndSkip.split(",")
    attempts = int(args[0])

    if len(args) > 1:
        skip = int(args[1])
    else:
        skip = 0

    excludes = ""

    p = re.compile('setUserLocation\("(.*)\)"')

    target = targets[country]

    for a in range(1, attempts):
        Tor.setTorExcludeNodes(excludes)

        rai = Utils.getStringFromUrl(grabber, userLocation)
        ip = Utils.getStringFromUrl(grabber, userIP)

        detected = p.match(rai)

        if detected:
            s = detected.group(1)
            if s == target:
                if skip > 0:
                    print(ip, s, "SKIP")
                    skip -= 1
                else:
                    print(ip, s, "ACCEPTED")
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
