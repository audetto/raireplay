from __future__ import print_function

import os
import time
import json

from datetime import date
from datetime import timedelta

import urlgrabber.progress

from asi import Meter
from asi import Utils
from asi import Config
from asi import Base

infoUrl = "http://www.rai.tv/dl/RaiTV/iphone/assets/tg_json.js?NS=0-1-4c61b46e9a4ab09b25da2246ae52d31edb528475-5.1.1"

def processSet(grabber, title, f, db):
    o = json.load(f)

    prog = o.get("integrale")
    if prog != None:
        contentItem   = prog["weblink"]
        h264          = prog["h264"]
        m3u8          = prog["m3u8"]
        date          = prog["date"]
        description   = prog["name"]

        pid = str(len(db))
        p = Program(grabber, "channel", date, pid, title, description, h264, m3u8)
        db[p.pid] = p
    else:
        # get the list
        lst = o["list"]

        for prg in lst:
            tp            = prg["type"]
            if tp != "empty":
                contentItem   = prg["weblink"]
                h264          = prg["h264"]
                m3u8          = prg["m3u8"]
                date          = prg["date"]
                title         = prg["name"]
                description   = prg["desc"]

                pid = str(len(db))
                p = Program(grabber, "channel", date, pid, title, description, h264, m3u8)
                db[p.pid] = p


def processSetIntegrale(grabber, title, f, db):
    o = json.load(f)

    prog          = o["integrale"]
    contentItem   = prog["weblink"]
    h264          = prog["h264"]
    m3u8          = prog["m3u8"]
    date          = prog["date"]
    description   = prog["name"]

    pid = str(len(db))
    p = Program(grabber, "channel", date, pid, title, description, h264, m3u8)
    db[p.pid] = p


def processItem(grabber, progress_obj, downType, title, url, db):
    folder = Config.tgFolder

    name = Utils.httpFilename(url)
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress_obj, url, localName, downType, "utf-8", True)
    processSet(grabber, title, f, db)


def processGroup(grabber, progress_obj, downType, prog, db):
    name = prog["title"]

    edizioni = prog.get("edizioni")
    dettaglio = prog.get("dettaglio")
    if edizioni != None:
        for time, url in edizioni.iteritems():
            title = name + " " + time
            processItem(grabber, progress_obj, downType, title, url, db)
    elif dettaglio.find("ContentSet") >= 0:
        processItem(grabber, progress_obj, downType, None, dettaglio, db)


def process(grabber, progress_obj, downType, f, db):
    o = json.load(f)

    programmes = o["list"]

    for prog in programmes:
        processGroup(grabber, progress_obj, downType, prog, db)


def download(db, grabber, downType):
    progress_obj = urlgrabber.progress.TextMeter()
    name = Utils.httpFilename(infoUrl)

    folder = Config.tgFolder
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress_obj, infoUrl, localName, downType, "utf-8", True)
    process(grabber, progress_obj, downType, f, db)


class Program(Base.Base):
    def __init__(self, grabber, channel, date, pid, title, desc, h264, m3u8):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        strtime = date.replace("-", "/")
        self.datetime = time.strptime(strtime, "%d/%m/%Y")
        if h264:
            self.h264 = h264
        if m3u8:
            self.ts = m3u8

        self.grabber = grabber

        self.m3 = None
        name = Utils.makeFilename(self.title)
        self.filename = self.pid + "-" + name


    def getTabletPlaylist(self):
        if self.m3 == None:
            self.m3 = Utils.load_m3u8_from_url(self.grabber, self.ts)

        return self.m3


    def display(self):
        width = urlgrabber.progress.terminal_width()

        print("=" * width)
        print("PID:", self.pid)
        print("Channel:", self.channel)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Date:", time.strftime("%Y-%m-%d %H:%M", self.datetime))
        print("Filename:", self.filename)
        print()
        print("h264:", self.h264)
        print("m3u8:", self.ts)

        m3 = self.getTabletPlaylist()

        if m3 != None and m3.is_variant:
            print()
            for playlist in m3.playlists:
                format = "\tProgram: {0:>2}, Bandwidth: {1:>10}, Codecs: {2}"
                line = format.format(playlist.stream_info.program_id, playlist.stream_info.bandwidth, playlist.stream_info.codecs)
                print(line)
            print()
