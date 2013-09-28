

import os
import datetime
import json

from asi import Item
from asi import Utils
from asi import Config
from asi import Base
from asi import RAIUrls

# try to guess a date from a description like
# "TG2 ore 23:30 del 14/01/2013"
def isThereADate(oldDate, description):
    try:
        delGiorno = description[-14:]
        if delGiorno.find("del ") != 0:
            return oldDate
        possibleDate = delGiorno[4:].replace("-", "/")
        newDate = datetime.datetime.strptime(possibleDate, "%d/%m/%Y")
        strDate = newDate.strftime("%d/%m/%Y")
        return strDate
    except ValueError:
        return oldDate


def processSet(grabber, title, time, f, db):
    o = json.load(f)

    prog = o.get("integrale")
    if prog:
        link          = prog["weblink"]
        h264          = prog["h264"]
        m3u8          = prog["m3u8"]
        if time == "LIS":
            # strange time for some TG3
            time = "00:00"

        description   = prog["name"]
        date          = prog["date"]

        # the filed "date" seems to be always TODAY
        # so we might actually get a program from yesterday
        date          = isThereADate(date, description)
        datetime      = date + " " + time

        pid = Utils.getNewPID(db, None)
        p = Program(grabber, link, title, datetime, pid, title, description, h264, m3u8)
        Utils.addToDB(db, p)
    else:
        # get the list
        lst = o.get("list")

        if not lst:
            return

        for prg in lst:
            tp = prg["type"]
            if tp != "empty":
                link          = prg["weblink"]
                h264          = prg["h264"]
                m3u8          = prg["m3u8"]
                dt            = prg["date"] + " 00:00"
                aTitle        = title + "-" + prg["name"]
                description   = prg["desc"]

                pid = Utils.getNewPID(db, None)
                p = Program(grabber, link, title, dt, pid, aTitle, description, h264, m3u8)
                Utils.addToDB(db, p)


def processItem(grabber, progress, downType, title, time, url, db):
    folder = Config.tgFolder

    name = Utils.httpFilename(url)
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress, url, localName, downType, "utf-8", True)

    if f:
        processSet(grabber, title, time, f, db)


def processGroup(grabber, progress, downType, prog, db):
    name = prog["title"]

    edizioni = prog.get("edizioni")
    dettaglio = prog.get("dettaglio")
    if edizioni:
        for time, url in edizioni.items():
            title = name + " " + time
            processItem(grabber, progress, downType, title, time, url, db)
    elif dettaglio.find("ContentSet") >= 0:
        processItem(grabber, progress, downType, name, None, dettaglio, db)


def process(grabber, progress, downType, f, db):
    o = json.load(f)

    programmes = o["list"]

    for prog in programmes:
        processGroup(grabber, progress, downType, prog, db)


def download(db, grabber, downType):
    progress = Utils.getProgress()
    name = Utils.httpFilename(RAIUrls.info)

    folder = Config.tgFolder
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress, RAIUrls.info, localName, downType, "utf-8", True)
    process(grabber, progress, downType, f, db)


class Program(Base.Base):
    def __init__(self, grabber, link, channel, date, pid, title, desc, h264, m3u8):
        super(Program, self).__init__()

        self.link = link
        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        strtime = date.replace("-", "/")
        self.datetime = datetime.datetime.strptime(strtime, "%d/%m/%Y %H:%M")
        if h264:
            self.h264[0] = h264
        if m3u8:
            self.ts = m3u8

        self.grabber = grabber

        name = Utils.makeFilename(self.title)
        self.filename = name + "-" + self.datetime.strftime("%Y-%m-%d")


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Channel:", self.channel)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Date:", Utils.strDate(self.datetime))
        print("Filename:", self.filename)
        print("Link:", self.link)
        print()
        Utils.displayH264(self.h264)
        print("m3u8:", self.ts)
        print()

        m3 = self.getTabletPlaylist()
        Utils.displayM3U8(m3)


    def follow(self, db, downType):
        pid = Utils.getNewPID(db, self.pid)
        p = Item.Demand(self.grabber, self.link, downType, pid)
        Utils.addToDB(db, p)
