#! /usr/bin/python

import sys
import platform
import codecs
import argparse
import logging.config
import os
import configparser

import driver


def get_cli_args(defaults):
    parser = argparse.ArgumentParser(description="Rai Replay", fromfile_prefix_chars="@")

    parser.add_argument("--download", action="store", default="update", choices=["always", "update", "never", "shm"],
                        help="Default is update")
    parser.add_argument("--format", action="store", choices=["h264", "ts", "tsmp4", "mms"])
    parser.add_argument("--bwidth", action="store", default="high")
    parser.add_argument("--ip", action="store_true", default=False, help="print IP info")
    parser.add_argument("--tor", action="store", help="coutry code for tor exit nodes")
    parser.add_argument("--tor-proxy", action="store_true", default=False, help="use tor proxy")
    parser.add_argument("--tor-search", action="store", help="search for a tor exit node [attempts,skip]")
    parser.add_argument("--proxy-all", action="store_true", default=False, help="use the proxy for everything")
    parser.add_argument("--proxy", action="store")
    parser.add_argument("--overwrite", action="store_true", default=False, help="overwrite program")
    parser.add_argument("--location", action="store", help="path where to download programs")
    parser.add_argument("--here", action="store_true", help="download to current folder")
    parser.add_argument("--ts-tries", action="store", default=20)

    parser.add_argument("--replay", action="store_true", default=False, help="RAI Replay")
    parser.add_argument("--raiplay", action="store_true", default=False, help="RaiPlay")
    parser.add_argument("--programma", action="store", default=False, help="RaiPlay Program URL")
    parser.add_argument("--ondemand", action="store_true", default=False, help="RAI On Demand List")

    parser.add_argument("--mediaset", action="store_true", default=False, help="Video Mediaset")
    parser.add_argument("--tg5", action="store_true", default=False, help="TG Mediaset")
    parser.add_argument("--m6", action="store_true", default=False, help="M6")
    parser.add_argument("--tf1", action="store_true", default=False, help="MY TF1")

    parser.add_argument("--m3u8", action="store", help="Playlist")

    parser.add_argument("--date", action="store", help="Filter by date YYYY-MM-DD")
    parser.add_argument("--channel", action="store", help="Filter by channel")
    parser.add_argument("--follow", action="append")

    parser.add_argument("--nolist", action="store_true", default=False)
    parser.add_argument("--get", action="store_true", default=False, help="download program")
    parser.add_argument("--cast", action="store_true", default=False, help="cast")
    parser.add_argument("--show", action="store_true", default=False, help="print video url")
    parser.add_argument("--info", action="store_true", default=False, help="display program info")
    parser.add_argument("--re", action="store_true", default=False, help="filters are RegExp")
    parser.add_argument("--logging", action="store", help="logging configuration")

    parser.set_defaults(**defaults)

    parser.add_argument("pid", nargs="*")

    args = parser.parse_args()

    return args


def get_default_configuration():
    home = os.path.expanduser('~')
    config_file = os.path.join(home, '.raireplay', 'config.ini')
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read([config_file])
        return config.defaults()
    else:
        return {}


def main():
    glo_args = get_default_configuration()
    args = get_cli_args(glo_args)

    if args.logging:
        logging.config.fileConfig(args.logging)

    driver.process(args)

    print()


def fix_codepages():
    if platform.system() == "Windows":
        # in windows there are issues when printing utf-8 to the console
        # it does not work out of the box
        # no clear solution comes out of google
        # this "choice" seems to work
        sys.stdout = codecs.getwriter("cp850")(sys.stdout.buffer, "ignore")
    elif not sys.stdout.encoding:
        # is this required??? seems a bit of pythonic nonsense
        # all RAI html is encoded in "utf-8" (decoded as we read)
        #
        # and it seems that redirecting the output (e.g. "| less") requires an explicit encoding
        # done here
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "ignore")


if __name__ == '__main__':
    fix_codepages()
    main()
