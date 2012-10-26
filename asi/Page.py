from __future__ import print_function

import os.path
import urlgrabber.grabber
import urlgrabber.progress

from asi import Utils

# http://www.rai.tv/StatisticheProxy/proxyPost.jsp?action=getLastContentByTag&numContents=12&tags=PageOB:Page-054bcd53-df7e-42c3-805b-dbe6e90bc817&domain=RaiTv&xsl=rai_tv-statisticheN&_=1351111295981


def getDataUrl(page):
    n = 1000
    url = "http://www.rai.tv/StatisticheProxy/proxyPost.jsp?action=getLastContentByTag&numContents={0}&tags=PageOB:{1}&domain=RaiTv".format(n, page)
    return url

class Page:
    def __init__(self, url, folder, type):
        self.url = url

        page = Utils.httpFilename(self.url)
        page = os.path.splitext(page)[0]

        self.dataUrl = getDataUrl(page)

        g = urlgrabber.grabber.URLGrabber()

        localFilename = os.path.join(folder, page + ".xml")
        f = Utils.download(g, self.dataUrl, localFilename, type, None)
