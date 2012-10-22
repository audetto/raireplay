#! /usr/bin/python

from __future__ import print_function

import sys
import json
import codecs
import os
import argparse
import urlgrabber.grabber
import urlgrabber.progress

from datetime import date
from datetime import timedelta
from asi import Program
from asi import Demand

rootFolder = os.path.expanduser("~/.raireplay")
dataFolder = os.path.join(rootFolder, "data")
programFolder = os.path.join(rootFolder, "programs")
channels = {"1": "RaiUno", "2": "RaiDue", "3": "RaiTre", "31": "RaiCinque"}
baseUrl = "http://www.rai.it/dl/portale/html/palinsesti/replaytv/static"

def parseItem(channel, date, time, value):
    name = value["t"]
    desc = value["d"]
    secs = value["l"]

    minutes = 0
    if secs != "":
        minutes = int(secs) / 60

    h264 = value["h264"]
    tablet = value["urlTablet"]
    smartPhone = value["urlSmartPhone"]
    pid = value["i"]

    if h264 != "" or tablet != "" or smartPhone != "" :
        p = Program.Program(channels[channel], date, time, pid, minutes, name, desc, h264, tablet, smartPhone)
        return p

    return None


def process(filename, db):
    f = codecs.open(filename, "r", encoding="latin1")
    o = json.load(f)

    for k1, v1 in o.iteritems():
        if k1 == "now":
            continue
        if k1 == "defaultBannerVars":
            continue

        channel = k1

        for date, v2 in v1.iteritems():
            for time, value in v2.iteritems():
                p = parseItem(channel, date, time, value)

                if p != None:
                    if p.pid in db:
                        print("WARNING: duplicate pid {0}".format(p.pid))
                        #                        db[pid].display()
                        #                        p.display()

                    db[p.pid] = p


def download(db, type):
    if not os.path.exists(dataFolder):
        os.makedirs(dataFolder)

    g = urlgrabber.grabber.URLGrabber(progress_obj = urlgrabber.progress.TextMeter())
    today = date.today()

    for x in range(1, 8):
        day = today - timedelta(days = x)
        strDate = day.strftime("_%Y_%m_%d")

        for channel in channels.itervalues():
            filename = channel + strDate + ".html"
            url = baseUrl + "/" + filename
            localName = os.path.join(dataFolder, filename)

            if type == "always" or (type == "update" and not os.path.exists(localName)):
                filename = g.urlgrab(url, filename = localName)

            if os.path.exists(localName):
                process(localName, db)

    print()


def list(db):
    for p in sorted(db.itervalues(), key = lambda x: x.datetime):
        print(p.short())


def display(item):
    item.display()


def main():

    parser = argparse.ArgumentParser(description = "Rai Replay")
    parser.add_argument("--download", action = "store", default = "update", choices = ["always", "update", "never"],
                        help = "Default is update")
    parser.add_argument("--list", action = "store_true", default = False)
    parser.add_argument("--get", action = "store_true", default = False)
    parser.add_argument("--format", action = "store", choices = ["h264", "ts"])
    parser.add_argument("--url", action = "store", help = "RAI On Demand")
    parser.add_argument("pid", nargs = "*")

    args = parser.parse_args()

    db = {}
    download(db, args.download)

    if args.list:
        list(db)

    if len(args.pid) > 0:
        for pid in args.pid:
            if pid in db:
                p = db[pid]
                display(p)
                if args.get:
                    p.download(programFolder, args.format)
            else:
                print("PID {0} not found".format(pid))
    elif args.url != None:
        d = Demand.Demand(args.url)
        d.display()
    else:
        print()
        print("INFO: {0} programmes found".format(len(db)))

    print()

# is this required??? seems a bit of pythonic nonsense
# all RAI html is encoded in "latin1" (decoded as we read)
#
# and it seems that redirecting the output requires a "latin1" terminal
# done here

sys.stdout = codecs.getwriter("latin1")(sys.stdout)
main()
