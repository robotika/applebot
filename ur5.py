#!/usr/bin/python
"""
  Control of UR5 from Universal Robots
    usage:
         ./ur5.py <cmd> [<log file>]
"""

# http://www.zacobria.com/universal-robots-zacobria-forum-hints-tips-how-to/script-via-socket-connection/

import sys
import time
import socket
import math
import struct
import datetime

UR5_HOST = "192.168.1.51" # TODO 
UR5_PORT = 30002


# TODO:
# - verify units (degrees/rads and mm/meters?)
# - logging
# - extra thread?

def parseData( data, robot=None, verbose=False ):
    if len(data) < 5:
        return None
    totalLen, robotState = struct.unpack(">IB", data[:5] )
    assert robotState == 16, robotState
#    print totalLen
    if len(data) < totalLen:
        return None
    ret = data[totalLen:]
    data = data[5:totalLen] # length includes header
    while len(data) > 0:
        subLen, packageType = struct.unpack(">IB", data[:5] )
        if len(data) < subLen:
            return None
#        print packageType, subLen
        if packageType == 1:
            # Joint Data
            assert subLen == 251, subLen
            sumSpeed = 0
            for i in xrange(6):
                position, target, speed, current, voltage, temperature, obsolete, mode = \
                        struct.unpack(">dddffffB", data[5+i*41:5+(i+1)*41])
#                print i,speed
                sumSpeed += abs(speed)
                # 253 running mode
            if verbose:
                print sumSpeed
            if robot:
                robot.moving = (sumSpeed > 0.000111)
        elif packageType == 4:
            # Cartesian Info
            assert subLen == 53, subLen
            x,y,z, rx,ry,rz = struct.unpack( ">dddddd", data[5:subLen] )
            if verbose:
                print "%.3f, %.3f, %.3f,    %.3f, %.3f, %.3f" % (x,y,z, rx,ry,rz)
        data = data[subLen:]
    if verbose:
        print "------------"
    return ret

class UniversalRobotUR5:
    def __init__( self, replayLog=None ):
        self.acc = 0.13962634015954636
        self.speed = 0.10471975511965976
        self.moving = None # unknown
        if replayLog is None:
            self.replayLog = False
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((UR5_HOST, UR5_PORT))
            filename = datetime.datetime.now().strftime("logs/ur5_%y%m%d_%H%M%S.bin")    
            print filename
            self.logIn = open( filename, "wb" ) 
            self.logOut = open( filename.replace(".bin", ".cmd"), "wb" ) 
        else:
            self.replayLog = True

    def term( self ):
        if not self.replayLog:
            self.s.close()
            self.s = None

    def receiveData( self ):
        data = self.s.recv(4096)
        if len(data) > 0:
            self.logIn.write(data)
            self.logIn.flush()
            parseData( data, self )

    def sendCmd( self, cmd ):
        self.logOut.write( cmd )
        self.logOut.flush()
        self.s.send( cmd )
        self.receiveData()


    def movej( self, sixAngles ):
        assert len(sixAngles) == 6, sixAngles
        self.sendCmd("movej("+str(list(sixAngles)) + ", a=%f, v=%f)" % (self.acc, self.speed) + "\n")
        # or use t=<time> and r=<radius>
#        time.sleep(2.0) # keep it as part of movej? it should rather check positions and wait until it is complete

    def movel( self, sixAngles ):
        "move linearly"
        pass

    def testIO( self ):
#        self.s.send("set_digital_out(8,True)" + "\n") # tool 0
        self.s.send("set_digital_out(8,False)" + "\n") # tool 0
        data = self.s.recv(1024)
        print "Received", repr(data)


    def scan( self ):
        self.sendCmd("movej( p[0.139, -0.065, 0.869,    -1.311, 1.026, -0.869], a=0.1, v=0.1 )\n")
        for i in xrange(80):
            self.receiveData()
        self.sendCmd("movej( p[0.139, -0.065, 0.369,    -1.311, 1.026, -0.869], a=0.1, v=0.1 )\n")
        for i in xrange(80):
            self.receiveData()


    def goto( self, xyz ):
        self.sendCmd("movej( p[%f, %f, %f, -1.311, 1.026, -0.869], a=0.1, v=0.1 )\n" % xyz )
        for i in xrange(80):
            self.receiveData()
            if not self.moving:
                break



def testUR5( args ):
    replayLog = None
    if len(args) > 2:
        replayLog = args[2]
    robot = UniversalRobotUR5( replayLog )
#    robot.testIO()
#    robot.movej( [-0.5405182705025187, -2.350330184112267, -1.316631037266588, -2.2775736604458237, 3.3528323423665642, -1.2291967454894914] )
#    robot.movej( [math.radians(x) for x in [0, -90, 0, -90, 0, 0]] ) # straight position
#    robot.s.send("movej( p[0.2, 0.2, 0.6, 0, -2.2218, 2.2228], a=0.1, v=0.1 )\n") # p - cartesian coordinates :)

# display coordinates
#    robot.s.send('popup("hi")\n')
#    robot.s.send("def myProg():\nm = get_inverse_kin( get_target_tcp_pose())\npopup( m )\nend\nmyProg()\n")
#    robot.s.send("def myProg():\nm = get_target_tcp_pose()\npopup( m )\nend\nmyProg()\n")

#    robot.sendCmd("movej( p[0.143, -0.187, 0.187, 0.16, -2.37, 2.37], a=0.1, v=0.1 )\n")

#    robot.sendCmd("movej( p[-0.00782237301675, -0.228968253334, 0.511269468576, 0.16, -2.37, 2.37], a=0.1, v=0.1 )\n")
#    for i in xrange(10):
#        robot.receiveData()
#    robot.sendCmd("movej( p[0.0786829156856, -0.173025495873, 0.671427332353, 0.16, -2.37, 2.37], a=0.1, v=0.1 )\n")
#    for i in xrange(10):
#        robot.receiveData()

#    robot.scan()
#    robot.goto( (0.139, -0.065, 0.869) ) # top
    robot.goto( (0.4, 0.3, 0.5) ) # top
    robot.term()


if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    if sys.argv[1] == "parse":
        data = open(sys.argv[2],"rb").read()
        while data:
            data = parseData( data, verbose=True )
        sys.exit(0)
    testUR5( sys.argv )

# vim: expandtab sw=4 ts=4
