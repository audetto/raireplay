from __future__ import print_function

import time

# super(Program, self).__init__()

class Base(object):
    def __init__(self):
        self.pid           = None
        self.title         = None
        self.channel       = None
        self.description   = None

        self.datetime      = None

        self.h264          = None
        self.ts            = None
        self.mms           = None


    def short(self, fmt):
        if self.datetime != None:
            ts = time.strftime("%Y-%m-%d %H:%M", self.datetime)
        else:
            ts = None

        str = fmt.format(self.pid, ts, self.title)
        return str
