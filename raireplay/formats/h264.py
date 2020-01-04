import os.path
import raireplay.common.utils
import raireplay.common.raiurls
import logging

import raireplay.formats.mp4


def download_h264(grabber_metadata, grabber_program, folder, url, options, pid, filename, title):
    local_filename = os.path.join(folder, filename + ".mp4")

    if (not options.overwrite) and os.path.exists(local_filename):
        print()
        print(f"{pid} already there as {local_filename}")
        print()
        return

    print("Downloading:")
    print(url)

    print()
    print(f"Saving {pid} as {local_filename}")

    try:
        progress = raireplay.common.utils.get_progress()
        raireplay.common.utils.download_file(grabber_metadata, grabber_program, progress, url, local_filename)

        size = os.path.getsize(local_filename)
        for a in raireplay.common.raiurls.invalidMP4:
            if size == len(a):
                raise Exception(f"{url} only available in Italy")

        raireplay.formats.mp4.set_mp4_tag(local_filename, title)

        print()
        print(f"Saved {pid} as {filename}")
        print()

    except BaseException:
        logging.exception(f'H264: {url}')
        if os.path.exists(local_filename):
            logging.info(f'Removing: {local_filename}')
            os.remove(local_filename)
        raise


def display_h264(h264):
    if h264:
        for k, v in h264.items():
            print(f"h264[{k}]: {v}")
        print()


def add_h264_url(h264, bwidth, url):
    # we do not want to add a None
    # so that
    # "if h264:"
    # can still be used
    if url:
        h264[bwidth] = url
