import os
import urllib.parse
import json

from asi import utils
from asi import config
from asi.services import raiplay


def process_set(grabber, down_type, f, db):
    o = json.load(f)

    channel = o["Name"]
    items = o["items"]

    for value in items:
        name = value["name"]
        desc = ""
        secs = value["duration"]

        date = value["datePublished"].strip()
        time = value["timePublished"].strip()

        length = secs

        path_id = value["pathID"]

        pid = utils.get_new_pid(db, None)
        p = raiplay.Program(grabber, down_type, channel, date, time, pid, length, name, desc, path_id)
        utils.add_to_db(db, p)


def process(grabber, progress, folder, down_type, f, db):
    o = json.load(f)

    blocks = o["Blocks"]

    for v1 in blocks:
        if "Sets" in v1:
            for v2 in v1["Sets"]:
                path = v2["url"]
                url = "http://www.raiplay.it/" + path

                filename = path.replace("/", "_")
                local_name = os.path.join(folder, filename + ".json")

                f = utils.download(grabber, progress, url, local_name, down_type, "utf-8", True)
                process_set(grabber, down_type, f, db)


def download(db, grabber, programma, down_type):
    progress = utils.get_progress()

    folder = config.raiplay_folder

    o = urllib.parse.urlparse(programma)
    filename = o.path.replace("/", "_")
    url = programma + "/?json"
    local_name = os.path.join(folder, filename + ".json")

    f = utils.download(grabber, progress, url, local_name, down_type, "utf-8", True)
    process(grabber, progress, folder, down_type, f, db)
