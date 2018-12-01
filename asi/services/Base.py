import os
import urllib

import asi.Utils
import asi.Cast
import asi.formats.H264
import asi.formats.M3U8
import logging


class Base:
    def __init__(self):
        self.pid = None
        self.title = None
        self.channel = None
        self.description = None
        self.grabber = None

        self.datetime = None

        self.length = None
        self.filename = None
        self.h264 = {}
        self.ts = None
        self.mms = None
        self.m3 = None
        self.canFollow = False

    def short(self, fmt):
        if self.datetime:
            ts = asi.Utils.str_date(self.datetime)
        else:
            ts = None

        str1 = fmt.format(self.pid, ts, self.channel, self.title)
        return str1

    def get_ts(self):
        return self.ts

    def get_h264(self):
        return self.h264

    def get_tablet_playlist(self):
        if self.m3:
            return self.m3

        ts = self.get_ts()
        if ts:
            try:
                self.m3 = asi.formats.M3U8.load_m3u8_from_url(self.grabber, ts)
            except urllib.error.HTTPError as e:
                logging.info('Exception: {0}'.format(e))
                pass

        return self.m3

    def cast(self, options):
        video_format, url = self.get_url_and_format(options)
        asi.Cast.cast_url(url)

    def show(self, options):
        video_format, url = self.get_url_and_format(options)
        print('Format: {}'.format(video_format))
        print('URL: {}'.format(url))

    def get_url_and_format(self, options):
        if not options.format:
            if self.get_h264():
                video_format = "h264"
            else:
                m3 = self.get_tablet_playlist()
                if m3:
                    video_format = "tsmp4"
                elif self.mms:
                    video_format = "mms"
        else:
            video_format = options.format

        if video_format == "h264":
            h264 = self.get_h264()
            url = asi.Utils.find_url_by_bandwidth(h264, options.bwidth)
        elif video_format in ["ts", "tsmp4"]:
            m3 = self.get_tablet_playlist()
            if not m3.is_variant:
                raise NotImplementedError
            playlist = asi.Utils.find_playlist(m3, options.bwidth)
            url = playlist.absolute_uri
        elif video_format == "mms":
            url = asi.Utils.get_mms_url(self.grabber, self.mms)

        return video_format, url

    def download(self, folder, options, grabber):
        if not os.path.exists(folder):
            os.makedirs(folder)

        video_format, url = self.get_url_and_format(options)
        logging.info('Video Format: {}'.format(video_format))
        logging.info('URL: {}'.format(url))

        if video_format == "h264":
            self.download_h264(folder, options, grabber, url)
        elif video_format == "ts":
            self.download_tablet(folder, options, grabber, url, False)
        elif video_format == "tsmp4":
            self.download_tablet(folder, options, grabber, url, True)
        elif video_format == "mms":
            self.download_mms(folder, options, grabber)

    def download_tablet(self, folder, options, grabber, url, remux):
        asi.formats.M3U8.download_m3u8(grabber, folder, url, options, self.pid, self.filename, self.title, remux)

    def download_h264(self, folder, options, grabber, url):
        asi.formats.H264.download_h264(self.grabber, grabber, folder, url, options, self.pid, self.filename, self.title)

    def download_mms(self, folder, options, url):
        try:
            import libmimms.core

            local_filename = os.path.join(folder, self.filename + ".wmv")

            if (not options.overwrite) and os.path.exists(local_filename):
                print("{0} already there as {1}".format(self.pid, local_filename))
                return

            opt = asi.Utils.Obj()
            opt.quiet = False
            opt.url = url
            opt.resume = False
            opt.bandwidth = 1e6
            opt.filename = local_filename
            opt.clobber = True
            opt.time = 0

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
            print("Date:", asi.Utils.str_date(self.datetime))
        if self.length:
            print("Length:", self.length)
        if self.filename:
            print("Filename:", self.filename)
        print()

        if self.canFollow:
            print("Follow: ENABLED")
            print()

        m3 = self.get_tablet_playlist()

        asi.formats.H264.display_h264(self.get_h264())
        if self.get_ts() or self.mms:
            if self.get_ts():
                print("ts:", self.get_ts())
            if self.mms:
                print("mms:", self.mms)
            print()

        asi.formats.M3U8.display_m3u8(m3)
