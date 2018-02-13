import json

from asi import Utils
from asi import Config
from asi import Tor

userIP = "https://api.ipify.org"
geoIP = "https://freegeoip.net/json/"

def searchTor(grabber, width, country, attemptsAndSkip):
    args = attemptsAndSkip.split(",")
    attempts = int(args[0])

    if len(args) > 1:
        skip = int(args[1])
    else:
        skip = 0

    excludes = ""

    for a in range(attempts):
        Tor.setTorExcludeNodes(excludes)

        ip, geo = getGeoIp(grabber)

        if geo.upper() == country.upper():
            if skip > 0:
                # skip the first matches if they have not worked
                print(ip, geo, "SKIP")
                skip -= 1
            else:
                print(ip, geo, "ACCEPTED")
                Tor.setTorExitNodes(ip)
                break

        if excludes:
            excludes = excludes + "," + ip
        else:
            excludes = ip


def getGeoIp(grabber):
    geo = Utils.getStringFromUrl(grabber, geoIP)
    data = json.loads(geo)
    ip = data['ip']
    country = data['country_code']
    return ip, country


def display(grabber, width):
    ip, country = getGeoIp(grabber)

    exitNodes = Tor.getTorExitNodes()
    excluded = Tor.getTorExcludeNodes()

    print("=" * width)

    print("Root folder:", Config.rootFolder)
    print("Location:   ", Config.programFolder)
    print("IP:         ", ip)
    print("Country:    ", country)
    print("Exit:       ", exitNodes)
    print("Excluded:   ", excluded)

    print()
