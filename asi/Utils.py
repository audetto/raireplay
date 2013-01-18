from __future__ import print_function

import sys
import os.path
import urlparse
import m3u8
import codecs
import datetime
import unicodedata
import telnetlib
import urlgrabber.progress

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
        age = datetime.datetime.today() - datetime.datetime.fromtimestamp(os.path.getmtime(localName))
        maximum = datetime.timedelta(days = 1)
        exists = age < maximum

    if downType == "always" or (downType == "update" and not exists):
        localName = grabber.urlgrab(str(url), filename = localName, progress_obj = progress)

    if encoding == None:
        f = open(localName, "r")
    else:
        f = codecs.open(localName, "r", encoding = encoding)

    return f


def getWebFromID(id):
    web = "/dl/RaiTV/programmi/media/{0}.html".format(id)
    return web


def findPlaylist(m3, bandwidth):
    if len(m3.playlists) == 1:
        return m3.playlists[0]

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


def downloadM3U8(grabber, folder, m3, bwidth, overwrite, quiet, pid, filename):
    if m3 != None and m3.is_variant:
        localFilename = os.path.join(folder, filename + ".ts")

        if (not overwrite) and os.path.exists(localFilename):
            print()
            print("{0} already there as {1}".format(pid, localFilename))
            print()
            return

        playlist = findPlaylist(m3, bwidth)

        print("Downloading:")
        print(playlist)

        uri = playlist.absolute_uri
        item = load_m3u8_from_url(grabber, uri)
        if not m3.is_variant:
            print("m3u8 @ {0} is not a playlist".format(uri))
            return

        print()
        print("Saving {0} as {1}".format(pid, localFilename))

        try:
            numberOfFiles = len(item.segments)
            progress = None
            if not quiet:
                progress = Meter.Meter(numberOfFiles, filename + ".ts")

            out = open(localFilename, "wb")
            for seg in item.segments:
                uri = seg.absolute_uri
                s = grabber.urlread(uri, progress_obj = progress)
                out.write(s)

            print()
            print("Saved {0} as {1}".format(pid, localFilename))
            print()

        except:
            print("Exception: removing {0}".format(localFilename))
            if os.path.exists(localFilename):
                os.remove(localFilename)


def downloadH264(grabber, folder, url, overwrite, quiet, pid, filename):
    localFilename = os.path.join(folder, filename + ".mp4")

    if (not overwrite) and os.path.exists(localFilename):
        print()
        print("{0} already there as {1}".format(pid, localFilename))
        print()
        return

    progress_obj = None
    if not quiet:
        progress_obj = urlgrabber.progress.TextMeter()

    print()
    print("Saving {0} as {1}".format(pid, localFilename))

    try:
        filename = grabber.urlgrab(str(url), filename = localFilename, progress_obj = progress_obj)

        print()
        print("Saved {0} as {1}".format(pid, filename))
        print()

    except:
        print("Exception: removing {0}".format(localFilename))
        if os.path.exists(localFilename):
            os.remove(localFilename)
        raise

def removeAccents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    result = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
    return result


# this is copied from M3U8 package
# as we want to ensure we use the grabber to download
# and we still get a good baseuri
def load_m3u8_from_url(grabber, uri):
    content = grabber.urlread(str(uri))
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
