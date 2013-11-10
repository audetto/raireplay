import os
import json
import datetime

from asi import Utils
from asi import Config
from asi import Base

# this comes from M6group.groovy
# https://bitbucket.org/Illico/serviio_plugins/wiki/M6group.groovy


def getCatalogueUrl(channel):
    catalogueUrl = "http://static.m6replay.fr/catalog/m6group_web/{0}replay/catalogue.json"
    url = catalogueUrl.format(channel)
    return url


def process(grabber, f, channel, db):
    o = json.load(f)

    clpList = o["clpList"]

    for k, v in clpList.items():
        if v["type"] == "vi":
            title = v["programName"] + " - " + v["clpName"]
            desc = v["desc"]
            date = v["antennaDate"]
            seconds = v["duration"]

            length = datetime.timedelta(seconds = int(seconds))

            url = None

            pid = Utils.getNewPID(db, k)
            p = Program(grabber, channel, date, pid, length, title, desc, url)
            Utils.addToDB(db, p)


def download(db, grabber, downType):
    progress = Utils.getProgress()

    channel = "m6"
    url = getCatalogueUrl(channel)
    name = Utils.httpFilename(url)

    folder = Config.m6Folder
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress, url, localName, downType, "utf-8", True)
    if (f):
        process(grabber, f, channel, db)


class Program(Base.Base):
    def __init__(self, grabber, channel, date, pid, length, title, desc, url):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel

        if date:
            self.datetime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        else:
            self.datetime =  datetime.datetime.now()

        self.grabber = grabber
        self.length = length

        name = Utils.makeFilename(self.title)
        self.filename = self.pid + "-" + name


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

        super(Program, self).display(width)
