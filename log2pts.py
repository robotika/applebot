#!/usr/bin/python
"""
  Convert log of laser scans into 3D points
    usage:
         ./log2pts.py <input log> <output pts filename>
"""

import sys
import math

MOTION_STEP_X = 0.024/10.


def log2ptsGenerator( filename ):
    x = 0.0
    for line in open(filename):
        arr = eval(line)
        for i, a in enumerate(arr):
            angle = math.radians(i-270/2)
            dist = a/1000.0
            yield (x, dist*math.cos(angle), dist*math.sin(angle))
        x += MOTION_STEP_X


def log2pts( filename, outputFilename ):
    f = open( outputFilename, "w" )
    for x,y,z in log2ptsGenerator( filename ):
        f.write( "%.3f %.3f %.3f\n" % (x, y, z) )
    f.close()


if __name__ == "__main__": 
    if len(sys.argv) < 3:
        print __doc__
        sys.exit(1)
    log2pts( sys.argv[1], sys.argv[2] )

# vim: expandtab sw=4 ts=4

