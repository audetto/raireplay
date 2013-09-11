import sys
import os.path
import urllib.parse
import m3u8
import codecs
import datetime
import unicodedata
import telnetlib
import subprocess
import io
import configparser
import socket
import re

from xml.etree import ElementTree

from asi import Meter
from asi import RAIUrls

class Obj:
    pass


# got from the iphone
# required for TF1 - www.wat.tv
userAgent = "AppleCoreMedia/1.0.0.9B206 (iPod; U; CPU OS 5_1_1 like Mac OS X; en_us)"
httpHeaders = {"User-Agent" : userAgent }


def httpFilename(url):
    name = os.path.basename(urllib.parse.urlsplit(url).path)
    return name


# simply download a file and saves it to localName
def downloadFile(grabber, progress, url, localName):
    try:
        if progress:
            progress.setName(localName)

        request = urllib.request.Request(url, headers = httpHeaders)
        with grabber.open(request) as response, open(localName, "wb") as f:
            # same length as shutil.copyfileobj

            # the rest is the same logic as urllib.request.urlretrieve
            # which unfortunately does not work with proxies
            blockSize = 1024 * 16
            size = -1

            headers = response.info()
            if "content-length" in headers:
                size = int(headers["Content-Length"])

            if progress:
                progress.start(size)

            while 1:
                buf = response.read(blockSize)
                if not buf:
                    break
                amountRead = len(buf)
                f.write(buf)
                if progress:
                    progress.update(amountRead)

            if progress:
                progress.done()
    except:
        print("Failed to download program file: {0}".format(url))
        raise


#def downloadFile(grabber, progress, url, localName):
#    if progress:
#        progress.setName(localName)
#    request = urllib.request.Request(url, headers = httpHeaders)
#
#    urllib.request.urlretrieve(url, filename = localName, reporthook = progress)
#    if progress:
#        progress.done()


# download a file and returns a file object
# with optional encoding, checking if it exists already...
def download(grabber, progress, url, localName, downType, encoding, checkTime = False):
    try:
        request = urllib.request.Request(url, headers = httpHeaders)

        if downType == "shm":
            f = grabber.open(request)
            if encoding:
                decoder = codecs.getreader(encoding)
                f = decoder(f)
            else:
                # make it seekable
                f = io.BytesIO(f.read())
        else:
            # here we need to download (maybe), copy local and open
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
                downloadFile(grabber, progress, url, localName)

            # now the file exists on the local filesystem
            if not encoding:
                f = open(localName, "rb")
            else:
                f = codecs.open(localName, "r", encoding = encoding)

        return f

    except:
        print("Failed to download data file: {0}".format(url))
        raise


def findPlaylist(m3, bandwidth):
    data = {}

    # bandwidth is alaways in Kb.
    # so we divide by 1000

    for p in m3.playlists:
        b = int(p.stream_info.bandwidth) // 1000
        data[b] = p

    opt = findUrlByBandwidth(data, bandwidth)

    return opt


def findUrlByBandwidth(data, bandwidth):
    if len(data) == 1:
        return next(iter(data.values()))

    if bandwidth == "high":
        b1 = sys.maxsize
    elif bandwidth == "low":
        b1 = 0
    else:
        b1 = int(bandwidth)

    opt = None
    dist = float('inf')

    for b2, v in data.items():
        d = abs(b2 - b1)
        if d < dist:
            dist = d
            opt = v

    return opt


def remuxToMP4(inFile, outFile):
    # -absf aac_adtstoasc
    # seems to be needed by ffmpeg (Fedora), not by avconv (Pi)
    cmdLine = ["ffmpeg", "-i", inFile, "-vcodec", "copy", "-acodec", "copy", "-absf", "aac_adtstoasc", "-y", outFile]
    code = subprocess.call(cmdLine)
    if code != 0:
        raise Exception("ffmpeg filed: exit code {0}".format(code))


def downloadM3U8(grabber, folder, m3, options, pid, filename, remux):
    if m3 and m3.is_variant:
        if remux:
            ext = ".mp4"
        else:
            ext = ".ts"

        localFilename   = os.path.join(folder, filename + ext)
        localFilenameTS = os.path.join(folder, filename + ".ts")

        if (not options.overwrite) and os.path.exists(localFilename):
            print()
            print("{0} already there as {1}".format(pid, localFilename))
            print()
            return

        playlist = findPlaylist(m3, options.bwidth)

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
            progress = getProgress(numberOfFiles, filename + ".ts")

            with open(localFilenameTS, "wb") as out:
                for seg in item.segments:
                    uri = seg.absolute_uri
                    with grabber.open(uri) as s:
                        b = s.read()
                        size = len(b)
                        if progress:
                            progress.start(size)
                        out.write(b)
                        if progress:
                            progress.update(size)

            if progress:
                progress.done()

            if remux:
                remuxToMP4(localFilenameTS, localFilename)
                os.remove(localFilenameTS)


            print()
            print("Saved {0} as {1}".format(pid, localFilename))
            print()

        except:
            print("Exception: removing {0}".format(localFilename))
            if os.path.exists(localFilename):
                os.remove(localFilename)
            if remux and os.path.exists(localFilenameTS):
                os.remove(localFilenameTS)
            raise


def downloadH264(grabber, folder, h264, options, pid, filename):
    localFilename = os.path.join(folder, filename + ".mp4")

    if (not options.overwrite) and os.path.exists(localFilename):
        print()
        print("{0} already there as {1}".format(pid, localFilename))
        print()
        return

    url = findUrlByBandwidth(h264, options.bwidth)

    print("Downloading:")
    print(url)

    print()
    print("Saving {0} as {1}".format(pid, localFilename))

    try:
        progress = getProgress()
        downloadFile(grabber, progress, url, localFilename)

        if os.path.getsize(localFilename) == len(RAIUrls.invalidMP4):
            raise Exception("{0} only available in Italy".format(url))

        print()
        print("Saved {0} as {1}".format(pid, filename))
        print()

    except:
        print("Exception: removing {0}".format(localFilename))
        if os.path.exists(localFilename):
            os.remove(localFilename)
        raise


# sometimes RAI sends invalid XML
# we get "reference to invalid character number"
def removeInvalidXMLCharacters(s):
    s = s.replace("&#0", "xx")
    s = s.replace("&#1", "xx")
    s = s.replace("&#22", "xx")
    return s


def removeAccents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    result = "".join([c for c in nkfd_form if not unicodedata.combining(c)])
    return result


def load_m3u8_from_url(grabber, uri):
    # here we need the global opener to be installed
    # as it is used internally by m3u8
    request = urllib.request.Request(uri, headers = httpHeaders)
    stream = grabber.open(request)

    return m3u8.load(uri, stream)


def setTorExitNodes(country, password):
    tn = telnetlib.Telnet("127.0.0.1", 9051)
    if not password:
        password = ""
    tn.write('AUTHENTICATE "{0}"\n'.format(password).encode("ascii"))
    tn.write("SETCONF ExitNodes={{{0}}}\n".format(country).encode("ascii"))
    tn.write("QUIT\n".encode("ascii"))
    tn.close()


def getTorExitNodes(password):
    try:
        tn = telnetlib.Telnet("127.0.0.1", 9051)
        if not password:
            password = ""
        tn.write('AUTHENTICATE "{0}"\n'.format(password).encode("ascii"))
        tn.read_until(b'\n')
        tn.write("GETCONF ExitNodes\n".encode("ascii"))
        res = tn.read_until(b'\n')
        tn.write("QUIT\n".encode("ascii"))
        tn.close()
        return res
    except socket.error:
        return None


def makeFilename(value):
    translateTo = "_"
    charactersToRemove = " /:^,|'"
    translateTable = dict((ord(char), translateTo) for char in charactersToRemove)
    name = value.translate(translateTable)
    name = removeAccents(name)
    name = re.sub("_+", "_", name)
    return name


def getResolution(p):
    if not p.stream_info.resolution:
        return None
    res = "{0:>4}x{1:>4}".format(p.stream_info.resolution[0], p.stream_info.resolution[1])
    return res


def displayM3U8(m3):
    if m3 and m3.is_variant:
        for playlist in m3.playlists:
            fmt = "\tProgram: {0:>2}, Bandwidth: {1:>10}, Resolution: {2:>10}, Codecs: {3}"

            # bandwidth is alaways in Kb.
            # so we divide by 1000

            line = fmt.format(playlist.stream_info.program_id, int(playlist.stream_info.bandwidth) // 1000,
                                 getResolution(playlist), playlist.stream_info.codecs)
            print(line)
        print()


def displayH264(h264):
    if h264:
        for k, v in h264.items():
            print("h264[{0}]: {1}".format(k, v))
        print()


def getProgress(numberOfFiles = 1, filename = None):
    # only use a progress meter if we are not redirected
    if sys.stdout.isatty():
        p = Meter.ReportHook(numberOfFiles)
        if filename:
            p.setName(filename)
        return p
    else:
        return None


def getNewPID(db, pid):
    # 0 is not a valid pid
    if not pid:
        pid = len(db) + 1

        # we only enforce uniqueness
        # if there is no real PID
        while str(pid) in db:
            pid = pid + 1

    pid = str(pid)

    return pid


def addToDB(db, prog):
    if not prog:
        return

    pid = prog.pid

    if pid in db:
        print("WARNING: duplicate pid {0}".format(prog.pid))

    db[pid] = prog


def getStringFromUrl(grabber, url):
    with grabber.open(url) as f:
        content = f.read().decode("ascii")
        return content


def strDate(date):
    s = date.strftime("%Y-%m-%d %H:%M")
    return s


def getMMSUrl(grabber, url):
    mms = None

    urlScheme = urllib.parse.urlsplit(url).scheme
    if urlScheme == "mms":
        # if it is already mms, don't look further
        mms = url
    else:
        # search for the mms url
        content = getStringFromUrl(grabber, url)

        if content == RAIUrls.invalidMP4:
            # is this the case of videos only available in Italy?
            mms = content
        else:
            root = ElementTree.fromstring(content)
            if root.tag == "ASX":
                asf = root.find("ENTRY").find("REF").attrib.get("HREF")

                if asf:
                    # use urlgrab to make it work with ConfigParser
                    content = getStringFromUrl(grabber, asf)
                    config = configparser.ConfigParser()
                    config.read_string(content)
                    mms = config.get("Reference", "ref1")
                    mms = mms.replace("http://", "mms://")
            elif root.tag == "playList":
                # adaptive streaming - unsupported
                pass
            else:
                print("Unknown root tag: " + root.tag)

    return mms
