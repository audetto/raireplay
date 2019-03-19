import os
import datetime
import json

from asi import utils
from asi import config
from asi.services import base

programs_url = "http://api.tf1.fr/tf1-programs/iphone/limit/100/"
news_url = "http://api.tf1.fr/tf1-homepage-news/iphone/"
homepage_url = "http://api.tf1.fr/tf1-homepage/iphone/"


def get_data_url(prog_id, item):
    url = f"http://api.tf1.fr/tf1-vods/iphone//integral/{item}/program_id/{prog_id}"
    return url


def get_wat_link(wat_id):
    url = f"http://www.wat.tv/get/iphone/{wat_id}.m3u8?bwmin=100000&bwmax=490000"
    return url


def parse_item(grabber, prog, name, db):
    pid = str(prog["id"])
    desc = prog["longTitle"]
    pub_date = prog["publicationDate"]
    duration = prog["duration"]
    name = name + " - " + prog["shortTitle"]
    wat = prog["watId"]
    category = prog["videoCategory"]

    length = datetime.timedelta(seconds=duration)
    date = datetime.datetime.strptime(pub_date, "%Y-%m-%d %H:%M:%S")

    # ignore the countless "extract", "bonus", "short" which last just a few minutes
    if category == "fullvideo":
        pid = utils.get_new_pid(db, pid)
        p = Program(grabber, date, length, pid, name, desc, wat, category)
        utils.add_to_db(db, p)


def process_group(grabber, f, name, db):
    o = json.load(f)

    for prog in o:
        parse_item(grabber, prog, name, db)


def process_news(grabber, f, folder, progress, down_type, db):
    o = json.load(f)

    for prog in o:
        name = prog["programName"]
        group_id = prog["programId"]

        download_group(grabber, name, group_id, folder, progress, down_type, db)

        # this group contains the info of the most recent Item
        # we add an other item with the group name
        # some info will still be missing

        title = prog["title"]
        wat = prog["linkAttributes"]["watId"]
        category = prog["linkAttributes"]["videoCategory"]

        pid = utils.get_new_pid(db, group_id)
        p = Program(grabber, datetime.datetime.now(), None, pid, name, title, wat, category)
        utils.add_to_db(db, p)


def process_programs(grabber, f, folder, progress, down_type, db):
    o = json.load(f)

    for prog in o:
        name = prog["shortTitle"]
        group_id = prog["id"]

        # here, we do not know the most recent item
        # we simply have to go through them all

        download_group(grabber, name, group_id, folder, progress, down_type, db)


def download_group(grabber, name, group_id, folder, progress, down_type, db):
    # we set it to True as this is a group
    # and subject to continuous changes
    check_timestamp = True

    # .0
    url_0 = get_data_url(group_id, 0)
    local_name_0 = os.path.join(folder, str(group_id) + ".0.json")
    f_0 = utils.download(grabber, progress, url_0, local_name_0, down_type, "utf-8", check_timestamp)

    if f_0:
        process_group(grabber, f_0, name, db)

    # .1
    url_1 = get_data_url(group_id, 1)
    local_name_1 = os.path.join(folder, str(group_id) + ".1.json")
    f_1 = utils.download(grabber, progress, url_1, local_name_1, down_type, "utf-8", check_timestamp)

    if f_1:
        process_group(grabber, f_1, name, db)


def download(db, grabber, down_type):
    progress = utils.get_progress()

    folder = config.tf1_folder

    local_name = os.path.join(folder, "news.json")
    f = utils.download(grabber, progress, news_url, local_name, down_type, "utf-8", True)

    process_news(grabber, f, folder, progress, down_type, db)

    local_name = os.path.join(folder, "programs.json")
    f = utils.download(grabber, progress, programs_url, local_name, down_type, "utf-8", True)

    process_programs(grabber, f, folder, progress, down_type, db)


class Program(base.Base):
    def __init__(self, grabber, datetime, length, pid, title, desc, wat, category):
        super().__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = "tf1"
        self.wat = wat
        self.datetime = datetime
        self.category = category

        self.length = length
        self.grabber = grabber
        self.ts = get_wat_link(self.wat)

        name = utils.make_filename(self.title)
        self.filename = self.pid + "-" + name

    def display(self, width):
        super().display(width)

        print()
        print("Category:", self.category)
