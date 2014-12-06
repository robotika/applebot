"""
  Apple detection class
"""

import sys
import math
import cv2
import numpy as np

class Apple:
    def __init__( self, patch ):
        w,h = patch.shape
        inside = patch[w/4:3*w/4,h/4:3*h/4]
        print np.amax(inside) - np.amin(inside)
        print inside

    def fitSphere( self ):
        return 0.5 # maybe yes, maybe not

