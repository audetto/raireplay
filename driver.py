from asi import utils
from asi import info
from asi.services import demand, mediaset, raiplay, tf1, m6, programma, replay, playlist
from asi import config
from asi import console
from asi import tor

import os
import re
import datetime
import urllib
import logging
import enum


class Action(enum.Enum):
    INFO = 0
    GET = 1
    CAST = 2
    SHOW = 3

    @staticmethod
    def get_actions(args):
        actions = []
        if args.info:
            actions.append(Action.INFO)
        if args.get:
            actions.append(Action.GET)
        if args.cast:
            actions.append(Action.CAST)
        if args.show:
            actions.append(Action.SHOW)
        return actions


def item_do_actions(item, nolist, actions, options, grabber, fmt):
    if Action.INFO in actions:
        width = console.terminal_width()
        item.display(width)
    elif not nolist:
        # this is list
        print(item.short(fmt))

    if Action.CAST in actions:
        item.cast(options)

    if Action.SHOW in actions:
        item.show(options)

    if Action.GET in actions:
        try:
            item.download_video(config.program_folder, options, grabber)
        except Exception:
            logging.exception(f'GET: {item.short(fmt)}')


def list_do_actions(items, nolist, actions, options, grabber):
    numberOfItems = len(items)

    if nolist:
        print()
        print(f"INFO: {numberOfItems} programmes found")

    if (Action.CAST in actions) and (numberOfItems > 1):
        raise Exception(f"Cannot cast {numberOfItems} items")

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
        item_do_actions(p, nolist, actions, options, grabber, fmt)


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
                s = utils.remove_accents(s)
                if s.find(match) != -1:
                    subset[ppid] = p


def process(args):
    db = {}

    proxy = None

    if args.location:
        config.program_folder = config.create_folder(args.location)

    if args.here:
        config.program_folder = os.getcwd()

    if args.tor:
        tor.set_tor_exit_nodes(args.tor)

    if args.tor or args.tor_proxy:
        # we use privoxy to access tor
        proxy = { "http"  : "http://127.0.0.1:8118",
                  "https" : "http://127.0.0.1:8118" }
    elif args.proxy:
        proxy = { "http"  : args.proxy,
                  "https" : args.proxy }

    proxyHandler = urllib.request.ProxyHandler(proxy)

    grabber = urllib.request.build_opener(proxyHandler)
    # we still need to install the global one, as sometimes we cannot pass in a new one
    # (m3u8 and urlretrieve)
    urllib.request.install_opener(grabber)

    grabberForDownload = None
    if proxy and not args.proxy_all:
        # we do not want to use tor/proxy for the actual download
        # only for the metadata
        grabberForDownload = urllib.request.build_opener()
    else:
        # use the same opener everywhere
        grabberForDownload = grabber

    if args.tor_search and args.tor:
        width = console.terminal_width()
        info.search_tor(grabber, args.tor, args.tor_search)
        return

    if args.ip:
        width = console.terminal_width()
        info.display(grabber, width)
        return

    if args.ondemand:
        demand.download(db, grabber, args.download)

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
        replay.download(db, grabber, args.download)

    if args.raiplay:
        raiplay.download(db, grabber, args.download)

    if args.programma:
        programma.download(db, grabber, args.programma, args.download)

    if args.tf1:
        tf1.download(db, grabber, args.download)

    if args.m6:
        m6.download(db, grabber, args.download)

    if args.mediaset:
        mediaset.download(db, grabber, args.download, "mediaset")

    if args.tg5:
        mediaset.download(db, grabber, args.download, "tg5")

    if args.m3u8:
        p = playlist.process(grabber, args.m3u8, len(db))
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

    actions = Action.get_actions(args)

    list_do_actions(subset, args.nolist, actions, options, grabberForDownload)
