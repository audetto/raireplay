import json

from asi import Utils
from asi import Config
from asi import Tor

userIP = "https://api.ipify.org"
geoIP = "https://freegeoip.net/json/"


def search_tor(grabber, width, country, attempts_and_skip):
    args = attempts_and_skip.split(",")
    attempts = int(args[0])

    if len(args) > 1:
        skip = int(args[1])
    else:
        skip = 0

    excludes = ""

    for a in range(attempts):
        Tor.set_tor_exclude_nodes(excludes)

        ip, geo = get_geo_ip(grabber)

        if geo.upper() == country.upper():
            if skip > 0:
                # skip the first matches if they have not worked
                print(ip, geo, "SKIP")
                skip -= 1
            else:
                print(ip, geo, "ACCEPTED")
                Tor.set_tor_exit_nodes(ip)
                break

        if excludes:
            excludes = excludes + "," + ip
        else:
            excludes = ip


def get_geo_ip(grabber):
    geo = Utils.get_string_from_url(grabber, geoIP)
    data = json.loads(geo)
    ip = data['ip']
    country = data['country_code']
    return ip, country


def display(grabber, width):
    ip, country = get_geo_ip(grabber)

    exit_nodes = Tor.get_tor_exit_nodes()
    excluded = Tor.get_tor_exclude_nodes()

    print("=" * width)

    print("Root folder:", Config.root_folder)
    print("Location:   ", Config.program_folder)
    print("IP:         ", ip)
    print("Country:    ", country)
    print("Exit:       ", exit_nodes)
    print("Excluded:   ", excluded)

    print()
