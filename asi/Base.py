import os
import urllib

import asi.Utils
import asi.formats.H264
import asi.formats.M3U8


class Base(object):
    def __init__(self):
        self.pid           = None
        self.title         = None
        self.channel       = None
        self.description   = None
        self.grabber       = None

        self.datetime      = None

        self.length        = None
        self.filename      = None
        self.h264          = {}
        self.ts            = None
        self.mms           = None
        self.m3            = None
        self.canFollow     = False


    def short(self, fmt):
        if self.datetime:
            ts = asi.Utils.strDate(self.datetime)
        else:
            ts = None

        str1 = fmt.format(self.pid, ts, self.channel, self.title)
        return str1


    def getTS(self):
        return self.ts


    def getH264(self):
        return self.h264


    def getTabletPlaylist(self):
        if self.m3:
            return self.m3

        ts = self.getTS()
        if ts:
            try:
                self.m3 = asi.formats.M3U8.load_m3u8_from_url(self.grabber, ts)
            except urllib.error.HTTPError:
                pass

        return self.m3


    def download(self, folder, options, grabber):
        if not os.path.exists(folder):
            os.makedirs(folder)

        if options.format == "h264":
            self.downloadH264(folder, options, grabber)
        elif options.format == "ts":
            self.downloadTablet(folder, options, grabber, False)
        elif options.format == "tsmp4":
            self.downloadTablet(folder, options, grabber, True)
        elif options.format == "mms":
            self.downloadMMS(folder, options, grabber)
        elif not options.format:
            if self.getH264():
                self.downloadH264(folder, options, grabber)
            else:
                m3 = self.getTabletPlaylist()
                if m3:
                    self.downloadTablet(folder, options, grabber, True)
                elif self.mms:
                    self.downloadMMS(folder, options, grabber)


    def downloadTablet(self, folder, options, grabber, remux):
        m3 = self.getTabletPlaylist()
        asi.formats.M3U8.downloadM3U8(self.grabber, grabber, folder, m3, options, self.pid, self.filename, self.title, remux)


    def downloadH264(self, folder, options, grabber):
        asi.formats.H264.downloadH264(self.grabber, grabber, folder, self.getH264(), options, self.pid, self.filename, self.title)


    def downloadMMS(self, folder, options, grabber):
        mms = asi.Utils.getMMSUrl(self.grabber, self.mms)

        try:
            import libmimms.core

            localFilename = os.path.join(folder, self.filename + ".wmv")

            if (not options.overwrite) and os.path.exists(localFilename):
                print("{0} already there as {1}".format(self.pid, localFilename))
                return

            opt = asi.Utils.Obj()
            opt.quiet        = False
            opt.url          = mms
            opt.resume       = False
            opt.bandwidth    = 1e6
            opt.filename     = localFilename
            opt.clobber      = True
            opt.time         = 0

            libmimms.core.download(opt)

        except ImportError:
            print("\nMissing libmimms.\nCannot download: {0}.".format(mms))


    def display(self, width):
        print("=" * width)
        print("PID:", self.pid)
        print("Channel:", self.channel)
        print("Title:", self.title)
        if self.description:
            print("Description:", self.description)
        if self.datetime:
            print("Date:", asi.Utils.strDate(self.datetime))
        if self.length:
            print("Length:", self.length)
        if self.filename:
            print("Filename:", self.filename)
        print()

        if self.canFollow:
            print("Follow: ENABLED")
            print()

        m3 = self.getTabletPlaylist()

        asi.formats.H264.displayH264(self.getH264())
        if self.getTS() or self.mms:
            if self.getTS():
                print("ts:", self.getTS())
            if self.mms:
                print("mms:", self.mms)
            print()

        asi.formats.M3U8.displayM3U8(m3)
