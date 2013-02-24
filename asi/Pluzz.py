

import os
import datetime
import json
import zipfile
import codecs

from asi import Utils
from asi import Config
from asi import Base

infoUrl = "http://webservices.francetelevisions.fr/catchup/flux/flux_main.zip"
baseUrl = "http://medias2.francetv.fr/catchup-mobile"


def parseItem(grabber, prog):
    pid     = prog["id_diffusion"]
    date    = prog["date"]
    hour    = prog["heure"]
    url     = baseUrl +  prog["url_video"]
    desc    = prog["accroche"]
    channel = prog["chaine"]
    name    = prog["titre"]
    minutes = prog["duree"]

    p = Program(grabber, channel, date, hour, pid, minutes, name, desc, url)

    return p


def process(grabber, f, db):
    o = json.load(f)

    programmes = o["programmes"]

    for prog in programmes:
        p = parseItem(grabber, prog)
        Utils.addToDB(db, p)


def download(db, grabber, downType):
    progress = Utils.getProgress()
    name = Utils.httpFilename(infoUrl)

    folder = Config.pluzzFolder
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress, infoUrl, localName, downType, None, True)

    z = zipfile.ZipFile(f, "r")

    decoder = codecs.getreader("ascii")

    for a in z.namelist():
        if a.find("catch_up_") == 0:
            with z.open(a) as f:
                process(grabber, decoder(f), db)

class Program(Base.Base):
    def __init__(self, grabber, channel, date, hour, pid, minutes, title, desc, url):
        super(Program, self).__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.datetime = datetime.datetime.strptime(date + " " + hour, "%Y-%m-%d %H:%M")
        self.ts = url

        self.grabber = grabber
        self.minutes = minutes

        name = Utils.makeFilename(self.title)
        self.filename = self.pid + "-" + name


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Channel:", self.channel)
        print("Title:", self.title)
        print("Description:", self.description)
        print("Date:", self.datetime.strftime("%Y-%m-%d %H:%M"))
        print("Length:", self.minutes, "minutes")
        print("Filename:", self.filename)
        print()
        print("url:", self.ts)

        m3 = self.getTabletPlaylist()
        Utils.displayM3U8(self.m3)
