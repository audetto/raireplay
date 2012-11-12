from __future__ import print_function

import urlgrabber.progress

# this returns some JavaScript like
# setUserLocation("ESTERO");
userLocation = "http://mediapolis.rai.it/relinker/relinkerServlet.htm?cont=826819"

def display(grabber, rootFolder):

    location = grabber.urlread(userLocation)

    width = urlgrabber.progress.terminal_width()

    print("=" * width)

    print("Location:   ", location)
    print("Root folder:", rootFolder)

    print()
