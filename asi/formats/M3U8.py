import asi.Utils
import os
import urllib
import posixpath
import m3u8
import gzip
import logging


def download_m3u8(grabber_program, folder, url, options, pid, filename, title, remux):
    if remux:
        ext = ".mp4"
    else:
        ext = ".ts"

    local_filename = os.path.join(folder, filename + ext)
    local_filename_ts = os.path.join(folder, filename + ".ts")

    if (not options.overwrite) and os.path.exists(local_filename):
        print()
        print("{0} already there as {1}".format(pid, local_filename))
        print()
        return

    item = load_m3u8_from_url(grabber_program, url)

    print()
    print("Saving {0} as {1}".format(pid, local_filename))

    # maximum number of attempts per segment
    max_attempts = options.ts_tries

    try:
        number_of_files = len(item.segments)
        logging.debug('{} segments'.format(number_of_files))
        progress = asi.Utils.get_progress(number_of_files, filename + ".ts")

        with open(local_filename_ts, "wb") as out:
            for seg in item.segments:
                uri = seg.absolute_uri
                attempt = 0
                while True:
                    try:
                        attempt = attempt + 1
                        logging.debug('#{}: {}'.format(attempt, uri))
                        with grabber_program.open(uri) as s:
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
            asi.Utils.remux_to_mp4(local_filename_ts, local_filename, title)
            os.remove(local_filename_ts)

        print()
        print("Saved {0} as {1}".format(pid, local_filename))
        print()

    except BaseException as e:
        logging.info('Exception: {0}'.format(e))
        logging.info('Will remove: {0}'.format(local_filename))
        logging.info('Will remove: {0}'.format(local_filename_ts))
        if os.path.exists(local_filename):
            os.remove(local_filename)
        if remux and os.path.exists(local_filename_ts):
            os.remove(local_filename_ts)
        raise


def load_m3u8_from_url(grabber, uri):
    request = urllib.request.Request(uri, headers=asi.Utils.httpHeaders)
    logging.info('M3U8: {}'.format(uri))
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

    return m3u8.M3U8(content, base_uri=base_uri)


def display_m3u8(m3):
    if m3:
        if m3.is_variant:
            for playlist in m3.playlists:
                fmt = "\tProgram: {0:>2}, Bandwidth: {1:>10}, Resolution: {2:>10}, Codecs: {3}"

                # bandwidth is always in Kb.
                # so we divide by 1000

                resolution = asi.Utils.get_resolution(playlist)
                if playlist.stream_info.program_id is None:
                    program_id = "missing"
                else:
                    program_id = playlist.stream_info.program_id
                line = fmt.format(program_id, int(playlist.stream_info.bandwidth) // 1000,
                                  resolution, playlist.stream_info.codecs)
                print(line)
            print()
        else:
            number_of_segments = len(m3.segments)
            if number_of_segments:
                fmt = "\tPlaylist: {0} segments"
                line = fmt.format(number_of_segments)
                print(line)
                print()
