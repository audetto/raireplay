import os
import json
import datetime

from xml.etree import ElementTree

from asi import Utils
from asi.services import Base
from asi import Config
from asi.formats import H264

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
            pid = Utils.get_new_pid(db, num)
            p = Program(grabber, conf, date, length, pid, title, desc, num, channel)
            Utils.add_to_db(db, p)


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
    name = Utils.http_filename(url)
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


def download(db, grabber, downType, mediasetType):
    progress = Utils.get_progress()
    name = Utils.http_filename(configUrl)

    folder = Config.mediaset_folder
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress, configUrl, localName, downType, None, True)
    s = f.read().strip()
    root = ElementTree.fromstring(s)
    conf = parseConfig(root)

    if mediasetType == "tg5":
        url = conf["FullVideoRequestUrl"].replace("http://ww.", "http://www.")
        downloadItems(grabber, url, FULL_VIDEO, conf, folder, progress, downType, db)
    else:
        url = conf["ProgramListRequestUrl"]
        downloadItems(grabber, url, PROGRAM_LIST, conf, folder, progress, downType, db)


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

        name = Utils.make_filename(self.title)
        self.filename = self.pid + "-" + name


    def getH264(self):
        if self.h264:
            return self.h264

        content = Utils.get_string_from_url(self.grabber, self.url)
        root = ElementTree.fromstring(content)
        if root.tag == "smil":
            url = root.find("body").find("switch").find("video").attrib.get("src")
            H264.add_h264_url(self.h264, 0, url)
        return self.h264


    def display(self, width):
        super(Program, self).display(width)

        print("URL:", self.url)
        print()
