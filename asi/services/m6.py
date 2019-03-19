import os
import datetime

from xml.etree import ElementTree

from asi import utils
from asi import config
from asi.services import base

# this comes from M6group.groovy
# https://bitbucket.org/Illico/serviio_plugins/wiki/M6group.groovy
# and maybe earlier from XBMC
# http://mirrors.xbmc.org/addons/frodo/plugin.video.m6groupe/
# but it seems to be broken

# this plugin has been moved to use the iphone machinery
# which seems to work

channels = ["m6replay", "w9replay", "6terreplay", "styles", "stories", "comedy", "crazy_kitchen"]


def get_ts_url(link):
    #    ts = "https://lb.cdn.m6web.fr/c/cu/s/m6replay_iphone/iphone/{0}".format(link)
    ts = f"https://lb.cdn.m6web.fr/s/cu/prime/{link}"
    return ts


def get_catalogue_url(channel):
    # old catalogue
    #    catalogue_url = "http://static.m6replay.fr/catalog/m6group_web/{0}replay/catalogue.json"
    # iphone catalogue
    url = f"http://static.m6replay.fr/catalog/m6group_iphone/{channel}/catalogue.xml"
    return url


def get_info_url(channel, clip):
    clip_key = clip[-2:] + '/' + clip[-4:-2]
    url = f"http://static.m6replay.fr/catalog/m6group_iphone/{channel}/clip/{clip_key}/clip_infos-{clip}.xml"
    return url


def process(grabber, down_type, f, channel, db):
    root = ElementTree.parse(f).getroot()

    clp_list = root.find("clpList")

    for clp in clp_list:
        k = clp.get("id")
        title = clp.find("programName").text + " - " + clp.find("clpName").text
        desc = clp.find("desc").text
        date = clp.find("antennaDate").text
        if not date:
            date = clp.find("publiDate").text
        seconds = clp.find("duration").text

        length = datetime.timedelta(seconds=int(seconds))

        pid = utils.get_new_pid(db, k)
        p = Program(grabber, down_type, channel, date, pid, k, length, title, desc)
        utils.add_to_db(db, p)


def download(db, grabber, down_type):
    progress = utils.get_progress()

    for channel in channels:
        url = get_catalogue_url(channel)
        name = utils.http_filename(url) + "." + channel

        folder = config.m6_folder
        local_name = os.path.join(folder, name)

        f = utils.download(grabber, progress, url, local_name, down_type, "utf-8", True)
        if f:
            process(grabber, down_type, f, channel, db)


class Program(base.Base):
    def __init__(self, grabber, down_type, channel, date, pid, key, length, title, desc):
        super().__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.key = key
        self.down_type = down_type
        self.url = get_info_url(self.channel, self.key)

        if date:
            self.datetime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        else:
            self.datetime = datetime.datetime.now()

        self.grabber = grabber
        self.length = length

        name = utils.make_filename(self.title)
        self.filename = self.pid + "-" + name

    def display(self, width):
        super().display(width)

        print("URL:", self.url)
        print()

    def get_ts(self):
        if self.ts:
            return self.ts

        folder = config.m6_folder
        name = utils.http_filename(self.url)
        local_name = os.path.join(folder, name)
        progress = utils.get_progress()

        f = utils.download(self.grabber, progress, self.url, local_name, self.down_type, "utf-8", True)
        if f:
            root = ElementTree.parse(f).getroot()
            asset = root.find("asset")
            for v in asset.findall("assetItem"):
                u = v.find("url").text
                self.ts = get_ts_url(u)
                return self.ts
