import os
import urllib.parse
import datetime
import json
import re

from asi import Utils
from asi import Config
from asi import Base
from asi import RAIUrls
import logging

channels = ["Rai1", "Rai2", "Rai3", "Rai4", "Rai5", "RaiGulp", "RaiPremium", "RaiYoyo", "RaiSport1", "RaiSport2", "RaiMovie", "RaiStoria", "RaiScuola"]

def parseItem(grabber, downType, channel, value, db, dup):
    if value and "hasVideo" in value and value["hasVideo"]:

        id = value["ID"]

        if not id in dup:

            dup.add(id)

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


def process(grabber, downType, f, db, dup):
    s = f.read()
    s = s.replace('[an error occurred while processing this directive]', '')
    o = json.loads(s)

    for k1, v1 in o.items():
        channel = k1
        for v2 in v1:
            palinsesto = v2['palinsesto']
            if palinsesto:
                programmi = palinsesto[0]['programmi']
                for p in programmi:
                    parseItem(grabber, downType, channel, p, db, dup)


def download(db, grabber, downType):
    progress = Utils.getProgress()

    folder = Config.raiplayFolder

    dup = set()

    for channel in channels:
        filename = "canale=" + channel
        url = RAIUrls.raiplay + filename
        localName = os.path.join(folder, filename + ".json")
        try:
            f = Utils.download(grabber, progress, url, localName, downType, "utf-8", True)

            if f:
                process(grabber, downType, f, db, dup)
        except json.decoder.JSONDecodeError as e:
            logging.info('While precessing channel: {0}'.format(channel))
            logging.info('Exception: {0}'.format(e))


class Program(Base.Base):
    def __init__(self, grabber, downType, channel, date, hour, pid, length, title, desc, pathID):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.downType = downType

        self.url = RAIUrls.base + pathID

        if date and hour:
            self.datetime = datetime.datetime.strptime(date + " " + hour, "%d/%m/%Y %H:%M")
        else:
            self.datetime = datetime.datetime.now()

        self.grabber = grabber
        self.length = length

        name = Utils.makeFilename(self.title)
        self.filename = name


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
