import os
import datetime

from xml.etree import ElementTree

from asi import Utils
from asi import Config
from asi.services import Base

# this comes from M6group.groovy
# https://bitbucket.org/Illico/serviio_plugins/wiki/M6group.groovy
# and maybe earlier from XBMC
# http://mirrors.xbmc.org/addons/frodo/plugin.video.m6groupe/
# but it seems to be broken

# this plugin has been moved to use the iphone machinery
# which seems to work

channels = ["m6replay", "w9replay", "6terreplay", "styles", "stories", "comedy", "crazy_kitchen"]

def getTSUrl(link):
#    ts = "https://lb.cdn.m6web.fr/c/cu/s/m6replay_iphone/iphone/{0}".format(link)
    ts = "https://lb.cdn.m6web.fr/s/cu/prime/{0}".format(link)
    return ts


def getCatalogueUrl(channel):
# old catalogue
#    catalogueUrl = "http://static.m6replay.fr/catalog/m6group_web/{0}replay/catalogue.json"
# iphone catalogue
    catalogueUrl = "http://static.m6replay.fr/catalog/m6group_iphone/{0}/catalogue.xml"
    url = catalogueUrl.format(channel)
    return url


def getInfoUrl(channel, clip):
    infoUrl = "http://static.m6replay.fr/catalog/m6group_iphone/{0}/clip/{1}/clip_infos-{2}.xml"
    clip_key = clip[-2:] + '/' + clip[-4:-2]
    url = infoUrl.format(channel, clip_key, clip)
    return url


def process(grabber, downType, f, channel, db):
    root = ElementTree.parse(f).getroot()

    clpList = root.find("clpList")

    for clp in clpList:
        k = clp.get("id")
        title = clp.find("programName").text + " - " + clp.find("clpName").text
        desc = clp.find("desc").text
        date = clp.find("antennaDate").text
        if not date:
            date = clp.find("publiDate").text
        seconds = clp.find("duration").text

        length = datetime.timedelta(seconds = int(seconds))

        pid = Utils.get_new_pid(db, k)
        p = Program(grabber, downType, channel, date, pid, k, length, title, desc)
        Utils.add_to_db(db, p)


def download(db, grabber, downType):
    progress = Utils.get_progress()

    for channel in channels:
        url = getCatalogueUrl(channel)
        name = Utils.http_filename(url) + "." + channel

        folder = Config.m6_folder
        localName = os.path.join(folder, name)

        f = Utils.download(grabber, progress, url, localName, downType, "utf-8", True)
        if f:
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

        name = Utils.make_filename(self.title)
        self.filename = self.pid + "-" + name


    def display(self, width):
        super(Program, self).display(width)

        print("URL:", self.url)
        print()


    def getTS(self):
        if self.ts:
            return self.ts

        folder = Config.m6_folder
        name = Utils.http_filename(self.url)
        localName = os.path.join(folder, name)
        progress = Utils.get_progress()

        f = Utils.download(self.grabber, progress, self.url, localName, self.downType, "utf-8", True)
        if f:
            root = ElementTree.parse(f).getroot()
            asset = root.find("asset")
            for v in asset.findall("assetItem"):
                u = v.find("url").text
                self.ts = getTSUrl(u)
                return self.ts
