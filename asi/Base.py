import os
import urllib

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
        self.h264          = {}
        self.ts            = None
        self.mms           = None
        self.m3            = None


    def short(self, fmt):
        if self.datetime:
            ts = Utils.strDate(self.datetime)
        else:
            ts = None

        str1 = fmt.format(self.pid, ts, self.title)
        return str1


    def getTabletPlaylist(self):
        try:
            if (not self.m3) and self.ts:
                self.m3 = Utils.load_m3u8_from_url(self.grabber, self.ts)
        except urllib.error.HTTPError:
            pass

        return self.m3


    def download(self, folder, options):
        if not os.path.exists(folder):
            os.makedirs(folder)

        if options.format == "h264":
            self.downloadH264(folder, options)
        elif options.format == "ts":
            self.downloadTablet(folder, options, False)
        elif options.format == "tsmp4":
            self.downloadTablet(folder, options, True)
        elif options.format == "mms":
            self.downloadMMS(folder, options)
        elif not options.format:
            if self.h264:
                self.downloadH264(folder, options)
            else:
                m3 = self.getTabletPlaylist()
                if m3:
                    self.downloadTablet(folder, options, True)
                elif self.mms:
                    self.downloadMMS(folder, options)


    def downloadTablet(self, folder, options, remux):
        m3 = self.getTabletPlaylist()
        Utils.downloadM3U8(self.grabber, folder, m3, options, self.pid, self.filename, remux)


    def downloadH264(self, folder, options):
        Utils.downloadH264(self.grabber, folder, self.h264, options, self.pid, self.filename)


    def downloadMMS(self, folder, options):
        mms = Utils.getMMSUrl(self.grabber, self.mms)

        try:
            import libmimms.core

            localFilename = os.path.join(folder, self.filename + ".wmv")

            if (not options.overwrite) and os.path.exists(localFilename):
                print("{0} already there as {1}".format(self.pid, localFilename))
                return

            opt = Utils.Obj()
            opt.quiet        = False
            opt.url          = mms
            opt.resume       = False
            opt.bandwidth    = 1e6
            opt.filename     = localFilename
            opt.clobber      = True
            opt.time         = 0

            libmimms.core.download(opt)

        except ImportError as e:
            print("\nMissing libmimms.\nCannot downalod: {0}.".format(mms))


    def display(self, width):
        Utils.displayH264(self.h264)
        if self.ts:
            print("ts:  ", self.ts)
        if self.mms:
            print("mms: ", self.mms)
        print()

        m3 = self.getTabletPlaylist()
        Utils.displayM3U8(m3)
