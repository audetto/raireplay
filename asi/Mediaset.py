import os
import json

from xml.etree import ElementTree

from asi import Utils
from asi import Config

configUrl = "http://app.mediaset.it/app/videomediaset/iPhone/2.0.2/videomediaset_iphone_config.plist"

def parseConfig(root):
    dic = root.find("dict")

    result = {}

    process = False
    for n in dic.iter():
        if n.tag == "key" and n.text == "Configuration":
            process = True
        elif n.tag == "dict" and process:
            process = False
            for nn in n.iter():
                if nn.tag == "key":
                    name = nn.text
                elif nn.tag == "string":
                    result[name] = nn.text
            
    return result


def processGroup(grabber, f, folder, progress, downType, db):
    o = json.load(f)

    for a in o["programmi"]["programma"]:
        print(a["brand"]["value"], a["urlxml"])


def downloadGroup(grabber, url, folder, progress, downType, db):
    name = Utils.httpFilename(url)
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress, url, localName, downType, "utf-8", True)

    processGroup(grabber, f, folder, progress, downType, db)


def download(db, grabber, downType):
    progress = Utils.getProgress()
    name = Utils.httpFilename(configUrl)

    folder = Config.mediasetFolder
    localName = os.path.join(folder, name)

    f = Utils.download(grabber, progress, configUrl, localName, downType, None, True)
    s = f.read().strip()
    root = ElementTree.fromstring(s)
    conf = parseConfig(root)

    programs = conf["ProgramListRequestUrl"]
    downloadGroup(grabber, programs, folder, progress, downType, db)
