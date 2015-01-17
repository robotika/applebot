#!/usr/bin/python
"""
  Applebot ver0 demo
    usage:
         ./demo.py <???>
"""

import os
import sys
import time
import datetime

from threading import Thread,Event,Lock 
from dualcam import recordStream
from scan3d import scan, takePicture
from ur5 import UniversalRobotUR5, SCAN_TOP_XYZ
from finder import findApples

sys.path.append( ".."+os.sep+"eduro") 
import laser 

class H264Camera( Thread ):
    def __init__( self ):
        Thread.__init__(self)
        self.setDaemon(True) 
    def run( self ):
        recordStream( datetime.datetime.now().strftime("logs/video_%y%m%d_%H%M%S.bin") )


class Laser3D( Thread ):
    def __init__( self ):
        Thread.__init__(self)
        self.setDaemon(True) 
        self.laser = laser.LaserIP()
        filename = datetime.datetime.now().strftime("logs/scan_%y%m%d_%H%M%S.txt")    
        print filename
        self.f = open( filename, "w" )
        self.laser.startLaser()
        self.shouldIRun = Event()
        self.shouldIRun.set()
        self.collect = False
        self.scan = []

    def run( self ):
        print "laser running ..."
        i = 0
        while self.shouldIRun.isSet(): 
            if i % 10 == 0:
                takePicture( i/10 )
            data, reminision = self.laser.internalScan()
            self.f.write( str( (data, reminision) ) + '\n' )
            self.f.flush()
            if self.collect:
                self.scan.append( (data,reminision) )        
            i += 1
        self.f.close() 

    def requestStop(self):
        self.shouldIRun.clear() 

    def startCollect( self ):
        self.collect = True
        self.scan = []

    def stopCollect( self ):
        self.collect = False

    def getScan( self ):
        return self.scan # TODO extract only distance data, maybe some thread-locks


def demo():
    camera = H264Camera()
    scanner = Laser3D()
    camera.start()
    scanner.start()

    robot = UniversalRobotUR5()
    robot.openGripper()
    robot.goto( SCAN_TOP_XYZ ) # initial scan position
    scanner.startCollect()
    robot.scan()
    scanner.stopCollect()
    scan = scanner.getScan()

    # dump scan for further analysis
    filename = datetime.datetime.now().strftime("logs/snapshot_%y%m%d_%H%M%S.txt")
    f = open( filename, "w" )
    f.write( str(scan) )
    f.close()
    
    #apples = findApples( APPLE_SIZE, scan )
    apples = [(1,2,3)]
    for apple in apples:
        print "Apple", apple
        # TODO conversion image -> xyz
        robot.goto( (0.3693, 0.291, 0.279) ) # pick apple
        robot.closeGripper()
        robot.goto( (0.3693, 0.291, 0.1) ) # drop apple
        robot.openGripper()
    robot.term()
    scanner.requestStop()
    scanner.join()

if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    laser.HOST, laser.PORT = '192.168.1.156', 2111 
    demo()

# vim: expandtab sw=4 ts=4

