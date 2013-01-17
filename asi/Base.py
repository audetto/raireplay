from __future__ import print_function

import datetime
import os
import libmimms.core

from asi import Utils

# super(Program, self).__init__()

class Base(object):
    def __init__(self):
        self.pid           = None
        self.title         = None
        self.channel       = None
        self.description   = None
        self.grabber       = None

        self.datetime      = None

        self.filename      = None
        self.h264          = None
        self.ts            = None
        self.mms           = None
        self.m3            = None


    def short(self, fmt):
        if self.datetime != None:
            ts = self.datetime.strftime("%Y-%m-%d %H:%M")
        else:
            ts = None

        str = fmt.format(self.pid, ts, self.title)
        return str


    def getTabletPlaylist(self):
        if self.m3 == None and self.ts:
            self.m3 = Utils.load_m3u8_from_url(self.grabber, self.ts)

        return self.m3


    def download(self, folder, format, bwidth, overwrite):
        if not os.path.exists(folder):
            os.makedirs(folder)

        if format == "h264":
            self.downloadH264(folder, overwrite)
        elif format == "ts":
            self.downloadTablet(folder, bwidth, overwrite)
        elif format == "mms":
            self.downloadMMS(folder, overwrite)
        elif format == None:
            if self.h264 != None:
                self.downloadH264(folder, overwrite)
            else:
                m3 = self.getTabletPlaylist()
                if m3 != None:
                    self.downloadTablet(folder, bwidth, overwrite)
                elif self.mms != None:
                    self.downloadMMS(folder, overwrite)


    def downloadTablet(self, folder, bwidth, overwrite):
        m3 = self.getTabletPlaylist()
        Utils.downloadM3U8(self.grabber, folder, m3, bwidth, overwrite, self.pid, self.filename)


    def downloadH264(self, folder, overwrite):
        Utils.downloadH264(self.grabber, folder, self.h264, overwrite, self.pid, self.filename)


    def downloadMMS(self, folder):
        localFilename = os.path.join(folder, self.filename + ".wmv")

        if (not overwrite) and os.path.exists(localFilename):
            print("{0} already there as {1}".format(self.pid, localFilename))
            return

        options = Utils.Obj()
        options.quiet        = False
        options.url          = self.mms
        options.resume       = False
        options.bandwidth    = 1e6
        options.filename     = localFilename
        options.clobber      = True
        options.time         = 0

        libmimms.core.download(options)
