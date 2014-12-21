"""
  Threshold distance image with slide bar (fixed distance only)
  usage:
     ./applethreshold.py <filename>
"""
import sys
import cv2

import numpy as np

bins = np.arange(256).reshape(256,1)

def threshold( img, appleSize=10, twoLevels=True ):
  gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )
  def update( level ):
    tmp = gray.copy()
    mask = tmp < (level - appleSize/2)
    tmp[mask] = 255
    if twoLevels:
      mask = gray < level
      tmp[mask] = 254
    mask = gray > (level + appleSize/2)
    tmp[mask] = 255
    mask = (tmp < 254)
    tmp[mask] = 0
    if twoLevels:
      mask = (tmp == 254)
      tmp[mask] = 128
    cv2.imshow( 'threshold', tmp )

    mask = (tmp != 0 )
    bw = tmp.copy()
    bw[mask] = 0
    bw[~mask] = 2

    kernel = np.ones( (10,10), np.uint8)
    tmp = cv2.filter2D( bw, -1, kernel ) 
    y,x = np.unravel_index( tmp.argmax(), bw.shape )
    print x,y
    img2 = cv2.cvtColor( tmp, cv2.COLOR_GRAY2BGR )
    cv2.circle( img2, (x,y), 10, (0,0,255), 2 )
    cv2.imshow( 'image', img2 )
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

