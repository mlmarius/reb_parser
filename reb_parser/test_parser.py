import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__,'../../')))
from glob import glob


from reb_parser.parser import RebFile
if __name__ == "__main__":
    testdir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'testdata')
    for testfile in glob(os.path.join(testdir,'*')):
        print "now parsing %s" % testfile
        rf = RebFile(testfile)
        # print rf.toDict()
        # print "\n\n\n"
        # print rf.raw
