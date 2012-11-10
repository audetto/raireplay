import os.path
import urlparse
import codecs


class Obj:
    pass


def httpFilename(url):
    name = os.path.split(urlparse.urlsplit(url).path)[1]
    return name

def download(grabber, progress, url, localName, type, encoding):
    exists = os.path.exists(localName)

    if type == "never" and not exists:
        raise Exception("Will not download missing file: {0} -> {1}".format(url, localName))

    if type == "always" or (type == "update" and not os.path.exists(localName)):
        localName = grabber.urlgrab(url, filename = localName, progress_obj = progress)

    if encoding == None:
        f = open(localName, "r")
    else:
        f = codecs.open(localName, "r", encoding = encoding)

    return f
