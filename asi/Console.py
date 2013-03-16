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
    except: # IOError
        return 80
