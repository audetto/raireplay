import logging


def cast_url(url):
    import pychromecast

    logging.info('Cast discovery')
    chromecasts = pychromecast.get_chromecasts()
    for cc in chromecasts:
        logging.info(f'Found: {cc.device.friendly_name}')

    if not chromecasts:
        logging.info('No casts found')
        return

    cast = chromecasts[0]
    logging.info(f'Casting to {cast.host}:{cast.port} {url}')
    cast.wait()
    mc = cast.media_controller
    mc.play_media(url, 'video/mp4')
