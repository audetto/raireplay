onDemand     = "http://www.rai.tv/dl/RaiTV/programmi/ricerca/ContentSet-6445de64-d321-476c-a890-ae4ed32c729e-darivedere.html"
replay       = "http://www.rai.it/dl/portale/html/palinsesti/replaytv/static"
info         = "http://www.rai.tv/dl/RaiTV/iphone/assets/tg_json.js?NS=0-1-4c61b46e9a4ab09b25da2246ae52d31edb528475-5.1.1"
invalidMP4   = "http://creativemedia3.rai.it/video_no_available.mp4"

base         = "http://www.rai.tv"


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
