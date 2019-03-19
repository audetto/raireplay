import json
import os.path
import datetime

from asi import utils
from asi import config
from asi.services import base, page
from asi import raiurls


def process(grabber, f, db):
    o = json.load(f)

    for v in o:
        pid = utils.get_new_pid(db, None)
        p = Group(grabber, pid, v["title"], v["linkDemand"], v["date"], v["editore"])
        utils.add_to_db(db, p)


def download(db, grabber, down_type):
    page = utils.http_filename(raiurls.on_demand)

    folder = config.demand_folder
    local_filename = os.path.join(folder, page)

    progress = utils.get_progress()

    f = utils.download(grabber, progress, raiurls.on_demand, local_filename, down_type, "raw-unicode-escape", True)

    process(grabber, f, db)


class Group(base.Base):
    def __init__(self, grabber, pid, title, link, date, channel):
        super().__init__()

        self.pid = pid
        self.grabber = grabber
        self.title = title
        self.datetime = datetime.datetime.fromtimestamp(int(date) / 1000)
        self.channel = channel

        self.url = raiurls.base + link
        self.canFollow = True

    def display(self, width):
        super().display(width)

        print("URL:", self.url)
        print()

    def follow(self, db, down_type):
        page.download(db, self.grabber, self.url, down_type)
