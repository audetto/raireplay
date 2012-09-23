from __future__ import print_function

import os

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


    def display(self):
        print("Channel:", self.channel)
        print("PID:", self.pid)
        print("Name:", self.name)
        print("Description:", self.desc)
        print("Date:", self.date)
        print("Time:", self.time)
        print("Length:", self.minutes, "minutes")
        print("h264:", self.h264)
        print("tablet:", self.tablet)


    def download(self, folder, format):
        if not os.path.exists(folder):
            os.makedirs(folder)

        if self.h264 != "" and format == "h264":
            self.downloadH264(folder)
        else:
            self.downloadTablet(folder)


    def downloadH264(self, folder):
        g = urlgrabber.grabber.URLGrabber(progress_obj = urlgrabber.progress.TextMeter())
        localFilename = os.path.join(folder, self.pid + ".mp4")
        filename = g.urlgrab(self.h264, filename = localFilename)
        print("Got: ", filename)


    def downloadTablet(self, folder):
        g = urlgrabber.grabber.URLGrabber(progress_obj = urlgrabber.progress.TextMeter())
        localFilename = os.path.join(folder, self.pid + ".m3u8")
        filename = g.urlgrab(self.tablet, filename = localFilename)
        print("Got: ", filename)
