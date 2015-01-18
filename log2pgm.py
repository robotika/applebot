#!/usr/bin/python
"""
  Convert log of laser scans into PGM image of distances
    usage:
         ./log2pgm.py <input log> <output image>
"""

import sys
import math


def loadAllScans( filename, returnAlsoRemission=False ):
    arr = []
    arrRem = []
    for line in open(filename):
        t = eval(line)
        if len(t) == 2: # distance + remission
            arr.append( t[0] )
            arrRem.append( t[1] )
        else:
            arr.append( t )
    # workaround for snapshots, where whole scan is single line
    if len(arr) == 1:
        print "Snapshot file detected, count =", len(arr[0])
        tmp = arr[0]
        arr = []
        for t in tmp:
            if len(t) == 2: # distance + remission
                arr.append( t[0] )
                arrRem.append( t[1] )
            else:
                arr.append( t )
    if returnAlsoRemission:
        return arr, arrRem
    return arr

def dist2gray( value ):
    return min(255, value/5)


def log2pgm( filename, outputFilename ):
    f = open( outputFilename, "w" )
    scans = loadAllScans( filename )
    f.write( "P2\n%d %d\n255\n" % (len(scans), len(scans[0])) )
    for y in xrange( len(scans[0]) ):
        for x in xrange(len(scans)):
            f.write( "%d " % dist2gray(scans[x][y]) )
        f.write( "\n" )
    f.close()


if __name__ == "__main__": 
    if len(sys.argv) < 3:
        print __doc__
        sys.exit(1)
    log2pgm( sys.argv[1], sys.argv[2] )

# vim: expandtab sw=4 ts=4

