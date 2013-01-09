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

programsUrl = "http://api.tf1.fr/tf1-programs/iphone/limit/100/"
newsUrl = "http://api.tf1.fr/tf1-homepage-news/iphone/"
homepageUrl = "http://api.tf1.fr/tf1-homepage/iphone/"

def getDataUrl(progId, item):
    url = "http://api.tf1.fr/tf1-vods/iphone//integral/{0}/program_id/{1}".format(item, progId)
    return url


def getWatLink(watId):
    url = "http://www.wat.tv//get/iphone/{0}.m3u8?bwmin=100000&bwmax=490000".format(watId)
    return url


def parseItem(grabber, prog, name):
    pid      = str(prog["id"])
    desc     = prog["longTitle"]
    date     = prog["publicationDate"]
    duration = prog["duration"]
    channel  = "tf1"
    name     = name + " - " + prog["shortTitle"]
    wat      = prog["watId"]

    minutes = duration / 60

    p = Program(grabber, channel, date, minutes, pid, name, desc, wat)

    return p


def processId(grabber, f, name, db):
    o = json.load(f)

    for prog in o:
        p = parseItem(grabber, prog, name)
        db[p.pid] = p


def process(grabber, f, folder, progress, downType, db):
    o = json.load(f)

    for prog in o:
        name = prog["programName"]
        progId = prog["programId"]

        url_0 = getDataUrl(progId, 0)
        localName_0 = os.path.join(folder, str(progId) + ".0.json")
        f_0 = Utils.download(grabber, progress, url_0, localName_0, downType, "utf-8", True)
        processId(grabber, f_0, name, db)

        url_1 = getDataUrl(progId, 1)
        localName_1 = os.path.join(folder, str(progId) + ".1.json")
        f_1 = Utils.download(grabber, progress, url_1, localName_1, downType, "utf-8", True)
        processId(grabber, f_1, name, db)


def download(db, grabber, downType):
    progress_obj = urlgrabber.progress.TextMeter()

    folder = Config.tf1Folder
    localName = os.path.join(folder, "news.json")
    f = Utils.download(grabber, progress_obj, newsUrl, localName, downType, "utf-8", True)

    process(grabber, f, folder, progress_obj, downType, db)


class Program(Base.Base):
    def __init__(self, grabber, channel, date, minutes, pid, title, desc, wat):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.wat = wat
        self.datetime = time.strptime(date, "%Y-%m-%d %H:%M:%S")

        self.minutes = minutes
        self.grabber = grabber
        self.ts = getWatLink(self.wat)

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
        print("Length:", self.minutes, "minutes")
        print("Filename:", self.filename)
        print()
        print("url:", self.ts)

        m3 = self.getTabletPlaylist()

        if m3 != None and m3.is_variant:
            print()
            for playlist in m3.playlists:
                format = "\tProgram: {0:>2}, Bandwidth: {1:>10}, Codecs: {2}"
                line = format.format(playlist.stream_info.program_id, playlist.stream_info.bandwidth, playlist.stream_info.codecs)
                print(line)
            print()
