import os
import datetime
import json
import re

from asi import Utils
from asi import Config
from asi.services import Base
from asi import RAIUrls
from asi.formats import H264

channels = {"1": "RaiUno", "2": "RaiDue", "3": "RaiTre", "23": "RaiGulp", "31": "RaiCinque", "32": "RaiPremium", "38": "RaiYoyo"}

# we want to extract all the
# h264_DIGIT
# which are now used for bwidth selection for MP4


def extract_h264_ext(value):
    res = {}
    reg = "^h264_(\d+)"
    for k in value:
        m = re.match(reg, k)
        url = value[k]
        if m and url:
            bwidth = int(m.group(1))
            H264.add_h264_url(res, bwidth, url)

    return res


def parse_item(grabber, channel, date, time, value, db):
    name = value["t"]
    desc = value["d"]
    secs = value["l"]

    length = None

    if secs != "":
        length = datetime.timedelta(seconds = int(secs))

    h264 = extract_h264_ext(value)

    # if the detailed h264 is not found, try with "h264"
    if not h264:
        single = value["h264"]
        H264.add_h264_url(h264, 0, single)

    tablet = value["urlTablet"]
    smart_phone = value["urlSmartPhone"]

    if h264:
        # sometimes RAI puts the same url for h264 and TS
        # normally this is only a valid h264,
        # so we skip it in TS

        h264_urls = h264.values()
        if tablet in h264_urls:
            tablet = None
        if smart_phone in h264_urls:
            smart_phone = None

    pid = value["i"]

    if h264 or tablet or smart_phone:
        pid = Utils.get_new_pid(db, pid)
        p = Program(grabber, channels[channel], date, time, pid, length, name, desc, h264, tablet, smart_phone)
        Utils.add_to_db(db, p)


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
                parse_item(grabber, channel, date, time, value, db)


def download(db, grabber, down_type):
    progress = Utils.get_progress()

    today = datetime.date.today()

    folder = Config.replay_folder

    for x in range(1, 8):
        day = today - datetime.timedelta(days = x)
        str_date = day.strftime("_%Y_%m_%d")

        for channel in channels.values():
            filename = channel + str_date + ".html"
            url = RAIUrls.replay + "/" + filename
            local_name = os.path.join(folder, filename)

            f = Utils.download(grabber, progress, url, local_name, down_type, "utf-8")

            if f:
                process(grabber, f, db)


class Program(Base.Base):
    def __init__(self, grabber, channel, date, hour, pid, length, title, desc, h264, tablet, smart_phone):
        super().__init__()

        self.pid = pid
        self.title = title
        self.h264 = h264
        self.description = desc
        self.channel = channel

        if tablet:    # higher quality normally
            self.ts = tablet
        else:
            self.ts = smart_phone

        self.datetime = datetime.datetime.strptime(date + " " + hour, "%Y-%m-%d %H:%M")

        self.grabber = grabber
        self.length = length

        name = Utils.make_filename(self.title)
        self.filename = self.pid + "-" + name
