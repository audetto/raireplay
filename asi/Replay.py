from __future__ import print_function

import os
import urlparse
import datetime
import json

from asi import Utils
from asi import Config
from asi import Base

baseUrl = "http://www.rai.it/dl/portale/html/palinsesti/replaytv/static"
channels = {"1": "RaiUno", "2": "RaiDue", "3": "RaiTre", "31": "RaiCinque"}

# tablet and phone url contain an overlapping set of bitrates
# this function makes the union of the 2
def getFullUrl(tablet, phone):
    if tablet == "":
        return phone

    if phone == "":
        return tablet

    posOfFirstCommaT = tablet.find(",")
    posOfLastCommaT  = tablet.rfind(",")
    midTablet = tablet[posOfFirstCommaT + 1 : posOfLastCommaT]

    posOfFirstCommaP = phone.find(",")
    posOfLastCommaP  = phone.rfind(",")
    midPhone = phone[posOfFirstCommaP + 1 : posOfLastCommaP]

    tabletSizes = midTablet.split(",")
    phoneSizes  = midPhone.split(",")

    sizes = set()
    sizes.update(tabletSizes)
    sizes.update(phoneSizes)

    fullUrl = tablet[0 : posOfFirstCommaT]
    for s in sorted(sizes, key = int):
        fullUrl = fullUrl + "," + s
    fullUrl = fullUrl + tablet[posOfLastCommaT :]

    return fullUrl


def parseItem(grabber, channel, date, time, value):
    name = value["t"]
    desc = value["d"]
    secs = value["l"]

    minutes = 0
    if secs != "":
        minutes = int(secs) / 60

    h264 = value["h264"]
    tablet = value["urlTablet"]
    smartPhone = value["urlSmartPhone"]
    pid = value["i"]

    if h264 != "" or tablet != "" or smartPhone != "" :
        p = Program(grabber, channels[channel], date, time, pid, minutes, name, desc, h264, tablet, smartPhone)
        return p

    return None


def process(grabber, f, db):
    o = json.load(f)

    for k1, v1 in o.iteritems():
        if k1 == "now":
            continue
        if k1 == "defaultBannerVars":
            continue

        channel = k1

        for date, v2 in v1.iteritems():
            for time, value in v2.iteritems():
                p = parseItem(grabber, channel, date, time, value)

                Utils.addToDB(db, p)


def download(db, grabber, downType):
    progress = Utils.getProgress()

    today = datetime.date.today()

    folder = Config.replayFolder

    for x in range(1, 8):
        day = today - datetime.timedelta(days = x)
        strDate = day.strftime("_%Y_%m_%d")

        for channel in channels.itervalues():
            filename = channel + strDate + ".html"
            url = baseUrl + "/" + filename
            localName = os.path.join(folder, filename)

            f = Utils.download(grabber, progress, url, localName, downType, "utf-8")
            process(grabber, f, db)

    print()


class Program(Base.Base):
    def __init__(self, grabber, channel, date, hour, pid, minutes, title, desc, h264, tablet, smartPhone):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.h264 = h264
        self.description = desc
        self.channel = channel
        self.ts = getFullUrl(tablet, smartPhone)
        self.datetime = datetime.datetime.strptime(date + " " + hour, "%Y-%m-%d %H:%M")

        self.grabber = grabber
        self.minutes = minutes

        self.filename = self.getFilename()

    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Channel:", self.channel)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Date:", self.datetime.strftime("%Y-%m-%d %H:%M"))
        print("Length:", self.minutes, "minutes")
        print("Filename:", self.filename)
        print()
        print("h264:", self.h264)
        print("ts:  ", self.ts)

        m3 = self.getTabletPlaylist()
        Utils.displayM3U8(self.m3)


    # use RAI m3u8 url to get a "nice" filename
    # as opposed to only use the pid
    def getFilename(self):
        if self.ts == "":
            return self.pid

        fullName = os.path.split(os.path.split(urlparse.urlsplit(self.ts).path)[0])[1]
        tmp = fullName.split(",")[0]
        posOfDash = tmp.rfind("-")
        nice = tmp[0 : posOfDash]

        filename = self.pid + "-" + nice

        return filename
