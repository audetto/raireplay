import json
import os
import urllib.parse
import datetime

from raireplay.common import utils, config
from raireplay.services import base


class Program(base.Base):
    def __init__(self, grabber, down_type, channel, date, hour, pid, length, title, desc, urls):
        super().__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.down_type = down_type

        if date and hour:
            self.datetime = datetime.datetime.strptime(date + " " + hour, "%d/%m/%Y %H:%M")
        else:
            self.datetime = datetime.datetime.now()

        self.grabber = grabber
        self.length = length

        self.urls = urls

        name = utils.make_filename(self.title)
        self.filename = name

    def get_ts(self):
        return None


def process(db, grabber, url, down_type):
    progress = utils.get_progress()

    folder = config.raiplay_folder

    o = urllib.parse.urlparse(url)
    filename = o.path.replace("/", "_")
    local_name = os.path.join(folder, filename + ".json")

    f = utils.download(grabber, progress, url, local_name, down_type, "utf-8", True)
    o = json.load(f)

    name = o['name']
    channel = o['channel']

    urls = [item['audio']['contentUrl'] for item in o['items']]

    pid = utils.get_new_pid(db, None)
    p = Program(grabber, down_type, channel, None, None, pid, None, name, '', urls)
    utils.add_to_db(db, p)


def download(db, grabber, radio, down_type):
    progress = utils.get_progress()

    folder = config.raiplay_folder

    o = urllib.parse.urlparse(radio)
    filename = o.path.replace("/", "_")
    url = radio + "?json"
    local_name = os.path.join(folder, filename + ".json")

    f = utils.download(grabber, progress, url, local_name, down_type, "utf-8", True)
    o = json.load(f)

    path_id = o['pathID']
    url = urllib.parse.urljoin(url, path_id)
    process(db, grabber, url, down_type)
