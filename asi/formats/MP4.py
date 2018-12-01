import logging
import subprocess


def remux_to_mp4(in_file, out_file, title):
    # -absf aac_adtstoasc
    # seems to be needed by ffmpeg (Fedora), not by avconv (Pi)
    cmd_line = ["ffmpeg", "-i", in_file, "-vcodec", "copy", "-acodec", "copy", "-absf", "aac_adtstoasc", "-y", out_file]
    code = subprocess.call(cmd_line)
    if code != 0:
        raise Exception("ffmpeg failed: exit code {0}".format(code))
    set_mp4_tag(out_file, title)


# sometimes the downloaded mp4 contains bad tag for the title
# TG5 has the title set to "unspecified"
# as this is then used by minidlna, it must be decent enough
# to be able to find it in the list
#
# we could as well remove it
# btw, the ones that are remux don't have the tag, so they are not wrong
# for symmetry we set the title tag to all of them
def set_mp4_tag(filename, title):
    # this is allowed to fail as mutagen(x) is somehow hard to obtain
    try:
        import mutagen.easymp4
        a = mutagen.easymp4.EasyMP4(filename)
        a["title"] = title
        a.save()
    except Exception as e:
        logging.info('Exception: {0}'.format(e))
        print("Failed to set MP4 tag to : {0}".format(filename))
