import urllib.parse

onDemand     = "http://www.rai.tv/dl/RaiTV/programmi/ricerca/ContentSet-6445de64-d321-476c-a890-ae4ed32c729e-darivedere.html"
replay       = "http://www.rai.it/dl/portale/html/palinsesti/replaytv/static"
info         = "http://www.rai.tv/dl/RaiTV/iphone/assets/tg_json.js?NS=0-1-4c61b46e9a4ab09b25da2246ae52d31edb528475-5.1.1"
junior       = "http://www.junior.rai.it/dl/junior/pages/H1/ContentSet-94000ddd-f6c6-4a24-87d6-7a63817ae207.html"
base         = "http://www.rai.tv"

invalidMP4   = {"http://creativemedia3.rai.it/video_no_available.mp4",
                '<Mediapolis><url type="content">http://download.rai.it/video_no_available.mp4</url><url type="bumper"></url><url type="bumperend"></url><ct>mp4</ct><bitrate>0</bitrate><smooth>N</smooth><is_live>N</is_live><description>Rai</description><geoprotection>N</geoprotection><category>11111</category><plVod></plVod><plLive></plLive><logo></logo><poster>http://www.rai.tv/dl/RaiTV/2012/images/ogImage.jpg</poster><duration></duration><krpano></krpano></Mediapolis>'}


def getItemUrl(name):
    url = "http://www.rai.tv/dl/RaiTV/programmi/media/" + name + ".html"
    return url


# returns the url that requests the list of ContentItems behind a Page-xxx page
def getPageDataUrl(page):
    n = 1000 # just get them all
    url = "http://www.rai.tv/StatisticheProxy/proxyPost.jsp?action=getLastContentByTag&numContents={0}&tags=PageOB:{1}&domain=RaiTv".format(n, page)
    return url


def getWebFromID(pid):
    web = "/dl/RaiTV/programmi/media/{0}.html".format(pid)
    return web


def getJuniorPage(pid):
    http = "http://www.junior.rai.it/dl/junior/pages/Container/Page-{0}.html".format(pid)
    return http


def getJuniorBlock(pid):
    http = "http://www.junior.rai.it{0}".format(pid)
    return http


def getSearchUrl(name, num = 10):
    # at the end omitted here
    # &NS=0-1-4c61b46e9a4ab09b25da2246ae52d31edb528475-5.1.1
    # alternative from firefox:
    # http://www.rai.tv/ricerca/search?q=crozza&sort=date:D:L:d1&filter=0&getfields=*&site=raitv&start=0

    quoted = urllib.parse.quote(name)

    http = "http://www.ricerca.rai.it/search?site=raitv&output=xml_no_dtd&proxystylesheet=json&client=json&sort=date:D:S:d1&filter=0&getfields=*&partialfields=videourl_mp4:http&num={1}&q={0}".format(quoted, num)
    return http
