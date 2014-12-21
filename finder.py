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
from apple import Apple

def isItApple( patch ):
    a = Apple(patch)
    val = a.fitSphere( minRadius=0.03, maxRadius=0.15 )
    if val > 0.8:
        print a.center, a.radius
        return True
    return False

def scans2img( scans ):
    "convert array of 2D scans into grayscale image"
    tmp = np.array( scans ) / 5 # i.e. millimieters -> 0.5 (255 is then 1.275m)
    mask = tmp > 255
    tmp[mask] = 255
    return np.array( tmp, dtype=np.uint8 ) # scaling milimeters to 1m in uint8


def findApples( size, scans ):
    "try to find an apple(s) of given size"
    orig = np.array( scans ).T
    img = scans2img( scans )
    print img.shape, img.dtype
#    cv2.threshold( img, 128, 255, cv2.THRESH_BINARY )    
    g_mser = cv2.MSER( _delta = 8, _min_area=100, _max_area=30*20 )
    gray = img.T
    frame = cv2.cvtColor( img.T, cv2.COLOR_GRAY2BGR )
    contours = g_mser.detect(gray, None)

    ret = []
    for cnt in contours:
        (x1,y1),(x2,y2) = np.amin( cnt, axis=0 ), np.amax( cnt, axis=0 )
        if abs( (x2-x1)*MOTION_STEP_X - size ) < 0.01:
            print (x2-x1)*MOTION_STEP_X, (x1,y1),(x2,y2)
            box = np.int0([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])        
            cv2.drawContours( frame,[box],0,(255,0,0),2)
            if isItApple( orig[y1:y2,x1:x2] ):
                ret.append( ((x1,y1),(x2,y2)) )
                cv2.drawContours( frame,[box],0,(0,0,255),2)

    cv2.imshow('image', frame) # transposed matrix corresponds to "what we are used to" view
    cv2.imwrite( "tmp.png", frame )
    cv2.waitKey(0)
    return ret

def bruteForce( size, scans ):
    orig = np.array( scans ).T
    tmp = np.array( scans ) / 5
    mask = tmp > 255
    tmp[mask] = 255
    img = np.array( tmp, dtype=np.uint8 ) # scaling milimeters to 1m in uint8
    frame = cv2.cvtColor( img.T, cv2.COLOR_GRAY2BGR )
    winSizeX = winSizeY = int(size/MOTION_STEP_X)
    ret = []
    for minX in xrange( 200 ):
        print minX,
        for minY in xrange( 200 ):
            x1,x2,y1,y2 = minX, minX+winSizeX, minY, minY+winSizeY
            if isItApple( orig[y1:y2,x1:x2] ):
                box = np.int0([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])        
                ret.append( ((x1,y1),(x2,y2)) )
                cv2.drawContours( frame,[box],0,(0,0,255),2)
        print len(ret)
    cv2.imshow('image', frame) # transposed matrix corresponds to "what we are used to" view
    cv2.imwrite( "tmp.png", frame )
    cv2.waitKey(0)
    return ret


########## GENERATORS ###########
def exampleG( img ):
    "example generator for potential apple positions"
    yield 220,129
    yield 161,135

def denseAreaG( img ):
    "search for areas with dense occupancy within two thresholds"
    appleSize = 10
    gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )
    kernel = np.ones( (10,10), np.uint8)
    for level in xrange( appleSize, 256-appleSize ):
        tmp = gray.copy()
        mask = tmp < (level - appleSize/2)
        tmp[mask] = 0
        mask = gray > (level + appleSize/2)
        tmp[mask] = 0
        mask = (tmp != 0)
        tmp[mask] = 1
        tmp = cv2.filter2D( tmp, -1, kernel ) 
        y,x = np.unravel_index( tmp.argmax(), tmp.shape )
        yield (x, y)


#################################

def findApples2( size, scans, gen ):
    orig = np.array( scans ).T
    img = scans2img( scans )
    frame = cv2.cvtColor( img.T, cv2.COLOR_GRAY2BGR )
    winSizeX = int(size/MOTION_STEP_X)
    ret = []
    for x,y in gen( frame ):
        dist = orig[y][x]/1000.0
        print x,y, dist, frame.shape
        if dist < 0.1 or dist > 1.0:
            continue
        if x < winSizeX or x > frame.shape[1]-winSizeX:
            continue
        winSizeY = 1+int(math.degrees( size/float(dist) )) # just approximation with 1deg resolution
        print "winSizeY", winSizeY, frame.shape
        if y < winSizeY or y > frame.shape[0]-winSizeY:
            continue

        x1,x2,y1,y2 = x-winSizeX/2, x+winSizeX/2, y-winSizeY/2, y+winSizeY/2
        box = np.int0([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])
        cv2.drawContours( frame,[box],0,(255,0,0),2)
        if isItApple( orig[y1:y2,x1:x2] ):
            ret.append( ((x1,y1),(x2,y2)) )
            cv2.drawContours( frame,[box],0,(0,0,255),2)
        cv2.imshow('image', frame) # transposed matrix corresponds to "what we are used to" view
        cv2.waitKey(1)
    cv2.imwrite( "tmp.png", frame )
    cv2.waitKey(0)
    return ret


if __name__ == "__main__": 
    if len(sys.argv) < 3:
        print __doc__
        sys.exit(1)
#    print findApples( size=float(sys.argv[1]), scans=loadAllScans(sys.argv[2]) )
    print findApples2( size=float(sys.argv[1]), scans=loadAllScans(sys.argv[2]), gen=denseAreaG )

# vim: expandtab sw=4 ts=4

