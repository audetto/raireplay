import os.path
import asi.Utils
import asi.RAIUrls
import logging

import asi.formats.MP4


def download_h264(grabber_metadata, grabber_program, folder, url, options, pid, filename, title):
    local_filename = os.path.join(folder, filename + ".mp4")

    if (not options.overwrite) and os.path.exists(local_filename):
        print()
        print("{0} already there as {1}".format(pid, local_filename))
        print()
        return

    print("Downloading:")
    print(url)

    print()
    print("Saving {0} as {1}".format(pid, local_filename))

    try:
        progress = asi.Utils.get_progress()
        asi.Utils.download_file(grabber_metadata, grabber_program, progress, url, local_filename)

        size = os.path.getsize(local_filename)
        for a in asi.RAIUrls.invalidMP4:
            if size == len(a):
                raise Exception("{0} only available in Italy".format(url))

        asi.formats.MP4.set_mp4_tag(local_filename, title)

        print()
        print("Saved {0} as {1}".format(pid, filename))
        print()

    except BaseException as e:
        logging.info('Exception: {0}'.format(e))
        logging.info('Will remove: {0}'.format(local_filename))
        if os.path.exists(local_filename):
            os.remove(local_filename)
        raise


def display_h264(h264):
    if h264:
        for k, v in h264.items():
            print("h264[{0}]: {1}".format(k, v))
        print()


def add_h264_url(h264, bwidth, url):
    # we do not want to add a None
    # so that
    # "if h264:"
    # can still be used
    if url:
        h264[bwidth] = url
