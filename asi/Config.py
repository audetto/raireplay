import os.path
import os

rootFolder    = os.path.expanduser("~/.raireplay")
dataFolder    = os.path.join(rootFolder, "data")

replayFolder  = os.path.join(dataFolder, "replay")
itemFolder    = os.path.join(dataFolder, "items")
pageFolder    = os.path.join(dataFolder, "pages")
demandFolder  = os.path.join(dataFolder, "demand")

programFolder = os.path.join(rootFolder, "programs")

if not os.path.exists(replayFolder):
    os.makedirs(replayFolder)

if not os.path.exists(itemFolder):
    os.makedirs(itemFolder)

if not os.path.exists(pageFolder):
    os.makedirs(pageFolder)

if not os.path.exists(demandFolder):
    os.makedirs(demandFolder)

if not os.path.exists(programFolder):
    os.makedirs(programFolder)
