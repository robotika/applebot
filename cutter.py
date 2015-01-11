"""
  Simple tool for cutting sub-scans/images with access to higher resolution
  usage:
     ./cutter.py <filename>
"""
# based on OpenCV2 sample mouse_and_match.py

import sys
import cv2

import numpy as np

drag_start = None
sel = (0,0,0,0)

def onmouse(event, x, y, flags, param):
    global drag_start, sel
    if event == cv2.EVENT_LBUTTONDOWN:
        drag_start = x, y
        sel = 0,0,0,0
    elif event == cv2.EVENT_LBUTTONUP:
        if sel[2] > sel[0] and sel[3] > sel[1]:
            patch = gray[sel[1]:sel[3],sel[0]:sel[2]]            
            cv2.imshow("patch", cv2.resize( patch, (0,0), fx=16, fy=16, interpolation=cv2.INTER_NEAREST ) )
        drag_start = None
    elif drag_start:
        if flags & cv2.EVENT_FLAG_LBUTTON:
            minpos = min(drag_start[0], x), min(drag_start[1], y)
            maxpos = max(drag_start[0], x), max(drag_start[1], y)
            sel = minpos[0], minpos[1], maxpos[0], maxpos[1]
            img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            cv2.rectangle(img, (sel[0], sel[1]), (sel[2], sel[3]), (0,255,255), 1)
            cv2.imshow("gray", img)
        else:
            print "selection is complete"
            drag_start = None


def cutter( img ):
    cv2.imshow("gray",img)
    cv2.waitKey()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    img = cv2.imread( sys.argv[1], cv2.CV_LOAD_IMAGE_COLOR )

    # note, that callback has to be set in main code otherwise it crashes :(
    cv2.namedWindow("gray",1)
    cv2.setMouseCallback("gray", onmouse)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cutter( img )
    cv2.destroyAllWindows()
# vim: expandtab sw=4 ts=4
