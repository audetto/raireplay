import os
import urllib.parse
import datetime
import json
import re

from asi import Utils
from asi import Config
from asi import Base
from asi import RAIUrls

channels = {"1": "RaiUno", "2": "RaiDue", "3": "RaiTre", "23": "RaiGulp", "31": "RaiCinque", "32": "RaiPremium", "38": "RaiYoyo"}

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


class Program(Base.Base):
    def __init__(self, grabber, channel, date, hour, pid, length, title, desc, h264, tablet, smartPhone):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.h264 = h264
        self.description = desc
        self.channel = channel

        if tablet:    # higher quality normally
            self.ts = tablet
        else:
            self.ts = smartPhone

        self.datetime = datetime.datetime.strptime(date + " " + hour, "%Y-%m-%d %H:%M")

        self.grabber = grabber
        self.length = length

        name = Utils.makeFilename(self.title)
        self.filename = self.pid + "-" + name
