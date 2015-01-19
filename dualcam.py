#!/usr/bin/python
"""
  Utility for testing of Dual Sensor Camera AV3236DN
    usage:
         ./dualcam.py <output file>
"""

import sys
import urllib

URL = "http://192.168.1.6/h264f?res=half&qp=20&ssn=1&channel=color" # color|mono
URLP = "http://192.168.1.6/h264f?res=half&qp=20&ssn=1&iframe=0&channel=color"
URL_DAY_NIGHT = "http://192.168.1.6/set?daynight=dual" # auto|day|night|dual

def recordStream( filename ):
    print urllib.urlopen( URL_DAY_NIGHT ).read()
    url = urllib.urlopen( URL ) 
    f = open( filename, "wb" )
    while True:
        data = url.read(200000)
        if len(data) > 0:
            print len(data)
            f.write( data )
            url.close()
            url = urllib.urlopen( URLP ) 
    f.close()

if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    recordStream( sys.argv[1] )

# vim: expandtab sw=4 ts=4

