import os
import m3u8

from raireplay.services import base


def process(grabber, filename, pid):
    p = Program(grabber, filename, pid)
    return p


class Program(base.Base):
    def __init__(self, grabber, filename, pid):
        super().__init__()

        self.pid = pid
        self.title = filename

        self.grabber = grabber
        self.filename = os.path.basename(filename)

        self.m3 = m3u8.load(filename)
        self.channel = "m3u8"
