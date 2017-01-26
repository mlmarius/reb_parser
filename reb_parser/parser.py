 # -*- coding: utf-8 -*-

'''
Parse a buffer of text containing a reb file into reb objects
'''

from collections import deque
from model import *
import re
from datetime import datetime
import pytz
import json
import logging



logger = logging.getLogger('rebparser')
# handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger.addHandler(handler)
# handler.setFormatter(formatter)
# logger.setLevel(logging.DEBUG)

class RebFile(Reb):
    """Parse a rebfile containing a single REB"""
    def __init__(self, filePath):
        super(RebFile, self).__init__()
        self.source_path = filePath

        with open(self.source_path, 'rb') as f:
            self.raw = f.read()

        self.lines = deque([line.strip() for line in self.raw.split("\n") if line.strip() != ''])   # fetch the lines

        self.regularExpressions = {
            "matchOriginData": re.compile('^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{2}\s+'),
            "matchMagnitudeVal": re.compile('^[a-z]{2}\s+([\d\.]+)\s+([\d\.]+\s+)?[0-9]+\s+.*'),
            "matchPhaseInfo": re.compile('^[A-Z\d]+\s+([\d\.]+)\s+([\d\.]+)\s+[PS{}nmb]+\s+\d{2}:\d{2}:\d{2}\.\d{3}.*')
        }

        self.parserStack = [
            self.parseRebHeader,
            self.parseOriginHeader,
            self.parseOriginData,
            self.parseMagnitudeHeader,
            self.parseMagnitudeData,
            self.parseArrivalHeader,
            self.parseArrivalData
        ]
        self.parserMatches = dict((f,0) for f in self.parserStack)
        try:
            self.parse()
        except IndexError:
            logger.debug("bulletin parsing complete")
            return

    def parse(self):
        '''
        Try all parsers in order for each line.
        If all parsers fail, remove the current line from the stack of lines
        and attempt all parsers on the next line until all lines are exhausted
        '''
        while len(self.lines):
            for parser in self.parserStack:
                self.runparser(parser)
            logger.info("Parsers exhausted. Removing a line from lines")
            self.lines.popleft()


    def runparser(self, parser):
        status = "[% 30s] - %s" % (parser.__name__, self.lines[0])
        logger.debug(status)
        while parser(self.lines[0]) is True:
            self.lines.popleft()
            # print "parser succeeded!"
            # for line in self.lines:
            #     print line

    def parseRebHeader(self, line):
        # Antelope Linux_a2  REB - Event       12  Transilvania, judetul Alba                                      Op: Daniel Paulescu•••••
        if "REB - Event" not in line:
            return False

        try:
            id_region, op = map(str.strip, line.split('REB - Event')[1].split('Op: '))
        except ValueError:
            # sometimes rebs have no operator
            id_region = line.split('REB - Event')[1].strip()
            op = None
            
        id_region = re.sub(r'\s+',' ', id_region).strip().split(' ')
        event_id = id_region[0]
        region = ' '.join(id_region[1:]).strip()
        self.event_id = event_id
        self.operator = op
        self.origin = Origin()
        self.origin.region = region
        return True

    def parseOriginHeader(self, line):
        # Date          Time        Err   RMS Latitude Longitude  Smaj  Smin  Az Depth   Err Ndef Nsta Gap  mdist  Mdist Qual   Author      OrigID
        if "Date          Time        Err   RMS Latitude Longitude  Smaj  Smin  Az Depth   Err Ndef Nsta Gap  mdist  Mdist Qual   Author      OrigID" in line:
            return True
        return False

    def parseOriginData(self, line):
        # 2016/12/07 02:11:31.47   0.33  0.60  42.6517   18.4457   3.4   2.3 110   5.0f  0.0   21   11 156   0.64   5.50 m i ke NIEP:rt m       13
        if self.regularExpressions.get('matchOriginData').match(line.strip()) is None:
            return False

        year = int(line[0:4])
        month = int(line[5:7])
        day = int(line[8:10])
        hour = int(line[11:13])
        minute = int(line[14:16])
        second = int(line[17:19])
        milisecond = int(line[20:22]+"0000")
        latitude = float(line[36:44].strip())
        longitude = float(line[46:54].strip())
        depth = float(line[71:76].strip())
        dt = datetime( year, month, day, hour, minute, second, milisecond, tzinfo = pytz.utc )
        self.origin.time = dt
        self.origin.time_raw = line[:22]
        self.origin.lat = latitude
        self.origin.lon = longitude
        self.origin.depth = depth
        self.origin.time_err = line[22:30].strip()
        self.origin.rms = float(line[30:36].strip())
        self.origin.smaj = line[54:61].strip()
        self.origin.smin = line[61:66].strip()
        self.origin.az = line[66:70].strip()
        self.origin.depth_err = line[76:82].strip()
        self.origin.ndef = line[87:92].strip()
        self.origin.gap = line[92:96].strip()
        self.origin._mdist = line[96:103].strip()
        self.origin.mdist = line[103:110].strip()
        self.origin.qual = line[110:117].strip()
        return True


    def parseMagnitudeHeader(self, line):
        # Magnitude   Err Nsta Author      OrigID
        if "Magnitude   Err Nsta Author      OrigID" not in line:
            return False
        return True

    def parseMagnitudeData(self, line):
        # ml   2.5  0.25     8 dbevproc        13

        if self.regularExpressions.get('matchMagnitudeVal').match(line) is None:
            return False

        magType = line[0:2].strip()
        magVal = float(line[5:9])
        mag = Magnitude()
        mag.type = magType
        mag.val =  magVal
        mag.err = line[10:16].strip()
        mag.nsta = int(line[16:20].strip())
        mag.author = line[20:31].strip()
        self.origin.magnitudes.append(mag)
        return True

    def parseArrivalHeader(self, line):
        # Sta     Dist  EvAz Phase        Time      TRes  Azim AzRes   Slow   SRes Def   SNR       Amp   Per Qual Magnitude    ArrID
        if "Sta     Dist  EvAz Phase        Time      TRes  Azim AzRes   Slow   SRes Def   SNR       Amp   Per Qual Magnitude    ArrID" not in line:
            return False
        return True

    def parseArrivalData(self, line):
        #PDG     0.64 110.0 P        02:11:43.144  -0.6                           T__             0.3       mc_ ml      2.4       11
        if self.regularExpressions.get('matchPhaseInfo').match(line) is None:
            return False

        arrival = Arrival()
        arrival.sta = line[0:5].strip()
        arrival.dist = line[5:12].strip()
        arrival.evAz = line[13:18].strip()
        arrival.phase = line[19:21].strip()
        arrival.t_res = line[40:46].strip()
        arrival.the_def = line[72:76].strip()
        arrival.amp = line[88:92].strip()
        arrival.qual = line[98:102].strip()
        arrival.magnitude_type = line[102:106].strip()
        arrival.magnitude_val = line[110:115].strip()
        arrival.id = line[115:].strip()

        if arrival.phase not in 'SP':
            #not a bad line maybe but not a good phase. we let the parser continue
            return True

        time = line[28:40]+"000"
        hour, minute, second, milisecond = map( (lambda x: int(x)), re.split('[:\.]',time))

        originDate = self.origin.time

        dt = datetime( originDate.year , originDate.month, originDate.day, hour, minute, second, milisecond, tzinfo = pytz.utc )
        arrival.time = dt
        self.origin.arrivals.append(arrival)
        return True

