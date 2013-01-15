from __future__ import print_function

from asi import Utils
from asi import Info
from asi import Replay
from asi import Page
from asi import Item
from asi import TG
from asi import Demand
from asi import Config
from asi import Pluzz
from asi import TF1

import urlgrabber.grabber


def displayOrGet(item, nolist, info, get, format, bwidth):
    if info:
        item.display()
    elif not nolist:
        # this is list
        fmt = "{0:>9}: {1} {2}"
        print(item.short(unicode(fmt)))

    if get:
        item.download(Config.programFolder, format, bwidth)


def listDisplayOrGet(items, nolist, info, get, format, bwidth):
    if nolist:
        print()
        print("INFO: {0} programmes found".format(len(items)))

    for p in sorted(items.itervalues(), key = lambda x: x.datetime):
        displayOrGet(p, nolist, info, get, format, bwidth)


def find(db, pid, subset):
    if pid in db:
        subset[pid] = db[pid]
    else:
        fmt = unicode("{2}")
        match = pid.lower()
        for pid, p in db.iteritems():
            s = p.short(fmt).lower()
            s = Utils.removeAccents(s)
            if s.find(match) != -1:
                subset[pid] = p


def process(args):
    db = {}

    proxy = None

    if args.tor != None:
        # we use privoxy to access tor
        Utils.setTorExitNodes(args.tor)
        proxy = { "http" : "http://127.0.0.1:8118" }
    else:
        if args.proxy != None:
            proxy = { "http" : args.proxy }

    # got from the iphone
    # required for TF1 - www.wat.tv
    userAgent = "AppleCoreMedia/1.0.0.9B206 (iPod; U; CPU OS 5_1_1 like Mac OS X; en_us)"

    grabber = urlgrabber.grabber.URLGrabber(proxies = proxy, quote = 0, user_agent = userAgent)

    if args.ip:
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
                p.follow(db, args.download)
                follows = follows[1:] # continue with one element less
            else:
                print("Too many/few ({0}) items selected during while processing follow '{1}'".format(len(subset), follows[0]))
                # replace the db with the subset and display it
                db = subset
                break

    if args.replay:
        Replay.download(db, grabber, args.download)

    if args.tg:
        TG.download(db, grabber, args.download)

    if args.pluzz:
        Pluzz.download(db, grabber, args.download)

    if args.tf1:
        TF1.download(db, grabber, args.download)

    if args.item != None:
        p = Item.Demand(grabber, args.item, args.download, len(db))
        db[p.pid] = p

    if args.pid:
        subset = {}
        for pid in args.pid:
            find(db, pid, subset)
    else:
        subset = db

    listDisplayOrGet(subset, args.nolist, args.info, args.get, args.format, args.bwidth)
