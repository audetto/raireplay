import datetime
import os.path

from xml.etree import ElementTree

from asi import Utils
from asi import Config
from asi.services import Base, Item
from asi import RAIUrls
from asi.formats import H264

# example: without xls we get a nice XML,
# numContent is compulsory, but it seems a big number is accepted and gives the whole list
# http://www.rai.tv/StatisticheProxy/proxyPost.jsp?action=getLastContentByTag&numContents=12&tags=PageOB:Page-054bcd53-df7e-42c3-805b-dbe6e90bc817&domain=RaiTv&xsl=rai_tv-statisticheN&_=1351111295981


class Elem(Base.Base):
    def __init__(self, pid, grabber, data):

        super(Elem, self).__init__()

        self.pid           = pid
        self.title         = data.findtext("titolo")
        self.description   = data.findtext("descrizione")
        self.channel       = data.findtext("dominio")
        self.grabber       = grabber
        strTime            = data.findtext("datapubblicazione")

        strTime            = strTime.replace("-", "/")
        self.datetime      = datetime.datetime.strptime(strTime, "%d/%m/%Y")

        # extra experimental data
        h264               = data.findtext("h264")
        H264.add_h264_url(self.h264, 0, h264)

        self.ts            = data.findtext("m3u8")

        self.id            = data.findtext("localid")
        self.length        = data.findtext("durata")
        web =  data.findtext("web")
        if not web:
            web = RAIUrls.get_web_from_id(self.id)
        self.url           = RAIUrls.base + web

        self.filename      = Utils.make_filename(self.title)

        self.canFollow     = True


    def display(self, width):
        super(Elem, self).display(width)

        print("URL:", self.url)
        print()


    def follow(self, db, downType):
        pid = Utils.get_new_pid(db, self.pid)
        p = Item.Demand(self.grabber, self.url, downType, pid)
        Utils.add_to_db(db, p)


def download(db, grabber, url, downType):
    page = Utils.http_filename(url)
    page = os.path.splitext(page)[0]

    dataUrl = RAIUrls.get_page_data_url(page)

    folder = Config.page_folder
    localFilename = os.path.join(folder, page + ".xml")
    f = Utils.download(grabber, None, dataUrl, localFilename, downType, "utf-8")

    # ElementTree does not like unicode, it prefers byte strings
    s = f.read().strip()
    s = Utils.remove_invalid_xml_characters(s)
    root = ElementTree.fromstring(s)

    for child in root.findall("content"):
        pid = Utils.get_new_pid(db, None)
        it = Elem(pid, grabber, child)
        Utils.add_to_db(db, it)
