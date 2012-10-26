from __future__ import print_function

import os.path
import urlgrabber.grabber
import urlgrabber.progress

import ConfigParser

from HTMLParser import HTMLParser
from xml.etree import ElementTree

from asi import Utils

# <meta name="videourl" content="....." />

# <ASX VERSION="3.0"><ENTRY><REF HREF="http://wms1.rai.it/raiunocdn/raiuno/79221.wmv" /></ENTRY></ASX>

# [Reference]
# Ref1=http://wms1.rai.it/raiunocdn/raiuno/79221.wmv?MSWMExt=.asf
# Ref2=http://92.122.190.142:80/raiunocdn/raiuno/79221.wmv?MSWMExt=.asf

# this one needs videoPath
# http://www.rai.tv/dl/RaiTV/programmi/media/ContentItem-6278dcf9-0225-456c-b4cf-71978200400a.html
#
# here we can get away with videoUrl
# http://www.rai.tv/dl/RaiTV/programmi/media/ContentItem-b9812490-7243-4545-a5fc-843bf46ec3c9.html

invalid = "http://creativemedia3.rai.it/video_no_available.mp4"


# create a subclass and override the handler methods
class VideoHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.values = Utils.Obj()
        self.values.videoUrl = None
        self.values.title = None
        self.values.program = None
        self.values.description = None
        self.values.videoPath = None

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            val = self.extract(attrs, "videourl")
            if val != None:
                self.values.videoUrl = val

            val = self.extract(attrs, "title")
            if val != None:
                self.values.title = val

            val = self.extract(attrs, "programmaTV")
            if val != None:
                self.values.program = val

            val = self.extract(attrs, "description")
            if val != None:
                self.values.description = val

        elif tag == "param":
            if len(attrs) > 0:
                if attrs[0][0] == "value":
                    path = attrs[0][1]
                    if path.find("videoPath") == 0:
                        firstEqual = path.find("=")
                        firstComma = path.find(",")
                        self.values.videoPath = path[firstEqual + 1: firstComma]

    def extract(self, attrs, name):
        if len(attrs) > 1:
            if attrs[0][0] == "name" and attrs[0][1] == name:
                if attrs[1][0] == "content":
                    return attrs[1][1]
        return None

class Demand:
    def __init__(self, url, folder, type):
        self.url = url

        g = urlgrabber.grabber.URLGrabber()

        localFilename = os.path.join(folder, Utils.httpFilename(self.url))

        f = Utils.download(g, self.url, localFilename, type, "latin1")

        parser = VideoHTMLParser()
        parser.feed(f.read())

        self.values = parser.values

        if self.values.videoUrl == None:
            self.values.videoUrl = self.values.videoPath

        #sometimes we get .mp4 which does not work
        self.values.videoUrl = self.values.videoUrl.replace("relinkerServlet.mp4", "relinkerServlet.htm")

        content = g.urlread(self.values.videoUrl)

        if content == invalid:
            self.asf = invalid
            self.mms = invalid
        else:
            root = ElementTree.fromstring(content)
            self.asf = root[0][0].attrib.get("HREF")

            # use urlgrab to make it work with ConfigParser
            content = g.urlgrab(self.asf)
            config = ConfigParser.ConfigParser()
            config.read(content)
            self.mms = config.get("Reference", "ref1")
            self.mms = self.mms.replace("http://", "mms://")

    def display(self):
        width = urlgrabber.progress.terminal_width()

        print("=" * width)
        print("title:      ", self.values.title)
        print("program:    ", self.values.program)
        print("description:", self.values.description)
        print()
        print("url:        ", self.url)
        print("videourl:   ", self.values.videoUrl)
        print("asf:        ", self.asf)
        print("mms:        ", self.mms)
