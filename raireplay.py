#! /usr/bin/python

from __future__ import print_function

import sys
import codecs
import argparse

from asi import Program
from asi import Demand
from asi import Config


def main():

    parser = argparse.ArgumentParser(description = "Rai Replay")
    parser.add_argument("--download", action = "store", default = "update", choices = ["always", "update", "never"],
                        help = "Default is update")
    parser.add_argument("--list", action = "store_true", default = False)
    parser.add_argument("--get", action = "store_true", default = False)
    parser.add_argument("--format", action = "store", choices = ["h264", "ts"])
    parser.add_argument("--url", action = "store", help = "RAI On Demand")
    parser.add_argument("pid", nargs = "*")

    args = parser.parse_args()

    db = {}
    Program.download(db, Config.replayFolder, args.download)

    if args.list:
        Program.list(db)

    if len(args.pid) > 0:
        for pid in args.pid:
            if pid in db:
                p = db[pid]
                Program.display(p)
                if args.get:
                    p.download(Config.programFolder, args.format)
            else:
                print("PID {0} not found".format(pid))
    elif args.url != None:
        d = Demand.Demand(args.url, Config.urlFolder, args.download)
        d.display()
    else:
        print()
        print("INFO: {0} programmes found".format(len(db)))

    print()

# is this required??? seems a bit of pythonic nonsense
# all RAI html is encoded in "latin1" (decoded as we read)
#
# and it seems that redirecting the output requires a "latin1" terminal
# done here

sys.stdout = codecs.getwriter("latin1")(sys.stdout)
main()
