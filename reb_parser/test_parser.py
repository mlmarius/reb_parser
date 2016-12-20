import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__,'../../')))

from reb_parser.parser import RebFile
if __name__ == "__main__":
    rf = RebFile('testdata/2015198_10_16_38')
    print rf.toDict()
    print "\n\n\n"
    print rf.raw
