import json
import os.path
import datetime

from asi import Utils
from asi import Config
from asi.services import Base, Page
from asi import RAIUrls


def process(grabber, f, db):
    o = json.load(f)

    for v in o:
        pid = Utils.get_new_pid(db, None)
        p = Group(grabber, pid, v["title"], v["linkDemand"], v["date"], v["editore"])
        Utils.add_to_db(db, p)


def download(db, grabber, down_type):
    page = Utils.http_filename(RAIUrls.on_demand)

    folder = Config.demand_folder
    local_filename = os.path.join(folder, page)

    progress = Utils.get_progress()

    f = Utils.download(grabber, progress, RAIUrls.on_demand, local_filename, down_type, "raw-unicode-escape", True)

    process(grabber, f, db)


class Group(Base.Base):
    def __init__(self, grabber, pid, title, link, date, channel):
        super().__init__()

        self.pid = pid
        self.grabber = grabber
        self.title = title
        self.datetime = datetime.datetime.fromtimestamp(int(date) / 1000)
        self.channel = channel

        self.url = RAIUrls.base + link
        self.canFollow = True

    def display(self, width):
        super().display(width)

        print("URL:", self.url)
        print()

    def follow(self, db, down_type):
        Page.download(db, self.grabber, self.url, down_type)
