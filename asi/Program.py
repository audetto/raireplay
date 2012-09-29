from __future__ import print_function

import sys
sys.path.append('/home/andrea/projects/cvs/3rdParty/m3u8')

import os
import m3u8

import urlgrabber.grabber
import urlgrabber.progress

class Program:
    def __init__(self, channel, date, time, pid, minutes, name, desc, h264, tablet):
        self.channel = channel
        self.date = date
        self.time = time
        self.pid = pid
        self.minutes = minutes
        self.name = name.encode('utf-8')
        self.desc = desc
        self.h264 = h264
        self.tablet = tablet
        self.m3 = None

    def display(self):
        print("Channel:", self.channel)
        print("PID:", self.pid)
        print("Name:", self.name)
        print("Description:", self.desc)
        print("Date:", self.date)
        print("Time:", self.time)
        print("Length:", self.minutes, "minutes")
        print()
        print("h264:", self.h264)
        print()
        print("tablet:", self.tablet)
        m3 = self.getTabletPlaylist()

        if m3.is_variant:
            for playlist in m3.playlists:
                format = "\tProgram: {0:>2}, Bandwidth: {1:>10}, Codecs: {2}"
                line = format.format(playlist.stream_info.program_id, playlist.stream_info.bandwidth, playlist.stream_info.codecs)
                print(line)


    def download(self, folder, format):
        if not os.path.exists(folder):
            os.makedirs(folder)

        if format == "h264":
            self.downloadH264(folder)
        elif format == "tablet":
            self.downloadTablet(folder)
        elif format == None:
            self.downloadH264(folder)


    def downloadH264(self, folder):
        g = urlgrabber.grabber.URLGrabber(progress_obj = urlgrabber.progress.TextMeter())
        localFilename = os.path.join(folder, self.pid + ".mp4")
        filename = g.urlgrab(self.h264, filename = localFilename)
        print("Got: ", filename)


    def getTabletPlaylist(self):
        if self.m3 == None:
            self.m3 = m3u8.load(self.tablet)
        return self.m3


    def downloadTablet(self, folder):
        m3 = self.getTabletPlaylist()
        if m3.is_variant:
            playlist = m3.playlists[0]
            uri = playlist.baseuri + "/" + playlist.uri
            item = m3u8.load(uri)
            if not m3.is_variant:
                print("m3u8 @ {0} is not a playlist".format(uri))
                return

            g = urlgrabber.grabber.URLGrabber(progress_obj = urlgrabber.progress.TextMeter(), quote = 0)
            localFilename = os.path.join(folder, self.pid + ".ts")
            out = open(localFilename, "a")

            print()
            print("Saving {0} as {1}".format(self.pid, localFilename))

            for seg in item.segments:
                uri = seg.baseuri + "/" + seg.uri
                s = g.urlopen(uri)
                out.write(s.read())

            print()
            print("Saved {0} as {1}".format(self.pid, localFilename))
