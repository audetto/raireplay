import os.path
import asi.Utils
import asi.RAIUrls
import logging


def downloadH264(grabberMetadata, grabberProgram, folder, h264, options, pid, filename, title):
    localFilename = os.path.join(folder, filename + ".mp4")

    if (not options.overwrite) and os.path.exists(localFilename):
        print()
        print("{0} already there as {1}".format(pid, localFilename))
        print()
        return

    url = asi.Utils.findUrlByBandwidth(h264, options.bwidth)

    print("Downloading:")
    print(url)

    print()
    print("Saving {0} as {1}".format(pid, localFilename))

    try:
        progress = asi.Utils.getProgress()
        asi.Utils.downloadFile(grabberMetadata, grabberProgram, progress, url, localFilename)

        size = os.path.getsize(localFilename)
        for a in asi.RAIUrls.invalidMP4:
            if size == len(a):
                raise Exception("{0} only available in Italy".format(url))

        asi.Utils.setMP4Tag(localFilename, title)

        print()
        print("Saved {0} as {1}".format(pid, filename))
        print()

    except BaseException as e:
        logging.info('Exception: {0}'.format(e))
        logging.info('Will remove: {0}'.format(localFilename))
        if os.path.exists(localFilename):
            os.remove(localFilename)
        raise


def displayH264(h264):
    if h264:
        for k, v in h264.items():
            print("h264[{0}]: {1}".format(k, v))
        print()


def addH264Url(h264, bwidth, url):
    # we do not want to add a None
    # so that
    # "if h264:"
    # can still be used
    if url:
        h264[bwidth] = url
