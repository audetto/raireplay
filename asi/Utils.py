import os.path
import urlparse
import codecs
import time

from datetime import timedelta
from datetime import datetime

class Obj:
    pass

baseUrl = "http://www.rai.tv"


def httpFilename(url):
    name = os.path.split(urlparse.urlsplit(url).path)[1]
    return name


def download(grabber, progress, url, localName, downType, encoding, checkTime = False):
    exists = os.path.exists(localName)
    exists = exists and os.path.getsize(localName) > 0

    if downType == "never" and not exists:
        raise Exception("Will not download missing file: {0} -> {1}".format(url, localName))

    if exists and checkTime:
        # if it is more than a day old, we redownload it
        age = datetime.today() - datetime.fromtimestamp(os.path.getmtime(localName))
        maximum = timedelta(days = 1)
        exists = age < maximum

    if downType == "always" or (downType == "update" and not exists):
        localName = grabber.urlgrab(url, filename = localName, progress_obj = progress)

    if encoding == None:
        f = open(localName, "r")
    else:
        f = codecs.open(localName, "r", encoding = encoding)

    return f


def getWebFromID(id):
    web = "/dl/RaiTV/programmi/media/{0}.html".format(id)
    return web
