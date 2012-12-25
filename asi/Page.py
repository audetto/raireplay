from __future__ import print_function

import time
import os.path
import urlgrabber.progress

from xml.etree import ElementTree

from asi import Utils
from asi import Config
from asi import Item

# example: without xls we get a nice XML,
# numContent is compulsory, but it seems a big number is accepted and gives the whole list
# http://www.rai.tv/StatisticheProxy/proxyPost.jsp?action=getLastContentByTag&numContents=12&tags=PageOB:Page-054bcd53-df7e-42c3-805b-dbe6e90bc817&domain=RaiTv&xsl=rai_tv-statisticheN&_=1351111295981

# returns the url that requests the list of ContentItems behind a Page-xxx page
def getDataUrl(page):
    n = 1000 # just get them all
    url = "http://www.rai.tv/StatisticheProxy/proxyPost.jsp?action=getLastContentByTag&numContents={0}&tags=PageOB:{1}&domain=RaiTv".format(n, page)
    return url


class Elem:
    def __init__(self, pid, data):
        self.pid           = pid
        self.id            = data.findtext("localid")
        self.length        = data.findtext("durata")
        self.title         = data.findtext("titolo")
        self.description   = data.findtext("descrizione")
        web =  data.findtext("web")
        if web == None:
            web = Utils.getWebFromID(self.id)
        self.url           = Utils.baseUrl + web
        strTime            = data.findtext("datapubblicazione")
        self.datetime      = time.strptime(strTime, "%d/%m/%Y")

        # extra experimental data
        self.h264          = data.findtext("h264")
        self.m3u8          = data.findtext("m3u8")


    def short(self, fmt):
        ts = time.strftime("%Y-%m-%d %H:%M", self.datetime)
        str = fmt.format(self.pid, ts, self.title)
        return str


    def display(self):
        width = urlgrabber.progress.terminal_width()

        print("=" * width)
        print("PID:", self.pid)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Date:", time.strftime("%Y-%m-%d %H:%M", self.datetime))
        print("Length:", self.length)
        print("URL:", self.url)
        print("h264:", self.h264)
        print("m3u8:", self.m3u8)
        print()


    def follow(self, db, grabber, downType):
        p = Item.Demand(grabber, self.url, downType, self.pid)
        db[str(self.pid)] = p


def download(db, grabber, url, downType):
    page = Utils.httpFilename(url)
    page = os.path.splitext(page)[0]

    dataUrl = getDataUrl(page)

    folder = Config.pageFolder
    localFilename = os.path.join(folder, page + ".xml")
    f = Utils.download(grabber, None, dataUrl, localFilename, downType, "utf-8")

    # ElementTree does not like unicode, it prefers byte strings
    root = ElementTree.fromstring(f.read().strip().encode("utf-8"))

    pid = 0

    for child in root:
        if child.tag == "content":
            it = Elem(pid, child)
            # use str() as a key for consistency with --replay
            db[str(pid)] = it
            pid = pid + 1
