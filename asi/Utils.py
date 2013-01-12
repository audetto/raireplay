from __future__ import print_function

import sys
sys.path.append('/home/andrea/projects/cvs/3rdParty/m3u8')

import os.path
import urlparse
import m3u8
import codecs
import time
import unicodedata
import telnetlib
import urlgrabber.progress

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

    opt = None
    dist = sys.maxint

    for p in m3.playlists:
        b2 = int(p.stream_info.bandwidth)
        d = abs(b2 - b1)
        if d < dist:
            dist = d
            opt = p

    return opt


def downloadM3U8(grabber, m3, bwidth, folder, pid, filename):
    if m3.is_variant:
        playlist = findPlaylist(m3, bwidth)

        print("Downloading:")
        print(playlist)

        uri = playlist.absolute_uri
        item = load_m3u8_from_url(grabber, uri)
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
            uri = seg.absolute_uri
            s = grabber.urlread(uri, progress_obj = progress)
            out.write(s)

        print()
        print("Saved {0} as {1}".format(pid, localFilename))


def downloadH264(grabber, folder, pid, url, filename):
    progress_obj = urlgrabber.progress.TextMeter()
    localFilename = os.path.join(folder, filename + ".mp4")

    print()
    print("Saving {0} as {1}".format(pid, localFilename))

    filename = grabber.urlgrab(url, filename = localFilename, progress_obj = progress_obj)

    print()
    print("Saved {0} as {1}".format(pid, filename))


def removeAccents(input_str):
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


def setTorExitNodes(country):
    tn = telnetlib.Telnet("127.0.0.1", 9051)
    tn.write('AUTHENTICATE "portachiusa"\n')
    tn.write("SETCONF ExitNodes={{{0}}}\n".format(country))
    tn.write("QUIT\n")


def makeFilename(input):
    translateTo = u"_"
    charactersToRemove = u" /:^,|"
    translateTable = dict((ord(char), translateTo) for char in charactersToRemove)
    name = input.translate(translateTable)
    name = removeAccents(name)
    return name


def getResolution(p):
    if p.stream_info.resolution == None:
        return None
    res = "{0:>4}x{1:>4}".format(p.stream_info.resolution[0], p.stream_info.resolution[1])
    return res


def displayM3U8(m3):
    if m3 != None and m3.is_variant:
        print()
        for playlist in m3.playlists:
            format = "\tProgram: {0:>2}, Bandwidth: {1:>10}, Resolution: {2:>10}, Codecs: {3}"

            line = format.format(playlist.stream_info.program_id, playlist.stream_info.bandwidth,
                                 getResolution(playlist), playlist.stream_info.codecs)
            print(line)
        print()
