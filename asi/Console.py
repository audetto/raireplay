import sys

# Code from http://mail.python.org/pipermail/python-list/2000-May/033365.html
def terminal_width_linux(fd=1):
    """ Get the real terminal width """

    import fcntl
    import struct
    import termios

    try:
        buf = 'abcdefgh'
        buf = fcntl.ioctl(fd, termios.TIOCGWINSZ, buf)
        ret = struct.unpack('hhhh', buf)[1]
        if ret == 0:
            return 80
        # Add minimum too?
        return ret
    except: # IOError
        return 80

def terminal_width_native():
    import shutil

    size = shutil.get_terminal_size((80, 24))

    return size.columns

def terminal_width():
    ver = sys.version_info
    if ver >= (3, 3):
        return terminal_width_native()
    else:
        return terminal_width_linux()
