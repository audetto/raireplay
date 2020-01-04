import raireplay.common.utils
import os
import urllib.error
import urllib.parse
import urllib.request
import posixpath

import raireplay.formats.mp4
import m3u8
import gzip
import logging
from Cryptodome.Cipher import AES


def decrypt(data, key, media_sequence, grabber, key_cache):
    if key is not None:
        if key.method == 'AES-128' and key.iv is None:
            uri = key.uri
            if uri not in key_cache:
                request = urllib.request.Request(uri, headers=raireplay.common.utils.http_headers)
                stream = grabber.open(request)
                logging.debug(f'AES-128 key: {uri}')
                key_cache[uri] = stream.read()

            aes_key = key_cache[uri]
            iv = media_sequence.to_bytes(16, 'big')
            aes = AES.new(aes_key, AES.MODE_CBC, IV=iv)
            clear = aes.decrypt(data)
            return clear
        else:
            raise Exception(f'M3U8 unsupported key: {key}')
    else:
        return data


def download_m3u8(grabber_program, folder, url, options, pid, filename, title, remux):
    if remux:
        ext = ".mp4"
    else:
        ext = ".ts"

    local_filename = os.path.join(folder, filename + ext)
    local_filename_ts = os.path.join(folder, filename + ".ts")

    if (not options.overwrite) and os.path.exists(local_filename):
        print()
        print(f"{pid} already there as {local_filename}")
        print()
        return

    item = load_m3u8_from_url(grabber_program, url)

    print()
    print(f"Saving {pid} as {local_filename}")

    # maximum number of attempts per segment
    max_attempts = options.ts_tries

    try:
        number_of_files = len(item.segments)
        logging.debug(f'{number_of_files} segments')
        progress = raireplay.common.utils.get_progress(number_of_files, filename + ".ts")
        key_cache = {}

        with open(local_filename_ts, "wb") as out:
            for seg in item.segments:
                segment_uri = seg.absolute_uri
                request = urllib.request.Request(segment_uri, headers=raireplay.common.utils.http_headers)
                attempt = 0

                while True:
                    try:
                        attempt = attempt + 1
                        logging.debug(f'#{attempt}: {segment_uri}')
                        with grabber_program.open(request) as s:
                            b = s.read()
                            size = len(b)
                            if progress:
                                progress.start(size)
                            b = decrypt(b, seg.key, item.media_sequence, grabber_program, key_cache)
                            out.write(b)
                            if progress:
                                progress.update(size)
                        break
                    except urllib.error.HTTPError:
                        if (attempt <= max_attempts) and progress:
                            progress.update(0)
                        else:
                            raise

        if progress:
            progress.done()

        if remux:
            raireplay.formats.mp4.remux_to_mp4(local_filename_ts, local_filename, title)
            os.remove(local_filename_ts)

        print()
        print(f"Saved {pid} as {local_filename}")
        print()

    except BaseException:
        logging.exception(f'M3U8: {local_filename}')
        if os.path.exists(local_filename):
            logging.info(f'Removing: {local_filename}')
            os.remove(local_filename)
        if remux and os.path.exists(local_filename_ts):
            logging.info(f'Removing: {local_filename_ts}')
            os.remove(local_filename_ts)
        raise


def load_m3u8_from_url(grabber, uri):
    request = urllib.request.Request(uri, headers=raireplay.common.utils.http_headers)
    logging.info(f'M3U8: {uri}')
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

                resolution = get_resolution(playlist)
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
                line = f"\tPlaylist: {number_of_segments} segments"
                print(line)
                print()


def get_resolution(p):
    if not p.stream_info.resolution:
        return "N/A"
    res = "{0:>4}x{1:>4}".format(p.stream_info.resolution[0], p.stream_info.resolution[1])
    return res


def find_playlist(m3, bandwidth):
    data = {}

    # bandwidth is alaways in Kb.
    # so we divide by 1000

    for p in m3.playlists:
        b = int(p.stream_info.bandwidth) // 1000
        data[b] = p

    opt = raireplay.common.utils.find_url_by_bandwidth(data, bandwidth)

    return opt