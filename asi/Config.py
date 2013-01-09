import os.path
import os

rootFolder    = os.path.expanduser("~/.raireplay")
dataFolder    = os.path.join(rootFolder, "data")

replayFolder  = os.path.join(dataFolder, "replay")
itemFolder    = os.path.join(dataFolder, "items")
pageFolder    = os.path.join(dataFolder, "pages")
demandFolder  = os.path.join(dataFolder, "demand")
pluzzFolder   = os.path.join(dataFolder, "pluzz")
tf1Folder     = os.path.join(dataFolder, "tf1")

programFolder = os.path.join(rootFolder, "programs")

if not os.path.exists(replayFolder):
    os.makedirs(replayFolder)

if not os.path.exists(itemFolder):
    os.makedirs(itemFolder)

if not os.path.exists(pageFolder):
    os.makedirs(pageFolder)

if not os.path.exists(demandFolder):
    os.makedirs(demandFolder)

if not os.path.exists(pluzzFolder):
    os.makedirs(pluzzFolder)

if not os.path.exists(tf1Folder):
    os.makedirs(tf1Folder)

if not os.path.exists(programFolder):
    os.makedirs(programFolder)
