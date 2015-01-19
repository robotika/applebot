#!/usr/bin/python
"""
  Try to find an apple in 3D scan
    usage:
         ./finder.py <apple size in meters> <motionStep> <log file>
"""

import sys
import math
import cv2
import numpy as np

from log2pgm import loadAllScans
from log2pts import MOTION_STEP_X
from apple import Apple

def isItApple( patch, motionStep ):
    a = Apple(patch, motionStep=motionStep)
    val = a.fitSphere( minRadius=0.03, maxRadius=0.15, maxDist=0.01, numIter=100 )
    desiredRatio = math.pi/4. # 0.78
    tolerance = 0.1
    if desiredRatio-tolerance < val < desiredRatio+tolerance:
        print "%.2f:" % val, "(%.3f, %.3f, %.3f)" % a.center, "%.3f" % a.radius
        return True
    return False

def scans2img( scans ):
    "convert array of 2D scans into grayscale image"
    tmp = np.array( scans ) / 5 # i.e. millimieters -> 0.5 (255 is then 1.275m)
    mask = tmp > 255
    tmp[mask] = 255
    return np.array( tmp, dtype=np.uint8 ) # scaling milimeters to 1m in uint8

def overlap( ((x1,y1),(x2,y2)), ((x3,y3),(x4,y4)) ):
    assert x1 < x2 and y1 < y2, ((x1,y1),(x2,y2))
    assert x3 < x4 and y3 < y4, ((x3,y3),(x4,y4))
    if x1 > x4 or x2 < x3:
        return False
    if y1 > y4 or y2 < y3:
        return False
    # TODO inside
    return True

def removeDuplicities( boxes ):
    "remove overlapping rectangles, 1st wins"
    if len(boxes) == 0:
        return boxes
    ret = [boxes[0]]
    for b in boxes:
        for c in ret:
            if overlap(b,c):
                break
        else:
            ret.append( b )
    return ret


def findApples1( size, scans ):
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
    for level in xrange( 40, 100 ): # i.e. from 20cm to 50cm
        tmp = gray.copy()
        mask = tmp < (level - appleSize/2)
        tmp[mask] = 0
        mask = gray > (level + appleSize/2)
        tmp[mask] = 0
        mask = (tmp != 0)
        tmp[mask] = 1
        tmp = cv2.filter2D( tmp, -1, kernel ) 
        y,x = np.unravel_index( tmp.argmax(), tmp.shape )
        yield (x, y), (level - appleSize/2, level + appleSize/2)


#################################

def findApples2( size, scans, gen, motionStep ):
    orig = np.array( scans ).T
    img = scans2img( scans )
    frame = cv2.cvtColor( img.T, cv2.COLOR_GRAY2BGR )
    winSizeX = int(size/motionStep)
    ret = []
    print "Image:", frame.shape[:2]
    for (x,y), (t1,t2) in gen( frame ):
        dist = orig[y][x]/1000.0
        if dist < 0.1 or dist > 1.0:
            continue
        if x < winSizeX or x > frame.shape[1]-winSizeX:
            continue
        winSizeY = 1+int(math.degrees( size/float(dist) )) # just approximation with 1deg resolution
        if y < winSizeY or y > frame.shape[0]-winSizeY:
            continue
        print dist, (x,y), "winSize:", (winSizeX, winSizeY), "t=", (t1,t2)

        x1,x2,y1,y2 = x-winSizeX/2, x+winSizeX/2, y-winSizeY/2, y+winSizeY/2
        box = np.int0([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])
        cv2.drawContours( frame,[box],0,(255,0,0),2)
        patch = orig[y1:y2,x1:x2].copy()
        mask = patch < (t1*5) # sigh raw mm readings vs. 0.l255 scaling
        patch[mask] = 0
        mask = patch > (t2*5)
        patch[mask] = 0
        if isItApple( patch, motionStep ):
            ret.append( ((x1,y1),(x2,y2)) )
            cv2.drawContours( frame,[box],0,(0,0,255),2)
        cv2.imshow('image', frame) # transposed matrix corresponds to "what we are used to" view
        cv2.waitKey(1)
    cv2.imwrite( "tmp.png", frame )
    cv2.waitKey(0)
    return removeDuplicities( ret )


#################################

def findApples3( size, scans, motionStep ):
    "looking for contours in dual-thresholded image"
    orig = np.array( scans ).T
    img = scans2img( scans )
    frame = cv2.cvtColor( img.T, cv2.COLOR_GRAY2BGR )

    ret = []
    appleSize = 10
    gray = cv2.cvtColor( frame, cv2.COLOR_BGR2GRAY )
    for level in xrange( 40, 100 ): # i.e. from 20cm to 50cm
        tmp = gray.copy()
        mask = tmp < (level - appleSize/2)
        tmp[mask] = 0
        mask = gray > (level + appleSize/2)
        tmp[mask] = 0
        contours, hierarchy = cv2.findContours( tmp, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
        winSizeY = 1+int(math.degrees( size*1000/float(level*5) )) # just approximation with 1deg resolution
        desiredArea = winSizeY*size/motionStep*math.pi/4.

        for cnt in contours:
            area = cv2.contourArea(cnt) #, oriented=True)
            x,y,w,h = cv2.boundingRect(cnt)
            if area > 10 and desiredArea*0.5 < area < desiredArea*1.5 and y > 45 and y+h < 225:
                # only in 180deg forward
                print level, area, area/desiredArea
                cv2.drawContours(frame, [cnt], -1, (0,255,0), 2)
                if len(ret) == 0:
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
                    ret.append( ((x,y),(x+w,y+h)) )

        cv2.imshow('image', frame) # transposed matrix corresponds to "what we are used to" view
        cv2.waitKey(1)
    cv2.waitKey(2000)
    return removeDuplicities( ret )



def findApples( size, scans, motionStep ):
    return findApples3( size, scans, motionStep=motionStep )


if __name__ == "__main__": 
    if len(sys.argv) < 4:
        print __doc__
        sys.exit(1)
    print findApples( size=float(sys.argv[1]), motionStep=float(sys.argv[2]), scans=loadAllScans(sys.argv[3]) )

# vim: expandtab sw=4 ts=4

