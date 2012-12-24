from __future__ import print_function

import os.path
import urlparse
import m3u8
import codecs
import time
import unicodedata

from datetime import timedelta
from datetime import datetime

from asi import Meter

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


def findPlaylist(m3, bandwidth):
    b1 = int(bandwidth)
    for p in m3.playlists:
        b2 = int(p.stream_info.bandwidth)
        b2 = b2 / 1000 # remove rightmost 3 0s
        b2 = (b2 / 100) * 100 # round to lowest 100
        if b1 == b2:
            return p
    return None


def downloadM3U8(grabber, m3, bwidth, folder, pid, filename):
    if m3.is_variant:
        playlist = findPlaylist(m3, bwidth)

        if playlist == None:
            print("Cannot fin playlist with desired bandwidth")
            return

        uri = playlist.baseuri + "/" + playlist.uri
        item = m3u8.load(uri)
        if not m3.is_variant:
            print("m3u8 @ {0} is not a playlist".format(uri))
            return

        localFilename = os.path.join(folder, filename + ".ts")
        out = open(localFilename, "wb")

        print()
        print("Saving {0} as {1}".format(pid, localFilename))

        numberOfFiles = len(item.segments)
        progress = Meter.Meter(numberOfFiles, filename + ".ts")

        for seg in item.segments:
            uri = seg.baseuri + "/" + seg.uri
            s = grabber.urlread(uri, progress_obj = progress)
            out.write(s)

        print()
        print("Saved {0} as {1}".format(pid, localFilename))


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    result = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
    return result


# this is copied from M3U8 package
# as we want to ensure we use the grabber to download
# and we still get a good baseuri
def load_m3u8_from_url(grabber, uri):
    content = grabber.urlread(uri)
    parsed_url = urlparse.urlparse(uri)
    prefix = parsed_url.scheme + '://' + parsed_url.netloc
    basepath = os.path.normpath(parsed_url.path + '/..')
    baseuri = urlparse.urljoin(prefix, basepath)
    return m3u8.model.M3U8(content, baseuri=baseuri)
