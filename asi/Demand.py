from __future__ import print_function

import urlgrabber.grabber
import urlgrabber.progress

import ConfigParser

from HTMLParser import HTMLParser
from xml.etree import ElementTree

# <meta name="videourl" content="....." />

# <ASX VERSION="3.0"><ENTRY><REF HREF="http://wms1.rai.it/raiunocdn/raiuno/79221.wmv" /></ENTRY></ASX>

# [Reference]
# Ref1=http://wms1.rai.it/raiunocdn/raiuno/79221.wmv?MSWMExt=.asf
# Ref2=http://92.122.190.142:80/raiunocdn/raiuno/79221.wmv?MSWMExt=.asf

# create a subclass and override the handler methods
class VideoHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.videourl = None
        self.title = None
        self.program = None
        self.description = None

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            val = self.extract(attrs, "videourl")
            if val != None:
                self.videourl = val

            val = self.extract(attrs, "title")
            if val != None:
                self.title = val

            val = self.extract(attrs, "programmatv")
            if val != None:
                self.program = val

            val = self.extract(attrs, "description")
            if val != None:
                self.description = val

    def extract(self, attrs, name):
        if len(attrs) > 1:
            if attrs[0][0] == "name" and attrs[0][1] == name:
                if attrs[1][0] == "content":
                    return attrs[1][1]
        return None

class Demand:
    def __init__(self, url):
        self.url = url

        g = urlgrabber.grabber.URLGrabber()
        content = g.urlread(self.url)

        parser = VideoHTMLParser()
        parser.feed(content)

        self.videourl    = parser.videourl
        self.title       = parser.title
        self.program     = parser.program
        self.description = parser.description

        #sometimes we get .mp4 which does not work
        self.videourl = self.videourl.replace("relinkerServlet.mp4", "relinkerServlet.htm")

        content = g.urlread(self.videourl)

        root = ElementTree.fromstring(content)
        self.asf = root[0][0].attrib.get("HREF")

        # use urlgrab to mak eit work with Configparser
        content = g.urlgrab(self.asf)
        config = ConfigParser.ConfigParser()
        config.read(content)
        self.mms = config.get("Reference", "ref1")
        self.mms = self.mms.replace("http://", "mms://")

    def display(self):
        width = urlgrabber.progress.terminal_width()

        print("=" * width)
        print("title:      ", self.title)
        print("program:    ", self.program)
        print("description:", self.description)
        print()
        print("url:        ", self.url)
        print("videourl:   ", self.videourl)
        print("asf:        ", self.asf)
        print("mms:        ", self.mms)
