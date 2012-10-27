from __future__ import print_function

import time

import urlgrabber.progress

# progress class for URLgrabber
# that "concatenates" many files.
# we want to have a global progress constrained by:
# we know the number of files
# we do not know the total size
# we estimate the size based on the previous files
# assuming they are about the same lenght

class Meter(urlgrabber.progress.TextMeter):
    def __init__(self, numberOfFiles, name):
        urlgrabber.progress.TextMeter.__init__(self)
        self.numberOfFiles = numberOfFiles
        self.name = name

        self.bytesSoFar = 0
        self.filesSoFar = 0
        self.now = None

    def addFile(self, size, now):
        self.baseRead   = self.bytesSoFar
        self.bytesSoFar = self.bytesSoFar + size
        self.filesSoFar = self.filesSoFar + 1

        # assume following files have same average length as past
        estimatedTotal = self.bytesSoFar / self.filesSoFar * self.numberOfFiles

        if self.now == None:
            self.now == now

        if self.now == None:
            self.now == time.time()

        return estimatedTotal

    def start(self, filename = None, url = None, basename = None, size = None, now = None, text = None):
        estimatedTotal = self.addFile(size, now)
        if self.filesSoFar == 1:
            urlgrabber.progress.TextMeter.start(self, filename, url, basename, estimatedTotal, self.now, self.name)
        else:
            # update total
            # a bit of a hack. Copied from URLGrabber source code
            self.size = estimatedTotal
            self.fsize = urlgrabber.progress.format_number(estimatedTotal) + 'B'
            self.re.total = estimatedTotal

    def end(self, amount_read, now = None):
        # otherwise we get a new line after each file
        if self.filesSoFar == self.numberOfFiles:
            totalRead = self.baseRead + amount_read
            urlgrabber.progress.TextMeter.end(self, totalRead, now)

    def update(self, amount_read, now = None):
        totalRead = self.baseRead + amount_read
        urlgrabber.progress.TextMeter.update(self, totalRead, now)
