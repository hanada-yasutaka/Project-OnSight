#!/usr/bin/env python

from MapSystem import *
import numpy

class PhaseSpace2d(object):
    def __init__(self, range, hdim=100):
        self.range = range
        self.hdim = hdim
class Hole(PhaseSpace2d):
    def __init__(self, bsetting):
        self.bsetting = bsetting
        # example
        bsetting = [ (True, [0.0,0.1], [0.2,0.3]), (False, []) ]

class Perturbation(PhaseSpace2d):
    def __init__(self, persetting):
        self.persetting = persetting
        # example
        persetting = [ (False, []), (True, [-0.5, 0.5]) ]


class WaveFunction(PhaseSpace2d):
    def __init__(self, range, hdim):
        PhaseSpace2d.__init__(self, range, hdim)
    def del_q(self, q_c):
        print self.range, self.hdim
    def del_p(self, p_c):
        pass
    def coherent(self, q_c, p_c):
        pass
    def quantized_linear_tori(self, p_c):
        # see peper written by ishikawa ( Recovery of chaotic tunneling due to destruction of dynamical localization by external noise)
        pass
class Representation(PhaseSpace2d):
    def __init__(self, range, hdim):
        PhaseSpace2d.__init__(self, range, hdim)
        self.wave = WaveFunction(range, hdim)
    def p_rep(self):
        pass
    def q_rep(self):
        pass
    def hsm_rep(self):
        pass
    def wigner_rep(self):
        pass
    
class Qmap(PhaseSpace2d):
    def __init__(self, map, range, hdim):
        self.map = map
        PhaseSpace2d.__init__(self, range, hdim)
        self.q = numpy.arange(self.range[0][0], self.range[0][1], (self.range[0][1] - self.range[0][0])/self.hdim)
        self.p = numpy.arange(self.range[1][0], self.range[1][1], (self.range[1][1] - self.range[1][0])/self.hdim)
    def set_inipacket(self):
        self.wave = WaveFunction(self.range, self.hdim)
        # use initial setting of wavefunction
        #x_c = int(x_in*hdim)/float(hdim)
    def evolve(self):
        pass
    def eigen_val(self):
        pass
        print self.range
    def set_range(self, range, hdim):
        self.range = range
        self.hdim = hdim
        self.q = numpy.arange(self.range[0][0], self.range[0][1], (self.range[0][1] - self.range[0][0])/self.hdim)
        self.p = numpy.arange(self.range[1][0], self.range[1][1], (self.range[1][1] - self.range[1][0])/self.hdim)
    def get_range(self):
        print self.range, self.hdim
class QmapSystem(object):
    def __init__(self, map):
        if isinstance(map, Symplectic2d) != True: raise TypeError
        self.map = map
        self.hdim = 100
        self.QMapName = map.__class__.__name__
        try:
            setting = self.map.Psetting
            self.range=[]
            for set in setting:
                if set[0]: self.range.append((0.0, set[1]))
                else: self.range.append((0.0, 1.0))
        except: self.range = [(0.0, 1.0), (0.0, 1.0)]
        try: self.Bsetting = self.map.Bsetting
        except: self.Bsetting = None
        
        self.qmap = Qmap(self.map, self.range, self.hdim)
    def set_range(self, qmin, qmax, pmin, pmax, hdim):
        self.range = [(qmin, qmax), (pmin, pmax)]
        self.hdim = hdim
        self.qmap.set_range(self.range, hdim)
        self.qmap.get_range()
    def set_inipacket(self):
        self.qmap.set_inipacket()

        
        
        
if __name__ == '__main__':
    map = StandardMap()
    #Space(2, False)x
    qmap = QmapSystem(map)
    qmap.set_range(0.0, 2.0, -1.0, 1.0, 100)
