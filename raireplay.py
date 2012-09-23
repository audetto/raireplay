#! /usr/bin/python

from __future__ import print_function

import json
import sys
import os
import argparse
import urlgrabber.grabber
import urlgrabber.progress

from datetime import date
from datetime import timedelta
from asi import Program

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
    pid = value["i"]

    if h264 != "" or tablet != "":
        p = Program.Program(channels[channel], date, time, pid, minutes, name, desc, h264, tablet)
        return p

    return None


def process(filename, db):
    f = open(filename, "r")
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
                        print("WARNING: duplicate pid", p.pid)
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
    for p in db.itervalues():
        print(p.pid + ":", p.date, p.name)


def display(item):
    item.display()


def main():

    parser = argparse.ArgumentParser(description = "Rai Replay")
    parser.add_argument("--download", action = "store", default = "update", choices = ["always", "update", "never"],
                        help = "Default is update")
    parser.add_argument("--list", action = "store_true", default = False)
    parser.add_argument("--get", action = "store_true", default = False)
    parser.add_argument("--format", action = "store", default = "h264", choices = ["h264", "tablet"])
    parser.add_argument("pid", nargs = "?")

    args = parser.parse_args()

    db = {}
    download(db, args.download)

    if args.list:
        list(db)

    if args.pid != None:
        p = db[args.pid]
        display(p)
        if args.get:
            p.download(programFolder, args.format)
    else:
        print()
        print("INFO:", len(db), "programmes")

    print()

main()
