import os
import json
import datetime

from xml.etree import ElementTree

from raireplay.common import utils
from raireplay.services import base
from raireplay.common import config
from raireplay.formats import h264

config_url = "http://app.mediaset.it/app/videomediaset/iPhone/2.0.2/videomediaset_iphone_config.plist"

FULL_VIDEO = 0
PROGRAM_LIST = 1
PROGRAM = 2
PROGRAM_VIDEO = 3


def parse_config(root):
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


def process_full_video(grabber, f, tag, conf, folder, progress, down_type, db):
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
            pid = utils.get_new_pid(db, num)
            p = Program(grabber, conf, date, length, pid, title, desc, num, channel)
            utils.add_to_db(db, p)


def process_program_list(grabber, f, conf, folder, progress, down_type, db):
    o = json.load(f)

    for a in o["programmi"]["programma"]:
        url = a["urlxml"]
        download_items(grabber, url, PROGRAM, conf, folder, progress, down_type, db)


def process_program(grabber, f, conf, folder, progress, down_type, db):
    o = json.load(f)

    url = o["brandinfo"]["url_xmlvideo"]
    download_items(grabber, url, PROGRAM_VIDEO, conf, folder, progress, down_type, db)


def download_items(grabber, url, which, conf, folder, progress, down_type, db):
    name = utils.http_filename(url)
    local_name = os.path.join(folder, name)

    f = utils.download(grabber, progress, url, local_name, down_type, "utf-8", True)

    if f:
        if which == FULL_VIDEO:
            process_full_video(grabber, f, "episodi_interi", conf, folder, progress, down_type, db)
        elif which == PROGRAM_LIST:
            process_program_list(grabber, f, conf, folder, progress, down_type, db)
        elif which == PROGRAM:
            process_program(grabber, f, conf, folder, progress, down_type, db)
        elif which == PROGRAM_VIDEO:
            process_full_video(grabber, f, "brand", conf, folder, progress, down_type, db)


def download(db, grabber, down_type, mediaset_type):
    progress = utils.get_progress()
    name = utils.http_filename(config_url)

    folder = config.mediaset_folder
    local_name = os.path.join(folder, name)

    f = utils.download(grabber, progress, config_url, local_name, down_type, None, True)
    s = f.read().strip()
    root = ElementTree.fromstring(s)
    conf = parse_config(root)

    if mediaset_type == "tg5":
        url = conf["FullVideoRequestUrl"].replace("http://ww.", "http://www.")
        download_items(grabber, url, FULL_VIDEO, conf, folder, progress, down_type, db)
    else:
        url = conf["ProgramListRequestUrl"]
        download_items(grabber, url, PROGRAM_LIST, conf, folder, progress, down_type, db)


def get_mediaset_link(conf, num):
    url = conf["CDNSelectorRequestUrl"]
    url = url.replace("%@", num)
    return url


class Program(base.Base):
    def __init__(self, grabber, conf, datetime, length, pid, title, desc, num, channel):
        super().__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.num = num
        self.datetime = datetime

        self.length = length
        self.grabber = grabber

        self.url = get_mediaset_link(conf, num)

        name = utils.make_filename(self.title)
        self.filename = self.pid + "-" + name

    def get_h264(self):
        if self.h264:
            return self.h264

        content = utils.get_string_from_url(self.grabber, self.url)
        root = ElementTree.fromstring(content)
        if root.tag == "smil":
            url = root.find("body").find("switch").find("video").attrib.get("src")
            h264.add_h264_url(self.h264, 0, url)
        return self.h264

    def display(self, width):
        super().display(width)

        print("URL:", self.url)
        print()
