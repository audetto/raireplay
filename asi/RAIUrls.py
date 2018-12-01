on_demand = "http://www.rai.tv/dl/RaiTV/programmi/ricerca/ContentSet-6445de64-d321-476c-a890-ae4ed32c729e-darivedere.html"
replay = "http://www.rai.it/dl/portale/html/palinsesti/replaytv/static"
info = "http://www.rai.tv/dl/RaiTV/iphone/assets/tg_json.js?NS=0-1-4c61b46e9a4ab09b25da2246ae52d31edb528475-5.1.1"
base = "http://www.rai.tv"
raiplay = "http://www.rai.it/dl/palinsesti/Page-e120a813-1b92-4057-a214-15943d95aa68-json.html?"  # canale=Rai3&giorno=08-01-2017"

# raiplay programs
# http://www.raiplay.it/programmi/?json
# http://www.raiplay.it/programmi/unpassodalcielo/?json


invalidMP4 = {"http://creativemedia3.rai.it/video_no_available.mp4",
              '<Mediapolis><url type="content">http://download.rai.it/video_no_available.mp4</url><url type="bumper"></url><url type="bumperend"></url><ct>mp4</ct><bitrate>0</bitrate><smooth>N</smooth><is_live>N</is_live><description>Rai</description><geoprotection>N</geoprotection><category>11111</category><plVod></plVod><plLive></plLive><logo></logo><poster>http://www.rai.tv/dl/RaiTV/2012/images/ogImage.jpg</poster><duration></duration><krpano></krpano></Mediapolis>'}


def get_item_url(name):
    url = "http://www.rai.tv/dl/RaiTV/programmi/media/" + name + ".html"
    return url


# returns the url that requests the list of ContentItems behind a Page-xxx page
def get_page_data_url(page):
    n = 1000  # just get them all
    url = "http://www.rai.tv/StatisticheProxy/proxyPost.jsp?action=getLastContentByTag&numContents={0}&tags=PageOB:{1}&domain=RaiTv".format(
        n, page)
    return url


def get_web_from_id(pid):
    web = "/dl/RaiTV/programmi/media/{0}.html".format(pid)
    return web
