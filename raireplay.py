#! /usr/bin/python



import sys
import codecs
import argparse

import Driver

def main():

    parser = argparse.ArgumentParser(description = "Rai Replay", fromfile_prefix_chars = "@")

    parser.add_argument("--download", action = "store", default = "update", choices = ["always", "update", "never", "shm"],
                        help = "Default is update")
    parser.add_argument("--format", action = "store", choices = ["h264", "ts", "tsmp4", "mms"])
    parser.add_argument("--bwidth", action = "store")
    parser.add_argument("--ip", action = "store_true", default = False)
    parser.add_argument("--tor", action = "store")
    parser.add_argument("--tor-pass", action = "store")
    parser.add_argument("--proxy", action = "store")
    parser.add_argument("--overwrite", action = "store_true", default = False)
    parser.add_argument("--location", action = "store", help = "path where to download programs")

    parser.add_argument("--page",   action = "store", help = "RAI On Demand Page")
    parser.add_argument("--replay", action = "store_true", default = False, help = "RAI Replay")
    parser.add_argument("--ondemand", action = "store_true", default = False, help = "RAI On Demand List")
    parser.add_argument("--tg", action = "store_true", default = False, help = "Telegiornali RAI")
    parser.add_argument("--junior", action = "store_true", default = False, help = "RAI Junior")
    parser.add_argument("--search", action = "store", help = "Search RAI TV")

    parser.add_argument("--pluzz", action = "store_true", default = False, help = "Pluzz France Television")
    parser.add_argument("--tf1", action = "store_true", default = False, help = "MY TF1")
    parser.add_argument("--item", action = "store", help = "RAI On Demand Item")

    parser.add_argument("--date", action = "store", help = "Filter by date YYYY-MM-DD")
    parser.add_argument("--follow", action = "append")

    parser.add_argument("--nolist", action = "store_true", default = False)
    parser.add_argument("--get", action = "store_true", default = False)
    parser.add_argument("--info", action = "store_true", default = False)
    parser.add_argument("--re", action = "store_true", default = False)

    parser.add_argument("pid", nargs = "*")



    args = parser.parse_args()

    Driver.process(args)

    print()

# is this required??? seems a bit of pythonic nonsense
# all RAI html is encoded in "utf-8" (decoded as we read)
#
# and it seems that redirecting the output (e.g. "| less") requires am explicit encoding
# done here
if not sys.stdout.encoding:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach(), "ignore")

if __name__ == '__main__':
    main()
