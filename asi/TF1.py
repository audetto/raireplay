from __future__ import print_function

import os
import datetime
import json

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
    pubDate  = prog["publicationDate"]
    duration = prog["duration"]
    name     = name + " - " + prog["shortTitle"]
    wat      = prog["watId"]
    category = prog["videoCategory"]

    minutes  = duration / 60
    date = datetime.datetime.strptime(pubDate, "%Y-%m-%d %H:%M:%S")

    p = Program(grabber, date, minutes, pid, name, desc, wat, category)

    return p


def processGroup(grabber, f, name, db):
    o = json.load(f)

    for prog in o:
        p = parseItem(grabber, prog, name)

        # ignore the countless "extract", "bonus", "short" which last just a few minutes
        if p.category == "fullvideo":
            Utils.addToDB(db, p)


def processNews(grabber, f, folder, progress, downType, db):
    o = json.load(f)

    for prog in o:
        name = prog["programName"]
        groupId = prog["programId"]

        downloadGroup(grabber, name, groupId, folder, progress, downType, db)

        # this group contains the info of the most recent Item
        # we add an other item with the group name
        # some info will still be missing

        title = prog["title"]
        wat = prog["linkAttributes"]["watId"]
        category = prog["linkAttributes"]["videoCategory"]

        p = Program(grabber, datetime.datetime.now(), None, str(groupId), name, title, wat, category)
        Utils.addToDB(db, p)


def processPrograms(grabber, f, folder, progress, downType, db):
    o = json.load(f)

    for prog in o:
        name = prog["shortTitle"]
        groupId = prog["id"]

        # here, we do not know the most recent item
        # we simply have to go through them all

        downloadGroup(grabber, name, groupId, folder, progress, downType, db)


def downloadGroup(grabber, name, groupId, folder, progress, downType, db):

    # we set it to True as this is a group
    # and subject to continuous changes
    checkTimestamp = True

    url_0 = getDataUrl(groupId, 0)
    localName_0 = os.path.join(folder, str(groupId) + ".0.json")
    f_0 = Utils.download(grabber, progress, url_0, localName_0, downType, "utf-8", checkTimestamp)
    processGroup(grabber, f_0, name, db)

    url_1 = getDataUrl(groupId, 1)
    localName_1 = os.path.join(folder, str(groupId) + ".1.json")
    f_1 = Utils.download(grabber, progress, url_1, localName_1, downType, "utf-8", checkTimestamp)
    processGroup(grabber, f_1, name, db)


def download(db, grabber, downType):
    progress = Utils.getProgress()

    folder = Config.tf1Folder

    localName = os.path.join(folder, "news.json")
    f = Utils.download(grabber, progress, newsUrl, localName, downType, "utf-8", True)

    processNews(grabber, f, folder, progress, downType, db)

    localName = os.path.join(folder, "programs.json")
    f = Utils.download(grabber, progress, programsUrl, localName, downType, "utf-8", True)

    processPrograms(grabber, f, folder, progress, downType, db)


class Program(Base.Base):
    def __init__(self, grabber, datetime, minutes, pid, title, desc, wat, category):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = "tf1"
        self.wat = wat
        self.datetime = datetime
        self.category = category

        self.minutes = minutes
        self.grabber = grabber
        self.ts = getWatLink(self.wat)

        name = Utils.makeFilename(self.title)
        self.filename = self.pid + "-" + name


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Channel:", self.channel)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Date:", self.datetime.strftime("%Y-%m-%d %H:%M"))
        print("Length:", self.minutes, "minutes")
        print("Filename:", self.filename)
        print("Category:", self.category)
        print()
        print("url:", self.ts)

        m3 = self.getTabletPlaylist()
        Utils.displayM3U8(self.m3)
