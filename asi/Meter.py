import time
import os
import fcntl
import struct
import termios

# Code from http://mail.python.org/pipermail/python-list/2000-May/033365.html
def terminal_width(fd=1):
    """ Get the real terminal width """
    try:
        buf = 'abcdefgh'
        buf = fcntl.ioctl(fd, termios.TIOCGWINSZ, buf)
        ret = struct.unpack('hhhh', buf)[1]
        if ret == 0:
            return 80
        # Add minimum too?
        return ret
    except:
        return 80

def format_time(seconds, use_hours=0):
    if seconds is None or seconds < 0:
        if use_hours: return '--:--:--'
        else:         return '--:--'
    elif seconds == float('inf'):
        return 'Infinite'
    else:
        seconds = int(seconds)
        minutes = seconds / 60
        seconds = seconds % 60
        if use_hours:
            hours = minutes / 60
            minutes = minutes % 60
            return '%02i:%02i:%02i' % (hours, minutes, seconds)
        else:
            return '%02i:%02i' % (minutes, seconds)


def format_number(number, SI=0, space=' '):
    """Turn numbers into human-readable metric-like numbers"""
    symbols = ['',  # (none)
               'k', # kilo
               'M', # mega
               'G', # giga
               'T', # tera
               'P', # peta
               'E', # exa
               'Z', # zetta
               'Y'] # yotta

    if SI: step = 1000.0
    else: step = 1024.0

    thresh = 999
    depth = 0
    max_depth = len(symbols) - 1

    # we want numbers between 0 and thresh, but don't exceed the length
    # of our list.  In that event, the formatting will be screwed up,
    # but it'll still show the right number.
    while number > thresh and depth < max_depth:
        depth  = depth + 1
        number = number / step

    if isinstance(number, int):
        # it's an int or a long, which means it didn't get divided,
        # which means it's already short enough
        format = '%i%s%s'
    elif number < 9.95:
        # must use 9.95 for proper sizing.  For example, 9.99 will be
        # rounded to 10.0 with the .1f format string (which is too long)
        format = '%.1f%s%s'
    else:
        format = '%.0f%s%s'

    return(format % (float(number or 0), space, symbols[depth]))


class ReportHook():

    def __init__(self, numberOfFiles = 1):
        self.name = None
        self.numberOfFiles = numberOfFiles
        self.reset()


    def reset(self):
        self.startTime = None
        self.filesRead = 0
        self.totalSizeSoFar = 0
        self.readSoFar = 0
        self.estimatedSize = None


    def setName(self, name):
        self.name = os.path.basename(name)
        self.reset()


    def __call__(self, blockCount, blockSize, totalSize):
        if blockCount == 0:
            if not self.startTime:
                self.startTime = time.time()
            self.totalSizeSoFar = self.totalSizeSoFar + totalSize
            self.filesRead      = self.filesRead + 1
            self.estimatedSize  = self.totalSizeSoFar / self.filesRead * self.numberOfFiles
            return

        currentTime = time.time()
        elapsedTime = currentTime - self.startTime

        self.readSoFar = self.readSoFar + blockSize

        terminalWidth = terminal_width()

        nameWidth = terminalWidth - 28

        output = "\r{0:{nameWidth}}: {1:>6} {2:>6}".format(self.name[:nameWidth], format_number(self.readSoFar), format_time(elapsedTime), nameWidth = nameWidth)
        print(output, end = "")

        if self.estimatedSize > 0:
            self.readSoFar = min(self.estimatedSize, self.readSoFar)
            pct = self.readSoFar / self.estimatedSize
            timeToGo = elapsedTime * (1 - pct) / pct
            output = " {0:4.0%} {1:>6}".format(pct, format_time(timeToGo))
            print(output, end = "")

        print("\r", end = "")


    def done(self):
        print()
