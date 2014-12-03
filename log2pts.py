#!/usr/bin/python
"""
  Convert log of laser scans into 3D points
    usage:
         ./log2pts.py <input log> <output pts filename>
"""

import sys
import math

MOTION_STEP_X = 0.024/10.

def log2pts( filename, outputFilename ):
    x = 0.0
    f = open( outputFilename, "w" )
    for line in open(filename):
        arr = eval(line)
        for i, a in enumerate(arr):
            angle = math.radians(i-270/2)
            dist = a/1000.0
            f.write( "%.3f %.3f %.3f\n" % (x, dist*math.cos(angle), dist*math.sin(angle)) )
        x += MOTION_STEP_X
    f.close()

if __name__ == "__main__": 
    if len(sys.argv) < 3:
        print __doc__
        sys.exit(1)
    log2pts( sys.argv[1], sys.argv[2] )

# vim: expandtab sw=4 ts=4

