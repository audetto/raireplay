import os
import datetime
import json

from asi import Utils
from asi import Config
from asi.services import Base, Item
from asi import RAIUrls
from asi.formats import H264


# try to guess a date from a description like
# "TG2 ore 23:30 del 14/01/2013"
def is_there_a_date(oldDate, description):
    try:
        del_giorno = description[-14:]
        if del_giorno.find("del ") != 0:
            return oldDate
        possible_date = del_giorno[4:].replace("-", "/")
        new_date = datetime.datetime.strptime(possible_date, "%d/%m/%Y")
        str_date = new_date.strftime("%d/%m/%Y")
        return str_date
    except ValueError:
        return oldDate


def process_set(grabber, title, time, f, db):
    o = json.load(f)

    channel = "TG"

    prog = o.get("integrale")
    if prog:
        url = prog["weblink"]
        h264 = prog["h264"]
        m3u8 = prog["m3u8"]
        if time == "LIS":
            # strange time for some TG3
            time = "00:00"

        description = prog["name"]
        date = prog["date"]

        # the filed "date" seems to be always TODAY
        # so we might actually get a program from yesterday
        date = is_there_a_date(date, description)
        datetime = date + " " + time

        pid = Utils.get_new_pid(db, None)
        p = Program(grabber, url, channel, datetime, pid, title, description, h264, m3u8)
        Utils.add_to_db(db, p)
    else:
        # get the list
        lst = o.get("list")

        if not lst:
            return

        for prg in lst:
            tp = prg["type"]
            if tp != "empty":
                url = prg["weblink"]
                h264 = prg["h264"]
                m3u8 = prg["m3u8"]
                dt = prg["date"] + " 00:00"
                a_title = title + "-" + prg["name"]
                description = prg["desc"]

                pid = Utils.get_new_pid(db, None)
                p = Program(grabber, url, channel, dt, pid, a_title, description, h264, m3u8)
                Utils.add_to_db(db, p)


def process_item(grabber, progress, down_type, title, time, url, db):
    folder = Config.tg_folder

    name = Utils.http_filename(url)
    local_name = os.path.join(folder, name)

    f = Utils.download(grabber, progress, url, local_name, down_type, "utf-8", True)

    if f:
        process_set(grabber, title, time, f, db)


def processGroup(grabber, progress, down_type, prog, db):
    name = prog["title"]

    edizioni = prog.get("edizioni")
    dettaglio = prog.get("dettaglio")
    if edizioni:
        for time, url in edizioni.items():
            title = name + " " + time
            process_item(grabber, progress, down_type, title, time, url, db)
    elif dettaglio.find("ContentSet") >= 0:
        process_item(grabber, progress, down_type, name, None, dettaglio, db)


def process(grabber, progress, down_type, f, db):
    o = json.load(f)

    programmes = o["list"]

    for prog in programmes:
        processGroup(grabber, progress, down_type, prog, db)


def download(db, grabber, down_type):
    progress = Utils.get_progress()
    name = Utils.http_filename(RAIUrls.info)

    folder = Config.tg_folder
    local_name = os.path.join(folder, name)

    f = Utils.download(grabber, progress, RAIUrls.info, local_name, down_type, "utf-8", True)
    process(grabber, progress, down_type, f, db)


class Program(Base.Base):
    def __init__(self, grabber, url, channel, date, pid, title, desc, h264, m3u8):
        super().__init__()

        self.url = url
        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        strtime = date.replace("-", "/")
        self.datetime = datetime.datetime.strptime(strtime, "%d/%m/%Y %H:%M")
        H264.add_h264_url(self.h264, 0, h264)
        if m3u8:
            self.ts = m3u8

        self.grabber = grabber

        name = Utils.make_filename(self.title)
        self.filename = name + "-" + self.datetime.strftime("%Y-%m-%d")
        self.canFollow = True

    def display(self, width):
        super().display(width)

        print("URL:", self.url)
        print()

    def follow(self, db, down_type):
        pid = Utils.get_new_pid(db, self.pid)
        p = Item.Demand(self.grabber, self.url, down_type, pid)
        Utils.add_to_db(db, p)
