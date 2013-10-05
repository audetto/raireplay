

import os
import urllib.parse
import datetime
import json
import re

from asi import Utils
from asi import Config
from asi import Base
from asi import RAIUrls

channels = {"1": "RaiUno", "2": "RaiDue", "3": "RaiTre", "31": "RaiCinque", "32": "RaiPremium"}

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


# we want to extract all the
# h264_DIGIT
# which are now used for bwidth selection for MP4

def extractH264Ext(value):
    res = {}
    reg = "^h264_(\d+)"
    for k in value:
        m = re.match(reg, k)
        url = value[k]
        if m and url:
            bwidth = int(m.group(1))
            Utils.addH264Url(res, bwidth, url)

    return res


def parseItem(grabber, channel, date, time, value, db):
    name = value["t"]
    desc = value["d"]
    secs = value["l"]

    length = None

    if secs != "":
        length = datetime.timedelta(seconds = int(secs))

    h264 = extractH264Ext(value)

    # if the detailed h264 is not found, try with "h264"
    if not h264:
        single = value["h264"]
        Utils.addH264Url(h264, 0, single)

    tablet = value["urlTablet"]
    smartPhone = value["urlSmartPhone"]
    pid = value["i"]

    if h264 or tablet or smartPhone:
        pid = Utils.getNewPID(db, pid)
        p = Program(grabber, channels[channel], date, time, pid, length, name, desc, h264, tablet, smartPhone)
        Utils.addToDB(db, p)


def process(grabber, f, db):
    o = json.load(f)

    for k1, v1 in o.items():
        if k1 == "now":
            continue
        if k1 == "defaultBannerVars":
            continue

        channel = k1

        for date, v2 in v1.items():
            for time, value in v2.items():
                parseItem(grabber, channel, date, time, value, db)


def download(db, grabber, downType):
    progress = Utils.getProgress()

    today = datetime.date.today()

    folder = Config.replayFolder

    for x in range(1, 8):
        day = today - datetime.timedelta(days = x)
        strDate = day.strftime("_%Y_%m_%d")

        for channel in channels.values():
            filename = channel + strDate + ".html"
            url = RAIUrls.replay + "/" + filename
            localName = os.path.join(folder, filename)

            f = Utils.download(grabber, progress, url, localName, downType, "utf-8")

            if f:
                process(grabber, f, db)

    print()


class Program(Base.Base):
    def __init__(self, grabber, channel, date, hour, pid, length, title, desc, h264, tablet, smartPhone):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.h264 = h264
        self.description = desc
        self.channel = channel
        self.ts = getFullUrl(tablet, smartPhone)
        self.datetime = datetime.datetime.strptime(date + " " + hour, "%Y-%m-%d %H:%M")

        self.grabber = grabber
        self.length = length

        self.filename = self.getFilename()

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
        Utils.displayH264(self.h264)
        print("ts:  ", self.ts)
        print()

        m3 = self.getTabletPlaylist()
        Utils.displayM3U8(m3)


    # use RAI m3u8 url to get a "nice" filename
    # as opposed to only use the pid
    def getFilename(self):
        if self.ts == "":
            return self.pid

        fullName = os.path.split(os.path.split(urllib.parse.urlsplit(self.ts).path)[0])[1]
        tmp = fullName.split(",")[0]
        posOfDash = tmp.rfind("-")
        nice = tmp[0 : posOfDash]

        filename = self.pid + "-" + nice

        return filename
