
from asi import Utils
from asi import Info
from asi import Replay
from asi import Page
from asi import Item
from asi import TG
from asi import Search
from asi import Junior
from asi import Demand
from asi import Config
from asi import Pluzz
from asi import TF1
from asi import Mediaset
from asi import Console
from asi import M6
from asi import Playlist

import re
import datetime
import urllib


def displayOrGet(item, nolist, info, get, options, grabber, fmt):
    if info:
        width = Console.terminal_width()
        item.display(width)
    elif not nolist:
        # this is list
        print(item.short(fmt))

    if get:
        try:
            item.download(Config.programFolder, options, grabber)
        except Exception as e:
            print("Exception: {0}".format(e))
            print()
            raise


def listDisplayOrGet(items, nolist, info, get, options, grabber):
    if nolist:
        print()
        print("INFO: {0} programmes found".format(len(items)))

    # dynamically select width of fields
    # as they change according to broadcaster
    # as we try not too make them too wide for nothing
    maxLengthOfPID = 0
    maxLengthOfChannel = 0

    for p in items.values():
        maxLengthOfPID = max(maxLengthOfPID, len(str(p.pid)))
        maxLengthOfChannel = max(maxLengthOfChannel, len(str(p.channel)))

    fmt = " {{0:>{0}}}: {{1}} {{2:{1}}} {{3}}".format(maxLengthOfPID, maxLengthOfChannel)

    for p in sorted(items.values(), key = lambda x: (x.datetime, x.title)):
        displayOrGet(p, nolist, info, get, options, grabber, fmt)


def filterByDate(db, value):
    # this nonsense is because today() returns the same as now()
    # and date.today() is not compatible with datetime... all pythonic!

    if value.lower() == "today":
        date = datetime.datetime.today().replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    elif value.lower() == "yesterday":
        date = datetime.datetime.today().replace(hour = 0, minute = 0, second = 0, microsecond = 0) - datetime.timedelta(days = 1)
    else:
        date = datetime.datetime.strptime(value, "%Y-%m-%d")

    lower_date = date
    upper_date = date + datetime.timedelta(days = 1)

    def checkDate(prog):
        prog_date = prog.datetime
        return prog_date >= lower_date and prog_date < upper_date

    res = dict((k, v) for k, v in db.items() if checkDate(v))
    return res


def filterByChannel(db, value):
    channel = value.lower()

    def checkChannel(v):
        return v.channel and (v.channel.lower() == channel)

    res = dict((k, v) for k, v in db.items() if checkChannel(v))
    return res


def find(db, pid, isre, subset):
    if pid in db:
        subset[pid] = db[pid]
    else:
        match = pid.lower()
        for ppid, p in db.items():
            title = p.title
            if isre:
                if re.match(pid, title):
                    subset[ppid] = p
            else:
                s = title.lower()
                s = Utils.removeAccents(s)
                if s.find(match) != -1:
                    subset[ppid] = p


def process(args):
    db = {}

    proxy = None

    if args.location:
        Config.programFolder = Config.createFolder(args.location)

    if args.tor:
        # we use privoxy to access tor
        Utils.setTorExitNodes(args.tor, args.tor_pass)
        proxy = { "http"  : "http://127.0.0.1:8118",
                  "https" : "http://127.0.0.1:8118" }
    else:
        if args.proxy:
            proxy = { "http"  : args.proxy,
                      "https" : args.proxy }

    proxyHandler = urllib.request.ProxyHandler(proxy)

    grabber = urllib.request.build_opener(proxyHandler)
    # we still need to install the global one, as sometimes we cannot pass in a new one
    # (m3u8 and urlretrieve)
    urllib.request.install_opener(grabber)

    grabberForDownload = None
    if args.tor and args.tor_only_metadata:
        # we do not want to use to for the actual download
        # only for the metadata
        grabberForDownload = urllib.request.build_opener()
    else:
        # use the same opener everywhere
        grabberForDownload = grabber

    if args.ip:
        width = Console.terminal_width()
        Info.display(grabber, width, args.tor)
        return

    if args.page:
        Page.download(db, grabber, args.page, args.download)

    if args.ondemand:
        Demand.download(db, grabber, args.download)

    if args.tg:
        TG.download(db, grabber, args.download)

    if args.junior:
        Junior.download(db, grabber, args.download)

    if args.search:
        Search.download(db, grabber, args.search, args.download)

    if args.follow:
        follows = args.follow
        while follows:
            subset = {}
            find(db, follows[0], args.re, subset)
            # continue follow calculation
            db = {}
            for p in subset.values():
                p.follow(db, args.download)
            follows = follows[1:] # continue with one element less

    if args.replay:
        Replay.download(db, grabber, args.download)

    if args.pluzz:
        Pluzz.download(db, grabber, args.download)

    if args.tf1:
        TF1.download(db, grabber, args.download)

    if args.m6:
        M6.download(db, grabber, args.download)

    if args.mediaset:
        Mediaset.download(db, grabber, args.download, "mediaset")

    if args.tg5:
        Mediaset.download(db, grabber, args.download, "tg5")

    if args.item:
        p = Item.Demand(grabber, args.item, args.download, len(db))
        db[p.pid] = p

    if args.m3u8:
        p = Playlist.process(grabber, args.m3u8, len(db))
        db[p.pid] = p

    if args.pid:
        subset = {}
        for pid in args.pid:
            find(db, pid, args.re, subset)
    else:
        subset = db

    if args.date:
        subset = filterByDate(subset, args.date)

    if args.channel:
        subset = filterByChannel(subset, args.channel)

    # we should only copy over
    # format, bwidth, overwrite, quiet
    options = args

    listDisplayOrGet(subset, args.nolist, args.info, args.get, options, grabberForDownload)
