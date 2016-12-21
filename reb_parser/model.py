class Reb(object):
    '''Describes a parsed Reb file'''
    def __init__(self):
        self.created_by = None      # Name of computer that created this reb, if available
        self.source_path = None     # Path where the reb was initially saved
        self.op = None        # Operator name

        self.event_id = None
        self.raw = None             # Raw contents of reb file

        self.origin = Origin()

    def toDict(self):
        out = dict((k,self.__dict__[k]) for k in ['created_by','source_path', 'operator',
            'event_id', 'raw'])
        out['origin'] = self.origin.toDict()
        return out
        

class Origin(object):
    def __init__(self):
        self.id = None              # OriginID from reb file
        self.time = None            # GMT date and time at which the event occured
        self.time_raw = None        # The raw text of date and time from the reb file
        self.time_err = None
        self.rms = None
        self.lat = None
        self.lon = None
        self.region = None
        self.smaj = None
        self.smin = None
        self.az = None
        self.depth = None
        self.depth_err = None
        self.ndef = None
        self.nsta = None
        self.gap = 98
        self._mdist = None          # this is the mdist field
        self.mdist = None           # this is the Mdist field (capital leter)
        self.qual = None
        self.author = None

        self.magnitudes = []
        self.arrivals = []

    def toDict(self):
        out = dict((k,self.__dict__[k]) for k in ['id','time', 'time_raw', 'time_err',
            'rms', 'lat', 'lon', 'region', 'smaj', 'smin', 'az', 'depth', 'depth_err',
            'ndef', 'nsta', 'gap', '_mdist', 'qual', 'author'])

        out['time'] = out['time'].isoformat()
        out['magnitudes'] = [m.toDict() for m in self.magnitudes]
        out['arrivals'] = [a.toDict() for a in self.arrivals]

        return out
        

class Magnitude(object):
    def __init__(self):
        self.type = None
        self.val = None
        self.err = None
        self.nsta = None
        self.author = None

    def toDict(self):
        out = dict((k,self.__dict__[k]) for k in ['type','val', 'err', 'nsta', 'author'])
        return out
        

class Arrival(object):
    def __init__(self):
        self.sta = None
        self.dist = None
        self.ev_az = None
        self.phase = None
        self.time = None        # Date and time of this phase
        self.t_res = None
        self.azim = None
        self.az_res = None
        self.slow = None
        self.s_res = None
        self.the_def = None     # Can't have self.def because of reserved keyword
        self.snr = None
        self.amp = None
        self.per = None
        self.qual = None
        self.magnitude_type = None
        self.magnitude_val = None
        self.id = None          # ArrID from reb file

    def toDict(self):
        out = dict((k,self.__dict__[k]) for k in ['sta', 'dist', 'ev_az', 'phase', 'time',
            't_res', 'azim', 'az_res', 'slow', 's_res', 'the_def', 'snr', 'amp', 'per',
            'qual', 'magnitude_type', 'magnitude_val', 'id'])
        out['time'] = out['time'].isoformat()
        return out
