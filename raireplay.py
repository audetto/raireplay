#! /usr/bin/python

from __future__ import print_function

import json
import sys
import os
import argparse

from datetime import date
from datetime import timedelta
from urlgrabber.grabber import URLGrabber

root_folder = os.path.expanduser("~/.raireplay")
channels = ["RaiUno", "RaiDue", "RaiTre", "RaiCinque"]
base_url = "http://www.rai.it/dl/portale/html/palinsesti/replaytv/static"


class Program:
    def __init__(self, date, time, pid, minutes, name, h264, tablet):
        self.date = date
        self.time = time
        self.pid = pid
        self.minutes = minutes
        self.name = name.encode('utf-8')
        self.h264 = h264
        self.tablet = tablet


def process(filename, db):
    f = open(filename, "r")
    o = json.load(f)

    for k1, v1 in o.iteritems():
        if k1 == "now":
            continue
        if k1 == "defaultBannerVars":
            continue

        for k2, v2 in v1.iteritems():
            for key, value in v2.iteritems():
                name = value["t"]
                secs = value["l"]
                minutes = 0
                if secs != "":
                    minutes = int(secs) / 60 

                h264 = value["h264"]
                tablet = value["urlTablet"]
                pid = value["i"]

                if h264 != "" or tablet != "":
                    p = Program(k2, key, pid, minutes, name, h264, tablet)
                    db[pid] = p


def download(db, type):
    g = URLGrabber()
    today = date.today()

    for x in range(1, 8):
        day = today - timedelta(days = x)
        str_date = day.strftime("_%Y_%m_%d")

        for channel in channels:
            filename = channel + str_date + ".html"
            url = base_url + "/" + filename
            local_name = os.path.join(root_folder, filename) 

            if type == "always" or (type == "update" and not os.path.exists(local_name)):
                print("Getting " + filename + "...", end = "")
                filename = g.urlgrab(url, filename = local_name)
                print("OK")

            if os.path.exists(local_name):
                process(local_name, db)


def display(db):
    for p in db.itervalues():
        print(p.pid, p.name)


def main():

    parser = argparse.ArgumentParser(description = "Rai Replay")
    parser.add_argument("--download", action = "store", default = "update", help = "always, [update], never")
    parser.add_argument("--display", action = "store_true", default = False)

    args = parser.parse_args()

    db = {}
    download(db, args.download)

    if args.display:
        display(db)


main()
