import os
import m3u8

from asi import Base


def process(grabber, filename, pid):
    p = Program(grabber, filename, pid)
    return p


class Program(Base.Base):
    def __init__(self, grabber, filename, pid):
        super(Program, self).__init__()

        self.pid = pid
        self.title = filename

        self.grabber = grabber
        self.filename = os.path.basename(filename)

        self.m3 = m3u8.load(filename)
