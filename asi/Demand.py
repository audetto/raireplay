import json
import os.path
import datetime

from asi import Utils
from asi import Config
from asi import Page
from asi import Base
from asi import RAIUrls


def process(grabber, f, db):
    o = json.load(f)

    for v in o:
        pid = Utils.getNewPID(db, None)
        p = Group(grabber, pid, v["title"], v["linkDemand"], v["date"], v["editore"])
        Utils.addToDB(db, p)


def download(db, grabber, downType):
    page = Utils.httpFilename(RAIUrls.onDemand)

    folder = Config.demandFolder
    localFilename = os.path.join(folder, page)

    progress = Utils.getProgress()

    f = Utils.download(grabber, progress, RAIUrls.onDemand, localFilename, downType, "raw-unicode-escape", True)

    process(grabber, f, db)


class Group(Base.Base):
    def __init__(self, grabber, pid, title, link, date, channel):
        super(Group, self).__init__()

        self.pid = pid
        self.grabber = grabber
        self.title = title
        self.datetime = datetime.datetime.fromtimestamp(int(date) / 1000)
        self.channel = channel

        self.url = RAIUrls.base + link


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Title:", self.title)
        print("Channel:", self.channel)
        print("Follow: ENABLED")
        print()
        print("URL:", self.url)
        print()


    def follow(self, db, downType):
        Page.download(db, self.grabber, self.url, downType)
