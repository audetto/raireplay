import configparser
import os
import urllib
from xml.etree import ElementTree

import asi.Utils
import asi.RAIUrls


def download_mms(folder, url, options, pid, filename):
    try:
        import libmimms.core

        local_filename = os.path.join(folder, filename + ".wmv")

        if (not options.overwrite) and os.path.exists(local_filename):
            print("{0} already there as {1}".format(pid, local_filename))
            return

        opt = asi.Utils.Obj()
        opt.quiet = False
        opt.url = url
        opt.resume = False
        opt.bandwidth = 1e6
        opt.filename = local_filename
        opt.clobber = True
        opt.time = 0

        libmimms.core.download(opt)

    except ImportError:
        print("\nMissing libmimms.\nCannot download: {0}.".format(url))


def get_mms_url(grabber, url):
    mms = None

    url_scheme = urllib.parse.urlsplit(url).scheme
    if url_scheme == "mms":
        # if it is already mms, don't look further
        mms = url
    else:
        # search for the mms url
        content = asi.Utils.get_string_from_url(grabber, url)

        if content in asi.RAIUrls.invalidMP4:
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
                        content = asi.Utils.get_string_from_url(grabber, asf)
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
