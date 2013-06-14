import os.path
import datetime
import html.parser

from asi import Utils
from asi import Config
from asi import Base
from asi import RAIUrls

from xml.etree import ElementTree


def processEpisode(grabber, e, db):
    h = html.parser.HTMLParser()

    title = e.attrib.get("name")
    date  = e.attrib.get("createDate")
    url   = e.attrib.get("uniquename")
    units = e.find("units")
    length = None
    description = None

    for u in units.findall("textUnit"):
        typ = u.attrib.get("type")
        if typ == "Durata":
            length = u.find("text").text
        elif typ == "Testo breve":
            description = u.find("text").text
            if description:
                description = h.unescape(description)

    video = units.find("videoUnit")
    if video == None:
        # no video, skip this episode
        return

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

    pid = Utils.getNewPID(db, None)
    item = Episode(pid, grabber, title, description, date, length, url, h264, ts, mms)
    Utils.addToDB(db, item)


def processSet(grabber, progress, folder, f, db, downType):
    root = ElementTree.parse(f).getroot()

    index = int(root.attrib.get("pageIndex"))
    total = int(root.attrib.get("pages"))

    items = root.find("items")
    for e in items.findall("item"):
        processEpisode(grabber, e, db)

    return (index, total)


def processBlock(grabber, progress, folder, f, db, downType):
    h = html.parser.HTMLParser()

    root =  ElementTree.parse(f).getroot()
    group = root.find("label").text
    group = h.unescape(group)
    categoria = root.findall('categoria')
    for e in categoria:
        video = e.find("video")
        if video is not None:
            name = e.find("label").text
            name = h.unescape(name)
            path = video.text

            pid = Utils.getNewPID(db, None)
            item = Item(pid, grabber, path, downType, group, name)
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
            uniqueNameNode = e.find("uniqueName")
            if uniqueNameNode is not None:
                uniqueName = uniqueNameNode.text
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
    def __init__(self, pid, grabber, url, downType, group, title):
        super(Item, self).__init__()

        self.pid = pid
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

        again = True
        url = self.url

        while again:
            name = Utils.httpFilename(url)
            localFilename = os.path.join(folder, name)

            f = Utils.download(self.grabber, progress, url, localFilename, downType, None, True)
            (index, total) = processSet(self.grabber, progress, folder, f, db, downType)
            if index + 1 == total:
                again = False
            else:
                # replace -V-0.xml -> -V-1.xml and so on
                pos = url.rfind("-V-")
                if pos == -1:
                    again = False
                else:
                    base = url[:pos]
                    url = "{0}-V-{1}.xml".format(base, index + 1)


class Episode(Base.Base):
    def __init__(self, pid, grabber, title, description, date, length, url, h264, ts, mms):
        super(Episode, self).__init__()

        self.pid = pid
        self.grabber = grabber

        self.title = title
        self.description = description
        self.url = url
        self.datetime = datetime.datetime.strptime(date, "%d-%m-%Y")
        self.length = length

        self.h264[0] = h264
        self.ts = ts
        self.mms = mms

        self.filename = Utils.makeFilename(self.title)


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Filename:", self.filename)
        print("Date:", Utils.strDate(self.datetime))
        print("Length:", self.length)
        print()
        print("URL:", self.url)
        Utils.displayH264(self.h264)
        print("m3u8:", self.ts)
        print("mms:", self.mms)
        print()

        m3 = self.getTabletPlaylist()
        Utils.displayM3U8(m3)
