from __future__ import print_function

import sys
sys.path.append('/home/andrea/projects/cvs/3rdParty/m3u8')

import os
import urlparse
import m3u8
import time
import json

from datetime import date
from datetime import timedelta

import urlgrabber.progress

from asi import Meter
from asi import Utils

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


def parseItem(channel, date, time, value):
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
        p = Program(channels[channel], date, time, pid, minutes, name, desc, h264, tablet, smartPhone)
        return p

    return None


def process(f, db):
    o = json.load(f)

    for k1, v1 in o.iteritems():
        if k1 == "now":
            continue
        if k1 == "defaultBannerVars":
            continue

        channel = k1

        for date, v2 in v1.iteritems():
            for time, value in v2.iteritems():
                p = parseItem(channel, date, time, value)

                if p != None:
                    if p.pid in db:
                        print("WARNING: duplicate pid {0}".format(p.pid))
                        #                        db[pid].display()
                        #                        p.display()

                    db[p.pid] = p


def download(db, grabber, replayFolder, type):
    progress_obj = urlgrabber.progress.TextMeter()

    today = date.today()

    for x in range(1, 8):
        day = today - timedelta(days = x)
        strDate = day.strftime("_%Y_%m_%d")

        for channel in channels.itervalues():
            filename = channel + strDate + ".html"
            url = baseUrl + "/" + filename
            localName = os.path.join(replayFolder, filename)

            f = Utils.download(grabber, progress_obj, url, localName, type, "utf-8")
            process(f, db)

    print()


class Program:
    def __init__(self, channel, date, hour, pid, minutes, name, desc, h264, tablet, smartPhone):
        self.channel = channel
        self.pid = pid
        self.minutes = minutes
        self.name = name
        self.desc = desc
        self.h264 = h264
        self.ts = getFullUrl(tablet, smartPhone)
        self.datetime = time.strptime(date + " " + hour, "%Y-%m-%d %H:%M")

        self.m3 = None


    def short(self):
        ts = time.strftime("%Y-%m-%d %H:%M", self.datetime)
        str = unicode("{0:>6}: {1} {2}").format(self.pid, ts, self.name)
        return str


    def display(self):
        width = urlgrabber.progress.terminal_width()

        print("=" * width)
        print("Channel:", self.channel)
        print("PID:", self.pid)
        print("Title:", self.name)
        print("Description:", self.desc)
        print("Date:", time.strftime("%Y-%m-%d %H:%M", self.datetime))
        print("Length:", self.minutes, "minutes")
        print("Filename:", self.getFilename())
        print()
        print("h264:", self.h264)
        print("ts:  ", self.ts)

        m3 = self.getTabletPlaylist()

        if m3 != None and m3.is_variant:
            print()
            for playlist in m3.playlists:
                format = "\tProgram: {0:>2}, Bandwidth: {1:>10}, Codecs: {2}"
                line = format.format(playlist.stream_info.program_id, playlist.stream_info.bandwidth, playlist.stream_info.codecs)
                print(line)
            print()


    def download(self, grabber, folder, format):
        if not os.path.exists(folder):
            os.makedirs(folder)

        if format == "h264":
            self.downloadH264(grabber, folder)
        elif format == "ts":
            self.downloadTablet(grabber, folder)
        elif format == None:
            self.downloadH264(grabber, folder)


    def downloadH264(self, grabber, folder):
        progress_obj = urlgrabber.progress.TextMeter()
        localFilename = os.path.join(folder, self.getFilename() + ".mp4")

        print()
        print("Saving {0} as {1}".format(self.pid, localFilename))

        filename = grabber.urlgrab(self.h264, filename = localFilename, progress_obj = progress_obj)

        print()
        print("Saved {0} as {1}".format(self.pid, filename))


    def getTabletPlaylist(self):
        if self.m3 == None:
            if self.ts != "":
                self.m3 = m3u8.load(self.ts)

        return self.m3


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


    def downloadTablet(self, grabber, folder):
        m3 = self.getTabletPlaylist()
        if m3.is_variant:
            playlist = m3.playlists[0]
            uri = playlist.baseuri + "/" + playlist.uri
            item = m3u8.load(uri)
            if not m3.is_variant:
                print("m3u8 @ {0} is not a playlist".format(uri))
                return

            localFilename = os.path.join(folder, self.getFilename() + ".ts")
            out = open(localFilename, "wb")

            print()
            print("Saving {0} as {1}".format(self.pid, localFilename))

            numberOfFiles = len(item.segments)
            progress = Meter.Meter(numberOfFiles, self.getFilename() + ".ts")

            for seg in item.segments:
                uri = seg.baseuri + "/" + seg.uri
                s = grabber.urlread(uri, progress_obj = progress, quote = 0)
                out.write(s)

            print()
            print("Saved {0} as {1}".format(self.pid, localFilename))
