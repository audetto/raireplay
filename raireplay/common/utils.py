import sys
import os.path
import urllib.request
import urllib.parse
import codecs
import datetime
import unicodedata
import io
import re
import logging

from raireplay.common import meter


class Obj:
    pass


# got from the iphone
# required for TF1 - www.wat.tv
user_agent = "AppleCoreMedia/1.0.0.9B206 (iPod; U; CPU OS 5_1_1 like Mac OS X; en_us)"
http_headers = {"User-Agent": user_agent}


def http_filename(url):
    name = os.path.basename(urllib.parse.urlsplit(url).path)
    return name


# simply download a file and saves it to local_name
def download_file(grabber_metadata, grabber_program, progress, url, local_name):
    if progress:
        progress.set_name(local_name)

    request = urllib.request.Request(url, headers=http_headers)

    logging.info(f'URL: {url}')
    with grabber_metadata.open(request) as response:
        actual_url = response.geturl()
        if actual_url != url and grabber_metadata != grabber_program:
            logging.info(f'Redirection: {actual_url}')
            return download_file(grabber_program, grabber_program, progress, actual_url, local_name)

        with open(local_name, "wb") as f:
            # same length as shutil.copyfileobj

            # the rest is the same logic as urllib.request.urlretrieve
            # which unfortunately does not work with proxies
            block_size = 1024 * 16
            size = -1

            headers = response.info()
            if "content-length" in headers:
                size = int(headers["Content-Length"])

            if progress:
                progress.start(size)

            while 1:
                buf = response.read(block_size)
                if not buf:
                    break
                amount_read = len(buf)
                f.write(buf)
                if progress:
                    progress.update(amount_read)

            if progress:
                progress.done()


# def downloadFile(grabberMetadata, grabberProgram, progress, url, local_name):
#    if progress:
#        progress.setName(local_name)
#    request = urllib.request.Request(url, headers = httpHeaders)
#
#    urllib.request.urlretrieve(url, filename = local_name, reporthook = progress)
#    if progress:
#        progress.done()


# download a file and returns a file object
# with optional encoding, checking if it exists already...
def download(grabber, progress, url, local_name, down_type, encoding, check_time=False):
    try:
        if down_type == "shm":
            request = urllib.request.Request(url, headers=http_headers)
            logging.info(f'URL: {url}')
            f = grabber.open(request)
            if encoding:
                decoder = codecs.getreader(encoding)
                f = decoder(f)
            else:
                # make it seekable
                f = io.BytesIO(f.read())
        else:
            # here we need to download (maybe), copy local and open
            exists = os.path.exists(local_name)
            exists = exists and os.path.getsize(local_name) > 0

            if down_type == "never" and not exists:
                raise Exception(f"Will not download missing file: {url} -> {local_name}")

            if exists and check_time:
                # if it is from yesterday or before, we re-download it
                today = datetime.date.today()
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(local_name))
                exists = today == file_time.date()

            if down_type == "always" or (down_type == "update" and not exists):
                download_file(grabber, grabber, progress, url, local_name)
            else:
                logging.info(f'Exist: {url}')

            # now the file exists on the local filesystem
            if not encoding:
                f = open(local_name, "rb")
            else:
                f = codecs.open(local_name, "r", encoding=encoding)

        return f

    except Exception:
        logging.exception(f'URL: {url}')
        return None


def find_url_by_bandwidth(data, bandwidth):
    if len(data) == 1:
        return next(iter(data.values()))

    if bandwidth == "high":
        b1 = sys.maxsize
    elif bandwidth == "low":
        b1 = 0
    else:
        b1 = int(bandwidth)

    opt = None
    dist = float('inf')

    for b2, v in data.items():
        d = abs(b2 - b1)
        if d < dist:
            dist = d
            opt = v

    return opt


# sometimes RAI sends invalid XML
# we get "reference to invalid character number"
def remove_invalid_xml_characters(s):
    s = s.replace("&#0", "xx")
    s = s.replace("&#1", "xx")
    s = s.replace("&#22", "xx")
    return s


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    result = "".join([c for c in nkfd_form if not unicodedata.combining(c)])
    return result


def make_filename(value):
    if not value:
        return value

    translate_to = "_"
    characters_to_remove = " /:^,|'\\."
    translate_table = dict((ord(char), translate_to) for char in characters_to_remove)
    name = value.translate(translate_table)
    name = remove_accents(name)
    name = re.sub("_+", "_", name)
    name = re.sub("_-_", "_", name)
    return name


def get_progress(number_of_files=1, filename=None):
    # only use a progress meter if we are not redirected
    if sys.stdout.isatty():
        p = meter.ReportHook(number_of_files)
        if filename:
            p.set_name(filename)
        return p
    else:
        return None


def get_new_pid(db, pid):
    # 0 is not a valid pid
    if not pid:
        pid = len(db) + 1

        # we only enforce uniqueness
        # if there is no real PID
        while str(pid) in db:
            pid = pid + 1

    pid = str(pid)

    return pid


def add_to_db(db, prog):
    if not prog:
        return

    pid = prog.pid

    if pid in db:
        logging.warning(f"duplicate pid {pid}")

    db[pid] = prog


def get_string_from_url(grabber, url):
    logging.info(f'String: {url}')
    with grabber.open(url) as f:
        content = f.read().decode("ascii")
        return content


def str_date(date):
    s = date.strftime("%Y-%m-%d %H:%M")
    return s
