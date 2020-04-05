import os

import raireplay.common.utils
from raireplay.common.config import create_folder


def download_multi(grabber, folder, urls, options, pid, filename):
    program_folder = os.path.join(folder, filename)
    create_folder(program_folder)

    for i, url in enumerate(urls):
        progress = raireplay.common.utils.get_progress()
        part_filename = f'{filename}_#{1 + i:03}.mp3'
        local_filename = os.path.join(program_folder, part_filename)
        raireplay.common.utils.download_file(grabber, grabber, progress, url, local_filename)
