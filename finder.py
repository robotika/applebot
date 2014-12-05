#!/usr/bin/python
"""
  Try to find an apple in 3D scan
    usage:
         ./finder.py <size in meters> <log file>
"""

import sys
import math
import cv2
import numpy as np

from log2pgm import loadAllScans
from log2pts import MOTION_STEP_X

def findApples( size, scans ):
    "try to find an apple(s) of given size"
    tmp = np.array( scans ) / 5
    mask = tmp > 255
    tmp[mask] = 255
    img = np.array( tmp, dtype=np.uint8 ) # scaling milimeters to 1m in uint8
    print img.shape, img.dtype
#    cv2.threshold( img, 128, 255, cv2.THRESH_BINARY )    
    g_mser = cv2.MSER( _delta = 1, _min_area=100, _max_area=30*20 )
    gray = img.T
    frame = cv2.cvtColor( img.T, cv2.COLOR_GRAY2BGR )
    contours = g_mser.detect(gray, None)

    for cnt in contours:
        (x1,y1),(x2,y2) = np.amin( cnt, axis=0 ), np.amax( cnt, axis=0 )
        if abs( (x2-x1)*MOTION_STEP_X - size ) < 0.01:
            print (x2-x1)*MOTION_STEP_X, (x1,y1),(x2,y2)
            box = np.int0([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])        
            cv2.drawContours( frame,[box],0,(255,0,0),2)
            # TODO verify distance variability and holes

    cv2.imshow('image', frame) # transposed matrix corresponds to "what we are used to" view
    cv2.imwrite( "tmp.png", frame )
    cv2.waitKey(0)

if __name__ == "__main__": 
    if len(sys.argv) < 3:
        print __doc__
        sys.exit(1)
    print findApples( size=float(sys.argv[1]), scans=loadAllScans(sys.argv[2]) )

# vim: expandtab sw=4 ts=4

