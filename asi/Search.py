import datetime
import os.path
import json

from asi import Utils
from asi import Config
from asi import Item
from asi import Base
from asi import RAIUrls

def process(grabber, f, db):
    o = json.load(f)

    for prog in o["list"]:
        link          = prog["weblink"]
        h264          = prog["h264"]
        m3u8          = prog["m3u8"]
        wmv           = prog["wmv"]
        title         = prog["name"]
        date          = prog["date"]
        description   = prog["desc"]

        pid = Utils.getNewPID(db, None)
        p = Program(grabber, link, title, date, pid, title, description, h264, m3u8, wmv)
        Utils.addToDB(db, p)


class Program(Base.Base):
    def __init__(self, grabber, link, channel, date, pid, title, desc, h264, m3u8, wmv):
        super(Program, self).__init__()

        self.link = link
        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel

        if date:
            self.datetime = datetime.datetime.strptime(date, "%d/%m/%Y")
        else:
            self.datetime = datetime.datetime.now()

        if h264:
            self.h264 = h264

        if m3u8:
            self.ts = m3u8

        if wmv:
            self.mms = wmv

        self.grabber = grabber

        self.filename = Utils.makeFilename(self.title)


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
        print("h264:", self.h264)
        print("m3u8:", self.ts)
        print("mms:", self.mms)

        m3 = self.getTabletPlaylist()
        Utils.displayM3U8(self.m3)


    def follow(self, db, downType):
        pid = Utils.getNewPID(db, self.pid)
        p = Item.Demand(self.grabber, self.link, downType, self.pid)
        Utils.addToDB(db, p)


def download(db, grabber, term, downType):
    dataUrl = RAIUrls.getSearchUrl(term, 100)

    folder = Config.searchFolder
    localFilename = os.path.join(folder, term + ".json")
    f = Utils.download(grabber, None, dataUrl, localFilename, downType, "utf-8")

    process(grabber, f, db)
