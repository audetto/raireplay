import os
import json
import datetime
import time
import hashlib

from asi import Utils
from asi import Config
from asi import Base

# this comes from M6group.groovy
# https://bitbucket.org/Illico/serviio_plugins/wiki/M6group.groovy
# and maybe earlier frm XBMC
# http://mirrors.xbmc.org/addons/frodo/plugin.video.m6groupe/

# but it seems to be broken

channels = ["m6", "w9", "6ter"]

def getCatalogueUrl(channel):
    catalogueUrl = "http://static.m6replay.fr/catalog/m6group_web/{0}replay/catalogue.json"
    url = catalogueUrl.format(channel)
    return url


def getInfoUrl(channel, clip):
    infoUrl = "http://static.m6replay.fr/catalog/m6group_web/{0}replay/clip/{1}/clip_infos-{2}.json"
    clip_key = clip[-2:] + '/' + clip[-4:-2]
    url = infoUrl.format(channel, clip_key, clip)
    return url


def getLink(url):
    if url.startswith("mp4:"):
        return url
    if url.endswith(".f4m"):
        name = url.split("/")[-1].replace(".f4m", ".mp4")
        link = "mp4:production/regienum/" + name
        return link


def MD5Hash(s):
    md5 = hashlib.md5()
    md5.update(s.encode("ascii"))
    md5hash = md5.hexdigest()
    return md5hash


def encodePlayPath(app, playPath, timestamp):
    delay = 86400
    secretKey = "vw8kuo85j2xMc"
    url = "{0}?s={1}&e={2}".format(playPath, timestamp, timestamp + delay)
    urlHash = MD5Hash(secretKey + "/" + app + "/" + url[4:])
    tokenUrl = url + "&h=" + urlHash
    return tokenUrl


def getRTMPUrl(palyPath):
    rtmp = "rtmpe://groupemsix.fcod.llnwd.net"
    app = "a2883/e1"
    swfUrl = "http://www.6play.fr/rel-3/M6ReplayV3Application-3.swf"
    timestamp = int(time.time())
    tokenUrl = encodePlayPath(app, palyPath, timestamp)
    rtmpUrl = 'rtmpdump -r "' + rtmp + "/" + app + "/" + tokenUrl + '" --swfVfy ' + swfUrl + " -m 10"
    return rtmpUrl


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

            url = None

            pid = Utils.getNewPID(db, k)
            p = Program(grabber, downType, channel, date, pid, k, length, title, desc, url)
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
    def __init__(self, grabber, downType, channel, date, pid, key, length, title, desc, url):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.key = key
        self.downType = downType
        self.rtmp = {}

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

        self.getRTMP()
        for k, v in self.rtmp.items():
            print("RTMP[{0}]: {1}".format(k, v))
        print()

        super(Program, self).display(width)


    def getRTMP(self):
        if self.rtmp:
            return

        url = getInfoUrl(self.channel, self.key);
        folder = Config.m6Folder
        name = Utils.httpFilename(url)
        localName = os.path.join(folder, name)
        progress = Utils.getProgress()

        f = Utils.download(self.grabber, progress, url, localName, self.downType, "utf-8", True)
        if (f):
            o = json.load(f)
            asset = o["asset"]
            for k, v in asset.items():
                u = v["url"]
                if u:
                    link = getLink(u)
                    if link:
                        rtmpUrl = getRTMPUrl(link)
                        quality = v["quality"]
                        self.rtmp[quality] = rtmpUrl
