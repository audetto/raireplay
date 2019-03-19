import os
import datetime
import json

from asi import Utils
from asi import Config
from asi.services import Base
from asi import RAIUrls
import logging

channels = ["Rai1", "Rai2", "Rai3", "Rai4", "Rai5", "RaiGulp", "RaiPremium", "RaiYoyo", "RaiSport1", "RaiSport2",
            "RaiMovie", "RaiStoria", "RaiScuola"]


def parse_item(grabber, down_type, channel, value, db, dup):
    if value and "hasVideo" in value and value["hasVideo"]:

        id = value["ID"]

        if id not in dup:
            dup.add(id)

            name = value["name"]
            desc = value["description"]
            secs = value["duration"]

            date = value["datePublished"].strip()
            time = value["timePublished"].strip()

            length = secs

            path_id = value["pathID"]

            pid = Utils.get_new_pid(db, None)
            p = Program(grabber, down_type, channel, date, time, pid, length, name, desc, path_id)
            Utils.add_to_db(db, p)


def process(grabber, down_type, f, db, dup):
    s = f.read()
    s = s.replace('[an error occurred while processing this directive]', '')
    o = json.loads(s)

    for k1, v1 in o.items():
        channel = k1
        for v2 in v1:
            palinsesto = v2['palinsesto']
            if palinsesto:
                programmi = palinsesto[0]['programmi']
                for p in programmi:
                    parse_item(grabber, down_type, channel, p, db, dup)


def download(db, grabber, down_type):
    progress = Utils.get_progress()

    folder = Config.raiplay_folder

    dup = set()

    for channel in channels:
        filename = "canale=" + channel
        url = RAIUrls.raiplay + filename
        local_name = os.path.join(folder, filename + ".json")
        try:
            f = Utils.download(grabber, progress, url, local_name, down_type, "utf-8", True)

            if f:
                process(grabber, down_type, f, db, dup)
        except json.decoder.JSONDecodeError:
            logging.exception(f'JSON: {channel}')


class Program(Base.Base):
    def __init__(self, grabber, down_type, channel, date, hour, pid, length, title, desc, path_id):
        super().__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.down_type = down_type

        self.url = RAIUrls.base + path_id

        if date and hour:
            self.datetime = datetime.datetime.strptime(date + " " + hour, "%d/%m/%Y %H:%M")
        else:
            self.datetime = datetime.datetime.now()

        self.grabber = grabber
        self.length = length

        name = Utils.make_filename(self.title)
        self.filename = name

    def get_ts(self):
        if self.ts:
            return self.ts

        folder = Config.raiplay_folder
        name = Utils.http_filename(self.url)
        local_name = os.path.join(folder, name)
        progress = Utils.get_progress()

        f = Utils.download(self.grabber, progress, self.url, local_name, self.down_type, "utf-8", True)

        if f:
            o = json.load(f)
            url = o['video']['contentUrl']
            if url:
                self.ts = url
                return self.ts
