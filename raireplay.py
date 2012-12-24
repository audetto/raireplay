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
from asi import Pluzz
from asi import Utils

import urlgrabber.grabber

def list(db):
    for p in sorted(db.itervalues(), key = lambda x: x.datetime):
        print(p.short())


def displayOrGet(item, grabber, list, get, format, bwidth):
    if list:
        print(item.short())
    else:
        item.display()
    if get:
        item.download(grabber, Config.programFolder, format, bwidth)


def find(db, pid, subset):
    if pid in db:
        subset[pid] = db[pid]
    else:
        match = pid.lower()
        for pid, p in db.iteritems():
            s = p.short().lower()
            s = Utils.remove_accents(s)
            if s.find(match) != -1:
                subset[pid] = p


def main():

    parser = argparse.ArgumentParser(description = "Rai Replay")

    parser.add_argument("--download", action = "store", default = "update", choices = ["always", "update", "never"],
                        help = "Default is update")
    parser.add_argument("--format", action = "store", choices = ["h264", "ts"])
    parser.add_argument("--bwidth", action = "store")
    parser.add_argument("--info", action = "store_true", default = False)
    parser.add_argument("--tor", action = "store_true", default = False)
    parser.add_argument("--proxy", action = "store")

    parser.add_argument("--page",   action = "store", help = "RAI On Demand Page")
    parser.add_argument("--replay", action = "store_true", default = False, help = "RAI Replay")
    parser.add_argument("--ondemand", action = "store_true", default = False, help = "RAI On Demand List")
    parser.add_argument("--pluzz", action = "store_true", default = False, help = "Pluzz France Television")

    parser.add_argument("--follow", action = "append")

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
    else:
        if args.proxy != None:
            proxy = { "http" : args.proxy }


    grabber = urlgrabber.grabber.URLGrabber(proxies = proxy, quote = 0)

    if args.info:
        Info.display(grabber, Config.rootFolder)
        return

    if args.page != None:
        Page.download(db, grabber, args.page, args.download)

    if args.ondemand:
        Demand.download(db, grabber, args.download)

    if args.follow != None:
        follows = args.follow
        while follows:
            subset = {}
            p = find(db, follows[0], subset)
            if len(subset) == 1:
                # continue follow calculation
                db = {}
                p = next(subset.itervalues())
                p.follow(db, grabber, args.download)
                follows = follows[1:] # continue with one element less
            else:
                print("Too many/few ({0}) items selected during while processing follow '{1}'".format(len(subset), follows[0]))
                # replace the db with the subset and display it
                db = subset
                break

    if args.replay:
        Program.download(db, grabber, args.download)

    if args.pluzz:
        Pluzz.download(db, grabber, args.download)

    if args.pid:
        subset = {}
        for pid in args.pid:
            find(db, pid, subset)

            for p in sorted(subset.itervalues(), key = lambda x: x.datetime):
                displayOrGet(p, grabber, args.list, args.get, args.format, args.bwidth)

    elif args.item != None:
        p = Item.Demand(grabber, args.item, args.download)
        displayOrGet(p, grabber, args.list, args.get, args.format, args.bwidth)

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

if __name__ == '__main__':
    main()
