import os
import urllib.parse
import json

from asi import Utils
from asi import Config
from asi import Base
from asi import RAIUrls
from asi import RaiPlay


def processSet(grabber, downType, f, db):
    o = json.load(f)

    channel = o["Name"]
    items = o["items"]

    for value in items:
        name = value["name"]
        desc = ""
        secs = value["duration"]

        date = value["datePublished"]
        time = value["timePublished"]

        length = secs

        pathID = value["pathID"]

        pid = Utils.getNewPID(db, None)
        p = RaiPlay.Program(grabber, downType, channel, date, time, pid, length, name, desc, pathID)
        Utils.addToDB(db, p)


def process(grabber, progress, folder, downType, f, db):
    o = json.load(f)

    blocks = o["Blocks"]

    for v1 in blocks:
        if "Sets" in v1:
            for v2 in v1["Sets"]:
                path = v2["url"]
                url = "http://www.raiplay.it/" + path

                filename = path.replace("/", "_")
                localName = os.path.join(folder, filename + ".json")

                f = Utils.download(grabber, progress, url, localName, downType, "utf-8", True)
                processSet(grabber, downType, f, db)


def download(db, grabber, programma, downType):
    progress = Utils.getProgress()

    folder = Config.raiplayFolder

    o = urllib.parse.urlparse(programma)
    filename = o.path.replace("/", "_")
    url = programma + "/?json"
    localName = os.path.join(folder, filename + ".json")

    f = Utils.download(grabber, progress, url, localName, downType, "utf-8", True)
    process(grabber, progress, folder, downType, f, db)
