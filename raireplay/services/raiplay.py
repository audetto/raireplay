import os
import datetime
import json
from string import Template

from raireplay.common import utils
from raireplay.common import config
from raireplay.services import base
from raireplay.common import raiurls
import logging

channels = ["rai-1", "rai-2", "rai-3", "rai-4", "rai-5", "rai-gulp", "rai-premium", "rai-yoyo", "rai-movie",
            "rai-storia", "rai-scuola", "rai-news-24", "rai-sport-piu-hd"]


def parse_item(grabber, down_type, value, db, dup):
    if value and "has_video" in value and value["has_video"]:
        id = value['playlist_id']

        if id not in dup:
            dup.add(id)

            name = value["name"]
            desc = value["description"]
            secs = value["duration"]
            channel = value["channel"]

            date = value["date"].strip()
            time = value["hour"].strip()

            length = secs

            path_id = value["path_id"]

            pid = utils.get_new_pid(db, None)
            p = Program(grabber, down_type, channel, date, time, pid, length, name, desc, path_id)
            utils.add_to_db(db, p)


def process(grabber, down_type, f, db, dup):
    o = json.load(f)

    for event in o['events']:
        parse_item(grabber, down_type, event, db, dup)


def download(db, grabber, down_type):
    progress = utils.get_progress()

    folder = config.raiplay_folder

    dup = set()

    template = Template(raiurls.raiplay)
    today = datetime.date.today()

    for x in range(1, 8):
        day = today - datetime.timedelta(days=x)
        str_date = day.strftime("%d-%m-%Y")

        for channel in channels:
            filename = f'{channel}_{str_date}.json'
            url = template.substitute({'channel': channel, 'date': str_date})
            local_name = os.path.join(folder, filename)
            try:
                f = utils.download(grabber, progress, url, local_name, down_type, "utf-8", True)

                if f:
                    process(grabber, down_type, f, db, dup)
            except json.decoder.JSONDecodeError:
                logging.exception(f'JSON: {channel}')


class Program(base.Base):
    def __init__(self, grabber, down_type, channel, date, hour, pid, length, title, desc, path_id):
        super().__init__()

        self.pid = pid
        self.title = title
        self.description = desc
        self.channel = channel
        self.down_type = down_type

        self.url = raiurls.raiplay_base + path_id

        if date and hour:
            self.datetime = datetime.datetime.strptime(date + " " + hour, "%d/%m/%Y %H:%M")
        else:
            self.datetime = datetime.datetime.now()

        self.grabber = grabber
        self.length = length

        name = utils.make_filename(self.title)
        self.filename = name

    def get_ts(self):
        if self.ts:
            return self.ts

        folder = config.raiplay_folder
        name = utils.http_filename(self.url)
        local_name = os.path.join(folder, name)
        progress = utils.get_progress()

        f = utils.download(self.grabber, progress, self.url, local_name, self.down_type, "utf-8", True)

        if f:
            o = json.load(f)
            url = o['video']['content_url']
            if url:
                self.ts = url
                return self.ts
