

import datetime
import os.path

from xml.etree import ElementTree

from asi import Utils
from asi import Config
from asi import Item
from asi import Base
from asi import RAIUrls

# example: without xls we get a nice XML,
# numContent is compulsory, but it seems a big number is accepted and gives the whole list
# http://www.rai.tv/StatisticheProxy/proxyPost.jsp?action=getLastContentByTag&numContents=12&tags=PageOB:Page-054bcd53-df7e-42c3-805b-dbe6e90bc817&domain=RaiTv&xsl=rai_tv-statisticheN&_=1351111295981


class Elem(Base.Base):
    def __init__(self, pid, grabber, data):

        super(Elem, self).__init__()

        self.pid           = pid
        self.title         = data.findtext("titolo")
        self.description   = data.findtext("descrizione")
        self.grabber       = grabber
        strTime            = data.findtext("datapubblicazione")

        strTime            = strTime.replace("-", "/")
        self.datetime      = datetime.datetime.strptime(strTime, "%d/%m/%Y")

        # extra experimental data
        h264               = data.findtext("h264")
        Utils.addH264Url(self.h264, 0, h264)

        self.ts            = data.findtext("m3u8")

        self.id            = data.findtext("localid")
        self.length        = data.findtext("durata")
        web =  data.findtext("web")
        if not web:
            web = RAIUrls.getWebFromID(self.id)
        self.url           = RAIUrls.base + web

        self.filename      = Utils.makeFilename(self.title)

    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Date:", Utils.strDate(self.datetime))
        print("Length:", self.length)
        print("Filename:", self.filename)
        print("Follow: ENABLED")
        print()
        print("URL:", self.url)

        super(Elem, self).display(width)


    def follow(self, db, downType):
        pid = Utils.getNewPID(db, self.pid)
        p = Item.Demand(self.grabber, self.url, downType, pid)
        Utils.addToDB(db, p)


def download(db, grabber, url, downType):
    page = Utils.httpFilename(url)
    page = os.path.splitext(page)[0]

    dataUrl = RAIUrls.getPageDataUrl(page)

    folder = Config.pageFolder
    localFilename = os.path.join(folder, page + ".xml")
    f = Utils.download(grabber, None, dataUrl, localFilename, downType, "utf-8")

    # ElementTree does not like unicode, it prefers byte strings
    s = f.read().strip()
    s = Utils.removeInvalidXMLCharacters(s)
    root = ElementTree.fromstring(s)

    for child in root.findall("content"):
        pid = Utils.getNewPID(db, None)
        it = Elem(pid, grabber, child)
        Utils.addToDB(db, it)
