"""
  Threshold distance image with slide bar (fixed distance only)
  usage:
     ./applethreshold.py <filename>
"""
import sys
import cv2

import numpy as np

bins = np.arange(256).reshape(256,1)

def threshold( img, appleSize=10 ):
  gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )
  def update( level ):
    tmp = gray.copy()
    mask = tmp < (level - appleSize/2)
    tmp[mask] = 255
    mask = tmp > (level + appleSize/2)
    tmp[mask] = 255
    mask = (tmp != 255)
    tmp[mask] = 0
    cv2.imshow( 'image', tmp )
  ret, binary = cv2.threshold( gray, 0, 255, cv2.THRESH_OTSU )
  update( int(ret) )
  cv2.createTrackbar( "threshold", "image", 0, 256, update )
  cv2.setTrackbarPos( "threshold", "image", int(ret) )
  cv2.waitKey()
  cv2.destroyAllWindows()

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print __doc__
    sys.exit(1)
  img = cv2.imread( sys.argv[1], cv2.CV_LOAD_IMAGE_COLOR )
  threshold( img )

