from __future__ import print_function

from asi import Info
from asi import Replay
from asi import Page
from asi import Item
from asi import Demand
from asi import Config
from asi import Pluzz
from asi import Utils

import urlgrabber.grabber


def displayOrGet(item, grabber, list, get, format, bwidth, html):
    if list:
        if html:
            fmt = "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>"
        else:
            fmt = "{0:>7}: {1} {2}"
        print(item.short(unicode(fmt)))

    else:
        item.display()

    if get:
        item.download(grabber, Config.programFolder, format, bwidth)


def listDisplayOrGet(items, grabber, list, get, format, bwidth, html):
    if (list and html):
        print("<!DOCTYPE HTML>")
        print("<html>")
        print('<head><meta charset="utf-8"></head>')
        print("<body>")
        print('<table border="1">')
        print("<tr><td>PID</td><td>Time</td><td>Title</td></tr>")

    for p in sorted(items.itervalues(), key = lambda x: x.datetime):
        displayOrGet(p, grabber, list, get, format, bwidth, html)

    if (list and html):
        print("</table></body></html>")


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
        Replay.download(db, grabber, args.download)

    if args.pluzz:
        Pluzz.download(db, grabber, args.download)

    if args.pid:
        subset = {}
        for pid in args.pid:
            find(db, pid, subset)

        listDisplayOrGet(subset, grabber, args.list, args.get, args.format, args.bwidth, args.html)

    elif args.item != None:
        p = Item.Demand(grabber, args.item, args.download)
        displayOrGet(p, grabber, args.list, args.get, args.format, args.bwidth)

    elif args.list:
        listDisplayOrGet(db, grabber, args.list, args.get, args.format, args.bwidth, args.html)

    else:
        print()
        print("INFO: {0} programmes found".format(len(db)))
