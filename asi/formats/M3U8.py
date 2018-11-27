import asi.Utils
import os
import urllib
import posixpath
import m3u8
import gzip


def downloadM3U8(grabberMetadata, grabberProgram, folder, m3, options, pid, filename, title, remux):
    if m3:
        if remux:
            ext = ".mp4"
        else:
            ext = ".ts"

        localFilename   = os.path.join(folder, filename + ext)
        localFilenameTS = os.path.join(folder, filename + ".ts")

        if (not options.overwrite) and os.path.exists(localFilename):
            print()
            print("{0} already there as {1}".format(pid, localFilename))
            print()
            return

        if m3.is_variant:
            playlist = asi.Utils.findPlaylist(m3, options.bwidth)

            print("Downloading:")
            print(playlist)

            uri = playlist.absolute_uri
            item = load_m3u8_from_url(grabberProgram, uri)
        else:
            if len(m3.segments) == 0:
                return
            item = m3

        print()
        print("Saving {0} as {1}".format(pid, localFilename))

        # maximum number of attempts per segment
        max_attempts = options.ts_tries

        try:
            numberOfFiles = len(item.segments)
            progress = asi.Utils.getProgress(numberOfFiles, filename + ".ts")

            with open(localFilenameTS, "wb") as out:
                for seg in item.segments:
                    uri = seg.absolute_uri
                    attempt = 0
                    while True:
                        try:
                            attempt = attempt + 1
                            with grabberProgram.open(uri) as s:
                                b = s.read()
                                size = len(b)
                                if progress:
                                    progress.start(size)
                                out.write(b)
                                if progress:
                                    progress.update(size)
                            break
                        except urllib.error.HTTPError:
                            if attempt <= max_attempts:
                                progress.update(0)
                            else:
                                raise

            if progress:
                progress.done()

            if remux:
                asi.Utils.remuxToMP4(localFilenameTS, localFilename, title)
                os.remove(localFilenameTS)


            print()
            print("Saved {0} as {1}".format(pid, localFilename))
            print()

        except:
            print("Exception: removing {0}".format(localFilename))
            if os.path.exists(localFilename):
                os.remove(localFilename)
            if remux and os.path.exists(localFilenameTS):
                os.remove(localFilenameTS)
            raise


def load_m3u8_from_url(grabber, uri):
    request = urllib.request.Request(uri, headers = asi.Utils.httpHeaders)
    stream = grabber.open(request)

    encoding = None

    # TF1 returns gzipped m3u8 playlists
    info = stream.info()
    if "Content-Encoding" in info:
        encoding = info["Content-Encoding"]

    data = stream.read()
    if encoding == "gzip":
        data = gzip.decompress(data)

    content = data.decode('ascii').strip()

    parsed_url = urllib.parse.urlparse(uri)
    prefix = parsed_url.scheme + '://' + parsed_url.netloc
    base_path = posixpath.normpath(parsed_url.path + '/..')
    base_uri = urllib.parse.urljoin(prefix, base_path)

    return m3u8.M3U8(content, base_uri = base_uri)


def displayM3U8(m3):
    if m3:
        if m3.is_variant:
            for playlist in m3.playlists:
                fmt = "\tProgram: {0:>2}, Bandwidth: {1:>10}, Resolution: {2:>10}, Codecs: {3}"

                # bandwidth is always in Kb.
                # so we divide by 1000

                resolution = asi.Utils.getResolution(playlist)
                if playlist.stream_info.program_id is None:
                    program_id = "missing"
                else:
                    program_id = playlist.stream_info.program_id
                line = fmt.format(program_id, int(playlist.stream_info.bandwidth) // 1000,
                                  resolution, playlist.stream_info.codecs)
                print(line)
            print()
        else:
            numberOfSegments = len(m3.segments)
            if numberOfSegments:
                fmt = "\tPlaylist: {0} segments"
                line = fmt.format(numberOfSegments)
                print(line)
                print()
