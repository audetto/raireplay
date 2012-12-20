from __future__ import print_function

import sys
sys.path.append('/home/andrea/projects/cvs/3rdParty/m3u8')

import os
import m3u8
import time
import json

from datetime import date
from datetime import timedelta

import urlgrabber.progress

from asi import Meter
from asi import Utils
from asi import Config

baseUrl = "http://medias2.francetv.fr/catchup-mobile"


def parseItem(prog):
    pid     = prog["id_diffusion"]
    date    = prog["date"]
    hour    = prog["heure"]
    url     = baseUrl +  prog["url_video"]
    desc    = prog["accroche"]
    channel = prog["chaine"]
    name    = prog["titre"]
    minutes = prog["duree"]

    p = Program( channel, date, hour, pid, minutes, name, desc, url)

    return p


def process(f, db):
    o = json.load(open(f))

    programmes = o["programmes"]

    for prog in programmes:
        p = parseItem(prog)
        db[p.pid] = p


class Program:
    def __init__(self, channel, date, hour, pid, minutes, name, desc, url):
        self.channel = channel
        self.pid = pid
        self.minutes = minutes
        self.name = name
        self.desc = desc
        self.url = url
        self.datetime = time.strptime(date + " " + hour, "%Y-%m-%d %H:%M")

        self.m3 = None


    def getTabletPlaylist(self):
        if self.m3 == None:
            self.m3 = m3u8.load(self.url)

        return self.m3


    def short(self):
        ts = time.strftime("%Y-%m-%d %H:%M", self.datetime)
        str = unicode("{0:>6}: {1} {2}").format(self.pid, ts, self.name)
        return str


    def display(self):
        width = urlgrabber.progress.terminal_width()

        print("=" * width)
        print("Channel:", self.channel)
        print("PID:", self.pid)
        print("Title:", self.name)
        print("Description:", self.desc)
        print("Date:", time.strftime("%Y-%m-%d %H:%M", self.datetime))
        print("Length:", self.minutes, "minutes")
        print()
        print("url:", self.url)

        m3 = self.getTabletPlaylist()

        if m3 != None and m3.is_variant:
            print()
            for playlist in m3.playlists:
                format = "\tProgram: {0:>2}, Bandwidth: {1:>10}, Codecs: {2}"
                line = format.format(playlist.stream_info.program_id, playlist.stream_info.bandwidth, playlist.stream_info.codecs)
                print(line)
            print()


    def download(self, grabber, folder, format):
        if not os.path.exists(folder):
            os.makedirs(folder)

        m3 = self.getTabletPlaylist()
        Utils.downloadM3U8(grabber, m3, folder, self.pid, "xxx")
