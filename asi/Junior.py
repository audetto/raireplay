import os.path
import datetime

from asi import Utils
from asi import Config
from asi import Base
from asi import RAIUrls

from xml.etree import ElementTree


def processEpisode(grabber, e, db):
    title = e.attrib.get("name")
    date  = e.attrib.get("createDate")
    url   = e.attrib.get("uniquename")
    units = e.find("units")
    minutes = None
    description = None

    for u in units.findall("textUnit"):
        typ = u.attrib.get("type")
        if typ == "Durata":
            minutes = u.find("text").text
        elif typ == "Testo breve":
            description = u.find("text").text

    video = units.find("videoUnit")
    mms = video.find("url").text
    h264 = None
    ts = None

    for a in video.find("attributes").findall("attribute"):
        key = a.find("key").text
        value = a.find("value").text

        if key == "m3u8":
            ts = value
        elif key == "h264":
            h264 = value

    item = Episode(grabber, title, description, date, minutes, url, h264, ts, mms)
    Utils.addToDB(db, item)


def processSet(grabber, progress, folder, f, db, downType):
    root = ElementTree.parse(f).getroot()
    items = root.find("items")
    for e in items.findall("item"):
        processEpisode(grabber, e, db)


def processBlock(grabber, progress, folder, f, db, downType):
    root =  ElementTree.parse(f).getroot()
    group = root.find("label").text
    categoria = root.findall('categoria')
    for e in categoria:
        video = e.find("video")
        if video != None:
            name = e.find("label").text
            path = video.text
            item = Item(grabber, path, downType, group, name)
            Utils.addToDB(db, item)


def processPage(grabber, progress, folder, f, db, downType):
    root = ElementTree.parse(f).getroot().find('menu')
    for e in root:
        if e.tag == "item" and e.attrib.get("id") == "video":
            path = e.find("src").attrib.get("path")
            url = RAIUrls.getJuniorBlock(path)

            name = Utils.httpFilename(url)
            localFilename = os.path.join(folder, name)

            g = Utils.download(grabber, progress, url, localFilename, downType, None, True)
            processBlock(grabber, progress, folder, g, db, downType)


def process(grabber, progress, folder, f, db, downType):
    root = ElementTree.parse(f).getroot()

    for e in root:
        if e.tag == "elemento":
            titolo     = e.find("titolo").text
            uniqueName = e.find("uniqueName").text
            if uniqueName:
                url = RAIUrls.getJuniorPage(uniqueName)
                name = Utils.httpFilename(url)

                localFilename = os.path.join(folder, name)

                g = Utils.download(grabber, progress, url, localFilename, downType, None, True)
                processPage(grabber, progress, folder, g, db, downType)


def download(db, grabber, downType):
    page = Utils.httpFilename(RAIUrls.junior)

    folder = Config.juniorFolder
    localFilename = os.path.join(folder, page)

    progress = Utils.getProgress()
    f = Utils.download(grabber, progress, RAIUrls.junior, localFilename, downType, None, True)

    process(grabber, progress, folder, f, db, downType)


class Item(Base.Base):
    def __init__(self, grabber, url, downType, group, title):
        super(Item, self).__init__()

        self.grabber = grabber

        self.url = url
        self.title = group
        self.description = title


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Title:", self.title)
        print("Description:", self.description)
        print()
        print("URL:", self.url)
        print()


    def follow(self, db, downType):
        folder = Config.juniorFolder
        progress = Utils.getProgress()

        name = Utils.httpFilename(self.url)
        localFilename = os.path.join(folder, name)

        f = Utils.download(self.grabber, progress, self.url, localFilename, downType, None, True)
        processSet(self.grabber, progress, folder, f, db, downType)


class Episode(Base.Base):
    def __init__(self, grabber, title, description, date, minutes, url, h264, ts, mms):
        super(Episode, self).__init__()

        self.grabber = grabber

        self.title = title
        self.description = description
        self.url = url
        self.datetime = datetime.datetime.strptime(date, "%d-%m-%Y")
        self.minutes = minutes

        self.h264 = h264
        self.ts = ts
        self.mms = Utils.getMMSUrl(grabber, mms)

        self.filename = Utils.makeFilename(self.title)


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Filename:", self.filename)
        print("Date:", self.datetime.strftime("%Y-%m-%d %H:%M"))
        print("Length:", self.minutes, "minutes")
        print()
        print("URL:", self.url)
        print("h264:", self.h264)
        print("m3u8:", self.ts)
        print("mms:", self.mms)
        print()

        m3 = self.getTabletPlaylist()
        Utils.displayM3U8(self.m3)
