import os.path
import urlparse
import codecs
import urlgrabber.grabber


class Obj:
    pass


def httpFilename(url):
    name = os.path.split(urlparse.urlsplit(url).path)[1]
    return name

def download(grabber, url, localName, type, encoding):
    exists = os.path.exists(localName)

    if type == "never" and not exists:
        raise Exception("Will not download missing file: {0} -> {1}".format(url, localName))

    if type == "always" or (type == "update" and not os.path.exists(localName)):
        localName = grabber.urlgrab(url, filename = localName)

    if encoding == None:
        f = open(localName, "r")
    else:
        f = codecs.open(localName, "r", encoding = encoding)

    return f
