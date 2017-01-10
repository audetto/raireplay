import os
import urllib.parse
import datetime
import json
import re

from asi import Utils
from asi import Config
from asi import Base
from asi import RAIUrls

channels = ["Rai1", "Rai3", "Rai4", "Rai5", "RaiGulp", "RaiPremium", "RaiYoyo", "RaiSport1", "RaiSport2", "RaiMovie", "RaiStoria", "RaiScuola"]

def parseItem(grabber, downType, channel, value, db):
    name = value["name"]
    desc = value["description"]
    secs = value["duration"]

    date = value["datePublished"]
    time = value["timePublished"]

    length = secs

    pathID = value["pathID"]

    pid = Utils.getNewPID(db, None)
    p = Program(grabber, downType, channel, date, time, pid, length, name, desc, pathID)
    Utils.addToDB(db, p)


def process(grabber, downType, f, db):
    o = json.load(f)

    for k1, v1 in o.items():
        channel = k1
        for v2 in v1:
            date = v2['palinsesto'][0]['giorno']
            programmi = v2['palinsesto'][0]['programmi']
            for p in programmi:
                if p:
                    parseItem(grabber, downType, channel, p, db)


def download(db, grabber, downType):
    progress = Utils.getProgress()

    folder = Config.raiplayFolder

    for channel in channels:
        filename = "canale=" + channel
        url = RAIUrls.raiplay + filename
        localName = os.path.join(folder, filename + ".json")
        f = Utils.download(grabber, progress, url, localName, downType, "utf-8")

        if f:
            process(grabber, downType, f, db)


class Program(Base.Base):
    def __init__(self, grabber, downType, channel, date, hour, pid, length, title, desc, pathID):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.downType = downType

        self.url = RAIUrls.base + pathID

        self.datetime = datetime.datetime.strptime(date + " " + hour, "%d/%m/%Y %H:%M")

        self.grabber = grabber
        self.length = length

        name = Utils.makeFilename(self.title)
        self.filename = self.pid + "-" + name

    def getTS(self):
        if self.ts:
            return self.ts

        folder = Config.raiplayFolder
        name = Utils.httpFilename(self.url)
        localName = os.path.join(folder, name)
        progress = Utils.getProgress()

        f = Utils.download(self.grabber, progress, self.url, localName, self.downType, "utf-8", True)

        if f:
            o = json.load(f)
            url = o['video']['contentUrl']
            if url:
                self.ts = url
                return self.ts
