on_demand = "http://www.rai.tv/dl/RaiTV/programmi/ricerca/ContentSet-6445de64-d321-476c-a890-ae4ed32c729e-darivedere.html"
base = "http://www.rai.tv"

raiplay_base = "https://www.raiplay.it"
raiplay = "https://www.raiplay.it/palinsesto/app/${channel}/${date}.json"

# raiplay programs
# http://www.raiplay.it/programmi/?json
# http://www.raiplay.it/programmi/unpassodalcielo/?json


invalidMP4 = {"http://creativemedia3.rai.it/video_no_available.mp4",
              '<Mediapolis><url type="content">http://download.rai.it/video_no_available.mp4</url><url type="bumper"></url><url type="bumperend"></url><ct>mp4</ct><bitrate>0</bitrate><smooth>N</smooth><is_live>N</is_live><description>Rai</description><geoprotection>N</geoprotection><category>11111</category><plVod></plVod><plLive></plLive><logo></logo><poster>http://www.rai.tv/dl/RaiTV/2012/images/ogImage.jpg</poster><duration></duration><krpano></krpano></Mediapolis>'}


def get_item_url(name):
    url = f"http://www.rai.tv/dl/RaiTV/programmi/media/{name}.html"
    return url


# returns the url that requests the list of ContentItems behind a Page-xxx page
def get_page_data_url(page):
    n = 1000  # just get them all
    url = f"http://www.rai.tv/StatisticheProxy/proxyPost.jsp?action=getLastContentByTag&numContents={n}&tags=PageOB:{page}&domain=RaiTv"
    return url


def get_web_from_id(pid):
    web = f"/dl/RaiTV/programmi/media/{pid}.html"
    return web
