import configparser
import os
import urllib.parse
import logging
from xml.etree import ElementTree

import raireplay.common.utils
import raireplay.common.raiurls


def download_mms(folder, url, options, pid, filename):
    try:
        import libmimms.core

        local_filename = os.path.join(folder, filename + ".wmv")

        if (not options.overwrite) and os.path.exists(local_filename):
            print(f"{pid} already there as {local_filename}")
            return

        opt = raireplay.common.utils.Obj()
        opt.quiet = False
        opt.url = url
        opt.resume = False
        opt.bandwidth = 1e6
        opt.filename = local_filename
        opt.clobber = True
        opt.time = 0

        libmimms.core.download(opt)

    except ImportError:
        logging.exception(f'MMS: {url}')


def get_mms_url(grabber, url):
    mms = None

    url_scheme = urllib.parse.urlsplit(url).scheme
    if url_scheme == "mms":
        # if it is already mms, don't look further
        mms = url
    else:
        # search for the mms url
        content = raireplay.common.utils.get_string_from_url(grabber, url)

        if content in raireplay.common.raiurls.invalidMP4:
            # is this the case of videos only available in Italy?
            mms = content
        else:
            root = ElementTree.fromstring(content)
            if root.tag == "ASX":
                asf = root.find("ENTRY").find("REF").attrib.get("HREF")

                if asf:
                    # use urlgrab to make it work with ConfigParser
                    url_scheme = urllib.parse.urlsplit(asf).scheme
                    if url_scheme == "mms":
                        mms = asf
                    else:
                        content = raireplay.common.utils.get_string_from_url(grabber, asf)
                        config = configparser.ConfigParser()
                        config.read_string(content)
                        mms = config.get("Reference", "ref1")
                        mms = mms.replace("http://", "mms://")
            elif root.tag == "playList":
                # adaptive streaming - unsupported
                pass
            else:
                print("Unknown root tag: " + root.tag)

    return mms
