"""
  Apple detection class
"""

import sys
import math
import random
import cv2
import numpy as np

class Apple:
    def __init__( self, patch=None, motionStep=None ):
        self.center, self.radius = None, None
        if patch is not None:
            self.data = patch.copy()
        else:
            self.data = None
        self.motionStep = motionStep
        self.random = random.Random(0).choice


    def _symetryPlane( self, A, B ):
        "return plane of symetry for two points"
        # plane defined as a*x + b*y + c*z + d = 0
        v = (B[0]-A[0], B[1]-A[1], B[2]-A[2])
        d = -v[0]*(A[0]+B[0])/2.0 -v[1]*(A[1]+B[1])/2.0 -v[2]*(A[2]+B[2])/2.0
        return v,d

    def _dist( self, A, B ):
        "return distance of two 3D points"
        return math.sqrt( (A[0]-B[0])**2 + (A[1]-B[1])**2 + (A[2]-B[2])**2 )

    def sphere( self, fourPoints ):
        "return center and radius of corresponding sphere"
        # None - for not properly defined sphere (for example colinear input points)
        assert len(fourPoints) == 4, fourPoints
        A, B, C, D = fourPoints

        # center is insersection of 3 planes
        pAB = self._symetryPlane( A, B )
        pBC = self._symetryPlane( B, C )
        pCD = self._symetryPlane( C, D )

        # solve a*x = b
        a = np.array( [pAB[0], pBC[0], pCD[0]] )
        b = np.array( [-pAB[1], -pBC[1], -pCD[1]] )
        try:
            center = tuple(np.linalg.solve( a, b ).tolist())
        except np.linalg.LinAlgError:
            return None, None
        return center, self._dist( center, A )



    def points( self ):
        ret = []
        x = 0.0
        for arr in self.data.T.tolist():
            for i, a in enumerate(arr):
                angle = math.radians(i-len(arr)/2)
                dist = a/1000.0
                if a != 0:
                  ret.append( (x, dist*math.cos(angle), dist*math.sin(angle)) )
            x += self.motionStep
        return ret


    def saveAsCloud( self, filename ):
        f = open( filename, "w" )
        for x,y,z in self.points():
            f.write( "%.3f %.3f %.3f\n" % (x, y, z) )
        f.close()


    def fitSphere( self, maxDist=0.02, numIter=100, minRadius=None, maxRadius=None ):
        pts = self.points()
        best = None
        self.center, self.radius = None, None
        for it in xrange(numIter):
            center, radius = self.sphere( [self.random(pts) for i in xrange(4)] )
            if center is not None:
                count = 0
                for p in pts:
                    if abs(self._dist(center, p)-radius) < maxDist:
                        count += 1
                if best is None or count > best:
                    if minRadius is None or minRadius < radius < maxRadius:
                        self.center, self.radius = center, radius
                        best = count
        if best is None:
            return None
        return best/float(len(pts))

