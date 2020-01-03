import json

from asi import utils
from asi import config
from asi import tor

userIP = "https://api.ipify.org"
geoIP = "https://freegeoip.net/json/"


def search_tor(grabber, country, attempts_and_skip):
    args = attempts_and_skip.split(",")
    attempts = int(args[0])

    if len(args) > 1:
        skip = int(args[1])
    else:
        skip = 0

    excludes = ""

    for a in range(attempts):
        tor.set_tor_exclude_nodes(excludes)

        ip, geo = get_geo_ip(grabber)

        if geo.upper() == country.upper():
            if skip > 0:
                # skip the first matches if they have not worked
                print(ip, geo, "SKIP")
                skip -= 1
            else:
                print(ip, geo, "ACCEPTED")
                tor.set_tor_exit_nodes(ip)
                break

        if excludes:
            excludes = excludes + "," + ip
        else:
            excludes = ip


def get_geo_ip(grabber):
    geo = utils.get_string_from_url(grabber, geoIP)
    data = json.loads(geo)
    ip = data['ip']
    country = data['country_code']
    return ip, country


def display(grabber, width):
    ip, country = get_geo_ip(grabber)

    exit_nodes = tor.get_tor_exit_nodes()
    excluded = tor.get_tor_exclude_nodes()

    print("=" * width)

    print("Root folder:", config.root_folder)
    print("Location:   ", config.program_folder)
    print("IP:         ", ip)
    print("Country:    ", country)
    print("Exit:       ", exit_nodes)
    print("Excluded:   ", excluded)

    print()
