#!/usr/bin/python
"""
  Compose large from several vertical strips
    usage:
         ./imstrips.py <directory> <strip width>
"""
# Hints:
# http://stackoverflow.com/questions/7670112/finding-a-subimage-inside-a-numpy-image
# http://stackoverflow.com/questions/7589012/combining-two-images-with-opencv


import sys
import os
import cv2
import numpy as np

def imstrips( directory, width ):
    ret = None
    for filename in os.listdir( directory ):
        if filename.endswith(".jpg"):
            img = cv2.imread( directory + "/" + filename )
            print filename, img.shape
            cX = img.shape[1]/2
            subimg = img[:, cX-width/2:cX+width/2]
            if ret is None:
                ret = subimg.copy()
            else:
                ret = np.concatenate( (ret, subimg), axis=1 )
    return ret


if __name__ == "__main__": 
    if len(sys.argv) < 3:
        print __doc__
        sys.exit(1)
    img = imstrips( sys.argv[1], int(sys.argv[2]) )
    if img is not None:
        cv2.imshow( "image", img )
        cv2.waitKey(0)
        cv2.imwrite( "tmp.jpg", img )

# vim: expandtab sw=4 ts=4

