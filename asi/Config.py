import os.path
import os

def createFolder(name):
    if not os.path.exists(name):
        os.makedirs(name)
    return name

rootFolder    = createFolder(os.path.expanduser("~/.raireplay"))
dataFolder    = createFolder(os.path.join(rootFolder, "data"))

replayFolder  = createFolder(os.path.join(dataFolder, "replay"))
itemFolder    = createFolder(os.path.join(dataFolder, "items"))
pageFolder    = createFolder(os.path.join(dataFolder, "pages"))
demandFolder  = createFolder(os.path.join(dataFolder, "demand"))
tgFolder      = createFolder(os.path.join(dataFolder, "tg"))
pluzzFolder   = createFolder(os.path.join(dataFolder, "pluzz"))
tf1Folder     = createFolder(os.path.join(dataFolder, "tf1"))

programFolder = createFolder(os.path.join(rootFolder, "programs"))
