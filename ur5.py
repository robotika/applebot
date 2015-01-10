#!/usr/bin/python
"""
  Control of UR5 from Universal Robots
    usage:
         ./ur5.py <cmd>
"""

# http://www.zacobria.com/universal-robots-zacobria-forum-hints-tips-how-to/script-via-socket-connection/

import sys
import time
import socket

UR5_HOST = "192.168.1.18" # TODO 
UR5_PORT = 30002


# TODO:
# - verify units (degrees/rads and mm/meters?)
# - logging
# - extra thread?


class UniversalRobotUR5:
    def __init__( self ):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((UR5_HOST, UR5_PORT))
        self.acc = 1.3962634015954636
        self.speed = 1.0471975511965976

    def term( self ):
        self.s.close()
        self.s = None

    def movej( self, sixAngles ):
        assert len(sixAngles) == 6, sixAngles
        self.s.send("movej("+str(list(sixAngles)) + ", a=%f, v=%f)" % (self.acc, self.speed) + "\n")
        # or use t=<time> and r=<radius>
        time.sleep(2.0) # keep it as part of movej? it should rather check positions and wait until it is complete

    def movel( self, sixAngles ):
        "move linearly"
        pass

    def testIO( self ):
        self.s.send("set_digital_out(2,True)" + "\n")
        data = self.s.recv(1024)
        print "Received", repr(data)


def testUR5( cmd ):
    robot = UniversalRobotUR5()
    robot.testIO()
#    robot.movej( [-0.5405182705025187, -2.350330184112267, -1.316631037266588, -2.2775736604458237, 3.3528323423665642, -1.2291967454894914] )
    robot.term()


if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    testUR5( sys.argv[1] )

# vim: expandtab sw=4 ts=4
