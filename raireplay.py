#! /usr/bin/python

from __future__ import print_function

import sys
import codecs
import argparse

from asi import Info
from asi import Program
from asi import Page
from asi import Item
from asi import Demand
from asi import Config

import urlgrabber.grabber

def list(db):
    for p in sorted(db.itervalues(), key = lambda x: x.datetime):
        print(p.short())


def displayOrGet(item, grabber, list, get, format):
    if list:
        print(item.short())
    else:
        item.display()
    if get:
        item.download(grabber, Config.programFolder, format)


def find(db, pid, subset):
    if pid in db:
        subset.add(db[pid])
    else:
        match = pid.lower()
        for p in db.itervalues():
            s = p.short().lower()
            if s.find(match) != -1:
                subset.add(p)


def main():

    parser = argparse.ArgumentParser(description = "Rai Replay")

    parser.add_argument("--download", action = "store", default = "update", choices = ["always", "update", "never"],
                        help = "Default is update")
    parser.add_argument("--format", action = "store", choices = ["h264", "ts"])
    parser.add_argument("--info", action = "store_true", default = False)
    parser.add_argument("--tor", action = "store_true", default = False)

    parser.add_argument("--page",   action = "store", help = "RAI On Demand Page")
    parser.add_argument("--replay", action = "store_true", default = False, help = "RAI Replay")
    parser.add_argument("--ondemand", action = "store_true", default = False, help = "RAI On Demand List")

    parser.add_argument("--list", action = "store_true", default = False)
    parser.add_argument("--get", action = "store_true", default = False)
    parser.add_argument("pid", nargs = "*")

    parser.add_argument("--item", action = "store", help = "RAI On Demand Item")

    args = parser.parse_args()

    db = {}

    proxy = None

    if args.tor:
        # we use privoxy to access tor
        proxy = { "http" : "http://127.0.0.1:8118" }

    grabber = urlgrabber.grabber.URLGrabber(proxies = proxy)

    if args.info:
        Info.display(grabber, Config.rootFolder)
        return

    if args.replay:
        Program.download(db, grabber, Config.replayFolder, args.download)

    if args.page != None:
        Page.download(db, grabber, args.page, Config.pageFolder, args.download)

    if args.ondemand:
        Demand.download(db, grabber, Config.demandFolder, args.download)

    if len(args.pid) > 0:
        subset = set()
        for pid in args.pid:
            find(db, pid, subset)

            for p in sorted(subset, key = lambda x: x.datetime):
                displayOrGet(p, grabber, args.list, args.get, args.format)

    elif args.item != None:
        d = Item.Demand(grabber, args.item, Config.itemFolder, args.download)
        d.display()

    elif args.list:
        list(db)

    else:
        print()
        print("INFO: {0} programmes found".format(len(db)))

    print()

# is this required??? seems a bit of pythonic nonsense
# all RAI html is encoded in "utf-8" (decoded as we read)
#
# and it seems that redirecting the output (e.g. "| less") requires am explicit encoding
# done here
if sys.stdout.encoding == None:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout, "ignore")

main()
