from __future__ import print_function

import json
import os.path

from asi import Utils
from asi import Config
from asi import Page
from asi import Base

url = "http://www.rai.tv/dl/RaiTV/programmi/ricerca/ContentSet-6445de64-d321-476c-a890-ae4ed32c729e-darivedere.html"
baseUrl = "http://www.rai.tv"

def process(grabber, f, db):
    o = json.load(f)

    pid = 0

    for v in o:
        p = Group(grabber, pid, v["title"], v["linkDemand"], v["date"], v["editore"])
        db[str(pid)] = p
        pid = pid + 1


def download(db, grabber, downType):
    page = Utils.httpFilename(url)

    folder = Config.demandFolder
    localFilename = os.path.join(folder, page)

    progress = Utils.getProgress()

    f = Utils.download(grabber, progress, url, localFilename, downType, "raw-unicode-escape", True)

    process(grabber, f, db)


class Group(Base.Base):
    def __init__(self, grabber, pid, title, link, date, channel):
        super(Group, self).__init__()

        self.pid = pid
        self.grabber = grabber
        self.title = title
        self.somedate = float(date)
        self.channel = channel

        self.url = baseUrl + link


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Title:", self.title)
        print("Channel:", self.channel)
        print("URL:", self.url)

        print()


    def follow(self, db, downType):
        Page.download(db, self.grabber, self.url, downType)
