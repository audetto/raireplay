import os
import json
import datetime

from xml.etree import ElementTree

from asi import Utils
from asi import Base
from asi import Config

configUrl = "http://app.mediaset.it/app/videomediaset/iPhone/2.0.2/videomediaset_iphone_config.plist"

FULL_VIDEO = 0
PROGRAM_LIST = 1
PROGRAM = 2
PROGRAM_VIDEO = 3

def parseConfig(root):
    dic = root.find("dict")

    result = {}

    process = False
    for n in dic.iter():
        if n.tag == "key" and n.text == "Configuration":
            process = True
        elif n.tag == "dict" and process:
            process = False
            for nn in n.iter():
                if nn.tag == "key":
                    name = nn.text
                elif nn.tag == "string":
                    result[name] = nn.text
            
    return result


def processFullVideo(grabber, f, tag, conf, folder, progress, downType, db):
    o = json.load(f)

    videos = o[tag]["video"]

    for v in videos:
        title = v["brand"]["value"] + " " + v["title"]
        desc = v["desc"]
        channel = v["channel"]
        date = datetime.datetime.strptime(v["date"], "%d/%m/%Y")
        length = v["duration"]
        num = v["id"]

        category = v["subbrand"]["name"]

        if category == "full":
            pid = Utils.getNewPID(db, num)
            p = Program(grabber, conf, date, length, pid, title, desc, num, channel)
            Utils.addToDB(db, p)


def processProgramList(grabber, f, conf, folder, progress, downType, db):
    o = json.load(f)

    for a in o["programmi"]["programma"]:
        url = a["urlxml"]
        downloadItems(grabber, url, PROGRAM, conf, folder, progress, downType, db)


def processProgram(grabber, f, conf, folder, progress, downType, db):
    o = json.load(f)

    url = o["brandinfo"]["url_xmlvideo"]
    downloadItems(grabber, url, PROGRAM_VIDEO, conf, folder, progress, downType, db)


def downloadItems(grabber, url, which, conf, folder, progress, downType, db):
    name = Utils.httpFilename(url)
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress, url, localName, downType, "utf-8", True)

    if f:
        if which == FULL_VIDEO:
            processFullVideo(grabber, f, "episodi_interi", conf, folder, progress, downType, db)
        elif which == PROGRAM_LIST:
            processProgramList(grabber, f, conf, folder, progress, downType, db)
        elif which == PROGRAM:
            processProgram(grabber, f, conf, folder, progress, downType, db)
        elif which == PROGRAM_VIDEO:
            processFullVideo(grabber, f, "brand", conf, folder, progress, downType, db)


def download(db, grabber, downType):
    progress = Utils.getProgress()
    name = Utils.httpFilename(configUrl)

    folder = Config.mediasetFolder
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress, configUrl, localName, downType, None, True)
    s = f.read().strip()
    root = ElementTree.fromstring(s)
    conf = parseConfig(root)

    url = conf["ProgramListRequestUrl"]
    downloadItems(grabber, url, PROGRAM_LIST, conf, folder, progress, downType, db)

    url = conf["FullVideoRequestUrl"].replace("http://ww.", "http://www.")
    downloadItems(grabber, url, FULL_VIDEO, conf, folder, progress, downType, db)


def getMediasetLink(conf, num):
    url = conf["CDNSelectorRequestUrl"]
    url = url.replace("%@", num)
    return url


class Program(Base.Base):
    def __init__(self, grabber, conf, datetime, length, pid, title, desc, num, channel):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.num = num
        self.datetime = datetime

        self.length = length
        self.grabber = grabber

        self.url = getMediasetLink(conf, num)

        name = Utils.makeFilename(self.title)
        self.filename = self.pid + "-" + name


    def download(self, folder, options):
        if not self.h264:
            content = Utils.getStringFromUrl(self.grabber, self.url)
            root = ElementTree.fromstring(content)
            if root.tag == "smil":
                url = root.find("body").find("switch").find("video").attrib.get("src")
                self.h264[0] = url

        super(Program, self).download(folder, options)


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Channel:", self.channel)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Date:", Utils.strDate(self.datetime))
        print("Length:", self.length)
        print("Filename:", self.filename)
        print()
        print("url:", self.url)
