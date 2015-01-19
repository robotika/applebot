#!/usr/bin/python
"""
  Scan 3D area
    usage:
         ./scan3d.py <num>
"""

import sys
import os
import math
import datetime

sys.path.append( ".."+os.sep+"eduro") 

import laser
import urllib

URL = "http://192.168.1.6/img.jpg"
URL2 = "http://192.168.1.6/image?channel=mono"

def takePicture( index ):
    filename = datetime.datetime.now().strftime("logs/pic_%y%m%d_%H%M%S") + "_%03d.jpg" % index
    url = urllib.urlopen( URL ) 
    f = open( filename, "wb" )
    data = url.read(1000000)
    print len(data)
    f.write( data )
    f.close()
    filename = datetime.datetime.now().strftime("logs/bw_%y%m%d_%H%M%S") + "_%03d.jpg" % index
    url = urllib.urlopen( URL2 ) 
    f = open( filename, "wb" )
    data = url.read(1000000)
    print len(data)
    f.write( data )
    f.close()


def scan( laser, num ):
    filename = datetime.datetime.now().strftime("logs/scan_%y%m%d_%H%M%S.txt")    
    print filename
    f = open( filename, "w" )
    laser.startLaser()
    for i in xrange(num):
        if i % 10 == 0:
            takePicture( i/10 )
        data, reminision = laser.internalScan()
        f.write( str( (data, reminision) ) + '\n' )
        f.flush()
        print len(data), data[133:138]
    f.close()

if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
#    laser.HOST, laser.PORT = '169.254.225.156', 2111
    laser.HOST, laser.PORT = '192.168.1.156', 2111
    print datetime.datetime.now()
    print scan( laser.LaserIP(), num=int(sys.argv[1]) )
    print datetime.datetime.now()

# vim: expandtab sw=4 ts=4

