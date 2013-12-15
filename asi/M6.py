import os
import json
import datetime
import time

from xml.etree import ElementTree

from asi import Utils
from asi import Config
from asi import Base

# this comes from M6group.groovy
# https://bitbucket.org/Illico/serviio_plugins/wiki/M6group.groovy
# and maybe earlier frm XBMC
# http://mirrors.xbmc.org/addons/frodo/plugin.video.m6groupe/

# but it seems to be broken

# this plugin has been moved to use the iphone machinery

channels = ["m6", "w9", "6ter"]

def getTSUrl(link):
    ts = "https://lb.cdn.m6web.fr/s/su/s/m6replay_iphone/iphone/{0}".format(link)
    return ts


def getCatalogueUrl(channel):
    catalogueUrl = "http://static.m6replay.fr/catalog/m6group_web/{0}replay/catalogue.json"
    url = catalogueUrl.format(channel)
    return url


def getInfoUrl(channel, clip):
    infoUrl = "http://static.m6replay.fr/catalog/m6group_iphone/{0}replay/clip/{1}/clip_infos-{2}.xml"
    clip_key = clip[-2:] + '/' + clip[-4:-2]
    url = infoUrl.format(channel, clip_key, clip)
    return url


def process(grabber, downType, f, channel, db):
    o = json.load(f)

    clpList = o["clpList"]

    for k, v in clpList.items():
        if v["type"] == "vi":
            title = v["programName"] + " - " + v["clpName"]
            desc = v["desc"]
            date = v["antennaDate"]
            seconds = v["duration"]

            length = datetime.timedelta(seconds = int(seconds))

            pid = Utils.getNewPID(db, k)
            p = Program(grabber, downType, channel, date, pid, k, length, title, desc)
            Utils.addToDB(db, p)


def download(db, grabber, downType):
    progress = Utils.getProgress()

    for channel in channels:
        url = getCatalogueUrl(channel)
        name = Utils.httpFilename(url) + "." + channel

        folder = Config.m6Folder
        localName = os.path.join(folder, name)

        f = Utils.download(grabber, progress, url, localName, downType, "utf-8", True)
        if (f):
            process(grabber, downType, f, channel, db)


class Program(Base.Base):
    def __init__(self, grabber, downType, channel, date, pid, key, length, title, desc):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.key = key
        self.downType = downType
        self.url = getInfoUrl(self.channel, self.key);

        if date:
            self.datetime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        else:
            self.datetime =  datetime.datetime.now()

        self.grabber = grabber
        self.length = length

        name = Utils.makeFilename(self.title)
        self.filename = self.pid + "-" + name


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Channel:", self.channel)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Date:", Utils.strDate(self.datetime))
        print("Length:", self.length)
        print("Filename:", self.filename)
        print()
        print("URL:", self.url)

        super(Program, self).display(width)


    def getTabletPlaylist(self):
        if not self.ts:
            folder = Config.m6Folder
            name = Utils.httpFilename(self.url)
            localName = os.path.join(folder, name)
            progress = Utils.getProgress()

            f = Utils.download(self.grabber, progress, self.url, localName, self.downType, "utf-8", True)
            if (f):
                root = ElementTree.parse(f).getroot()
                asset = root.find("asset")
                for v in asset.findall("assetItem"):
                    if not self.ts:
                        u = v.find("url").text
                        self.ts = getTSUrl(u)

        return super(Program, self).getTabletPlaylist()
