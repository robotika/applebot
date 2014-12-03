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


def scan( laser, num ):
    filename = datetime.datetime.now().strftime("logs/scan_%y%m%d_%H%M%S.txt")    
    print filename
    f = open( filename, "w" )
    laser.startLaser()
    for i in xrange(num):
        data, reminision = laser.internalScan()
        f.write( str(data) + '\n' )
        f.flush()
        print len(data), data[133:138]
    f.close()

if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    laser.HOST, laser.PORT = '169.254.225.156', 2111
    print datetime.datetime.now()
    print scan( laser.LaserIP(), num=int(sys.argv[1]) )
    print datetime.datetime.now()

# vim: expandtab sw=4 ts=4

