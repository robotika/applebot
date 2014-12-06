"""
  Apple detection class
"""

import sys
import math
import cv2
import numpy as np

from log2pts import MOTION_STEP_X

class Apple:
    def __init__( self, patch ):
        self.data = patch.copy()


    def fitSphere( self ):
        # TODO
        return 0.5 # maybe yes, maybe no


    def points( self ):
        ret = []
        x = 0.0
        for arr in self.data.T.tolist():
            for i, a in enumerate(arr):
                angle = math.radians(i-len(arr)/2)
                dist = a/1000.0
                ret.append( (x, dist*math.cos(angle), dist*math.sin(angle)) )
            x += MOTION_STEP_X 
        return ret


    def saveAsCloud( self, filename ):
        f = open( filename, "w" )
        for x,y,z in self.points():
            f.write( "%.3f %.3f %.3f\n" % (x, y, z) )
        f.close()

