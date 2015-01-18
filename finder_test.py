from finder import *
import unittest

class FinderTest( unittest.TestCase ): 
    def testRemoveDuplicities( self ):
        self.assertEqual( removeDuplicities([]), [] )
        self.assertEqual( removeDuplicities( 
            [((118, 164), (142, 176)), ((122, 168), (146, 180)), 
             ((118, 164), (142, 176)), ((118, 164), (142, 176)),] ),
            [((118, 164), (142, 176))] )

        self.assertEqual( removeDuplicities([((0,0),(1,1)), ((3,3),(4,4))]), [((0,0),(1,1)), ((3,3),(4,4))] )

if __name__ == "__main__":
    unittest.main() 

# vim: expandtab sw=4 ts=4

