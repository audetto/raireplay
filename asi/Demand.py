from __future__ import print_function

import json
import os.path

import urlgrabber.grabber
import urlgrabber.progress

from asi import Utils

url = "http://www.rai.tv/dl/RaiTV/programmi/ricerca/ContentSet-6445de64-d321-476c-a890-ae4ed32c729e-darivedere.html"
baseUrl = "http://www.rai.tv"

def process(f, db):
    o = json.load(f)

    pid = 0

    for v in o:
        p = Group(pid, v["title"], v["linkDemand"], v["date"])
        db[str(pid)] = p
        pid = pid + 1


def download(db, folder, type):
    page = Utils.httpFilename(url)

    g = urlgrabber.grabber.URLGrabber()

    localFilename = os.path.join(folder, page)
    f = Utils.download(g, url, localFilename, type, "raw-unicode-escape")

    process(f, db)


class Group:
    def __init__(self, pid, title, link, date):
        self.pid = pid
        self.title = title
        self.url = baseUrl + link
        self.datetime = float(date)


    def short(self):
        str = unicode("{0:>6}: {1}").format(self.pid, self.title)
        return str


    def display(self):
        width = urlgrabber.progress.terminal_width()

        print("=" * width)
        print("Title:", self.title)
        print("URL:", self.url)

        print()
