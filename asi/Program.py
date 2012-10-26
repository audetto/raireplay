from __future__ import print_function

import sys
sys.path.append('/home/andrea/projects/cvs/3rdParty/m3u8')

import os
import urlparse
import m3u8
import time

import urlgrabber.grabber
import urlgrabber.progress

from asi import Meter
from asi import Utils

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
        str = self.pid + ": " + ts + " " + self.name
        return str


    def display(self):
        width = urlgrabber.progress.terminal_width()

        print("=" * width)
        print("Channel:", self.channel)
        print("PID:", self.pid)
        print("Name:", self.name)
        print("Description:", self.desc)
        print("Date:", time.strftime("%Y-%m-%d %H:%M", self.datetime))
        print("Length:", self.minutes, "minutes")
        print("Filename: ", self.getFilename())
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


    def download(self, folder, format):
        if not os.path.exists(folder):
            os.makedirs(folder)

        if format == "h264":
            self.downloadH264(folder)
        elif format == "ts":
            self.downloadTablet(folder)
        elif format == None:
            self.downloadH264(folder)


    def downloadH264(self, folder):
        g = urlgrabber.grabber.URLGrabber(progress_obj = urlgrabber.progress.TextMeter())
        localFilename = os.path.join(folder, self.getFilename() + ".mp4")

        print()
        print("Saving {0} as {1}".format(self.pid, localFilename))

        filename = g.urlgrab(self.h264, filename = localFilename)

        print()
        print("Saved {0} as {1}".format(self.pid, filename))


    def getTabletPlaylist(self):
        if self.m3 == None:
            if self.ts != "":
                self.m3 = m3u8.load(self.ts)

        return self.m3


    def getFilename(self):

        if self.ts == "":
            return self.pid

        fullName = Utils.httpFilename(self.ts)
        tmp = fullName.split(",")[0]
        posOfDash = tmp.rfind("-")
        nice = tmp[0 : posOfDash]

        filename = self.pid + "-" + nice

        return filename


    def downloadTablet(self, folder):
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
            progress = Meter.Meter(numberOfFiles, self.pid + ".ts")
            g = urlgrabber.grabber.URLGrabber(progress_obj = progress, quote = 0)

            for seg in item.segments:
                uri = seg.baseuri + "/" + seg.uri
                s = g.urlread(uri)
                out.write(s)

            print()
            print("Saved {0} as {1}".format(self.pid, localFilename))
