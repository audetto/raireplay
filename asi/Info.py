from __future__ import print_function

import urlgrabber.progress

# this returns some JavaScript like
# setUserLocation("ESTERO");
userLocation = "http://mediapolis.rai.it/relinker/relinkerServlet.htm?cont=826819"

# this one is from TF1
userIP = "http://api.prod.capptain.com/ip-to-country"

def display(grabber, rootFolder):

    location = grabber.urlread(userLocation)
    ip = grabber.urlread(userIP)

    width = urlgrabber.progress.terminal_width()

    print("=" * width)

    print("Root folder:", rootFolder)
    print("Location:   ", location)
    print("IP:         ", ip)

    print()
