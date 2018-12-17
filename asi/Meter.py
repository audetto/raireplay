import time
import os

from asi import Console


def format_time(seconds, use_hours=0):
    if seconds is None or seconds < 0:
        if use_hours:
            return '--:--:--'
        else:
            return '--:--'
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


def format_number(number, si=False, space=' '):
    """Turn numbers into human-readable metric-like numbers"""
    symbols = ['',  # (none)
               'k',  # kilo
               'M',  # mega
               'G',  # giga
               'T',  # tera
               'P',  # peta
               'E',  # exa
               'Z',  # zetta
               'Y']  # yotta

    if si:
        step = 1000.0
    else:
        step = 1024.0

    thresh = 999
    depth = 0
    max_depth = len(symbols) - 1

    # we want numbers between 0 and thresh, but don't exceed the length
    # of our list.  In that event, the formatting will be screwed up,
    # but it'll still show the right number.
    while number > thresh and depth < max_depth:
        depth = depth + 1
        number = number / step

    if isinstance(number, int):
        # it's an int or a long, which means it didn't get divided,
        # which means it's already short enough
        fmt = '%i%s%s'
    elif number < 9.95:
        # must use 9.95 for proper sizing.  For example, 9.99 will be
        # rounded to 10.0 with the .1f format string (which is too long)
        fmt = '%.1f%s%s'
    else:
        fmt = '%.0f%s%s'

    return fmt % (float(number or 0), space, symbols[depth])


class ReportHook:

    def __init__(self, number_of_files=1):
        self.name = None
        self.start_time = None
        self.files_read = None
        self.total_size_so_far = None
        self.read_so_far = None
        self.estimated_size = None

        self.numberOfFiles = number_of_files
        self.reset()

    def reset(self):
        self.start_time = None
        self.files_read = 0
        self.total_size_so_far = 0
        self.read_so_far = 0
        self.estimated_size = None

    def set_name(self, name):
        self.name = os.path.basename(name)
        self.reset()

    def start(self, total_size):
        if not self.start_time:
            self.start_time = time.time()
        self.total_size_so_far = self.total_size_so_far + total_size
        self.files_read = self.files_read + 1
        self.estimated_size = self.total_size_so_far / self.files_read * self.numberOfFiles
        return

    def update(self, amount_read):
        if not self.start_time:
            self.reset()
        else:
            current_time = time.time()
            elapsed_time = current_time - self.start_time

            self.read_so_far = self.read_so_far + amount_read

            if elapsed_time > 0:
                speed = self.read_so_far / elapsed_time
            else:
                speed = float("inf")

            terminal_width = Console.terminal_width()

            name_width = terminal_width - 33

            status = "{0:{name_width}}: {1:>6}B {2:>6}B/s".format(self.name[:name_width], format_number(self.read_so_far),
                                                                  format_number(speed), name_width=name_width)

            if self.estimated_size > 0:
                self.read_so_far = min(self.estimated_size, self.read_so_far)
                pct = self.read_so_far / self.estimated_size
                time_to_go = elapsed_time * (1 - pct) / pct
                output = " {0:4.0%} {1:>6}".format(pct, format_time(time_to_go))
                status = status + output

            print("\r", status, end="")

    def done(self):
        print()
