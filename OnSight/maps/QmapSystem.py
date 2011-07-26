#!/usr/bin/env python

from MapSystem import *
import numpy
import numpy.fft
import pylab


towpi = 2.0*numpy.pi

class PhaseSpace2d(object):
    def __init__(self, range, hdim=100):
        self.range = range
        self.hdim = hdim
        self.h = (self.range[0][1] - self.range[0][0]) * (self.range[1][1] - self.range[1][0])/float(self.hdim)
        self.q = numpy.arange(self.range[0][0], self.range[0][1], (self.range[0][1] - self.range[0][0])/self.hdim)
        self.p = numpy.arange(self.range[1][0], self.range[1][1], (self.range[1][1] - self.range[1][0])/self.hdim)
    def get_scaleinfo(self):
        info = {'qmin' : self.range[0][0], 'qmax': self.range[0][1],
                'pmin' : self.range[1][0], 'pmax': self.range[1][1],
                'h': self.h, 'hdim' : self.hdim }
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
        self.vec = numpy.zeros(self.hdim, dtype=numpy.complex128)
    def del_q(self, q_in):
        d = self.range[0][1] - self.range[0][0]
        s = int(round(self.q.min()*self.hdim/d))
        qq = numpy.arange(s, s+self.hdim, 1, dtype=int)
        q_c = int(round(q_in*self.hdim/d))
        index = numpy.where(qq == q_c)[0]
        self.vec[index] = 1.0
        return self.vec
    def del_p(self, p_c):
        pass
    def cs_qvec(self, q_c, p_c):
        d = self.range[0][1] - self.range[0][0]
        long_q = numpy.linspace(self.range[0][0] - d, self.range[0][1] + d, 3.0 * self.hdim) 
        q = numpy.linspace(self.range[0][0], self.range[0][1], self.hdim)
        coh_state = self.coherent_state_q(long_q, q_c, p_c)
        coh_state = coh_state / numpy.sum(numpy.abs(coh_state))
        vec = numpy.zeros(self.hdim, dtype=numpy.complex128)
        m = len(coh_state)/self.hdim
        coh_state2 = coh_state.reshape(m,len(q))
        for i in range(m):
            vec += coh_state2[i][::1]
        self.vec = vec / numpy.sum(numpy.abs(vec))
        return self.vec
    def coherent_state_q(self, q_in, q_c, p_c):
        q = q_in/numpy.sqrt(self.h/towpi)
        z = q_c/numpy.sqrt(self.h/numpy.pi) + p_c*1.j/numpy.sqrt(self.h/numpy.pi)
        zz = z*z
        tmp = -numpy.abs(z)*numpy.abs(z)/2.0 \
            - (q*q + zz.real)/2.0 + numpy.sqrt(2.0)*q*z.real\
            + 1.j *( - zz.imag/2.0 + numpy.sqrt(2.0)*q*z.imag)         
        res = numpy.exp(tmp)*numpy.sqrt(2.0 / self.h)
        return res
    def quantized_linear_tori(self, p_c):
        # see peper written by ishikawa ( Recovery of chaotic tunneling due to destruction of dynamical localization by external noise)
        pass
class Representation(PhaseSpace2d):
    def __init__(self, range, hdim):
        PhaseSpace2d.__init__(self, range, hdim)
        self.wave = WaveFunction(range, hdim)
    def get_p_rep(self, vec):
        return self.q, vec
    def q_rep(self):
        pass

class PhaseSpaceRep(Representation):
    def __init__(self, range, hdim):
        Representation.__init__(self, range, hdim)
        self.wave = WaveFunction(range, hdim)
    def set_vrange(self, vrange, grid):
        self.vrange = vrange
        self.grid = grid
    def hsm_rep(self, target):
        cs_dq = (self.vrange[0][1] - self.vrange[0][0]) / self.grid[0]
        cs_dp = (self.vrange[1][1] - self.vrange[1][0]) / self.grid[1]
        hsm_img = numpy.zeros((self.grid[0], self.grid[1]))
        for i in range(self.grid[1]):
            for j in range(self.grid[0]):
                cs_p = self.vrange[1][0] + i*cs_dp
                cs_q = self.vrange[0][0] + j*cs_dq
                cs_vec = self.wave.cs_qvec(cs_q, cs_p)
                sum = numpy.sum(target*numpy.conj(cs_vec)) 
                hsm_img[i][j] = numpy.abs(sum) * numpy.abs(sum)
        return hsm_img
    def wigner_rep(self):
        pass
class Qmap(PhaseSpace2d):
    def __init__(self, map, range, hdim):
        self.map = map
        PhaseSpace2d.__init__(self, range, hdim)
        self.rep = PhaseSpaceRep(range, hdim)
        self.rep.set_vrange(range,(50,50))
    def set_state(self, x_c, p_c, state):
        self.wave = WaveFunction(self.range, self.hdim)
        print x_c, p_c,state
        if state in ('q'): self.ivec = self.wave.del_q(x_c)
        elif state in ('p'): pass #self.wave.del_p(p_c)
        elif state in ('cs'): self.ivec = self.wave.cs_qvec(x_c,p_c)
        elif state in ('qlt'): pass
        else: raise TypeError
    def free_operator(self, isShift=True):
        print self.range, self.hdim, self.h
        if isShift:
            sp = numpy.fft.fftshift(self.p)
            tfunc = self.map.ifunc1(sp)
        else:
            tfunc = self.map.ifunc1(self.p)
        return numpy.exp(-towpi*1.j* tfunc/self.h)
    def kick_operator(self, isShift=False):
        if isShift:
            sq = numpy.fft.fftshift(self.q)
            vfunc = self.map.ifunc0(sq)
        else:
            vfunc = self.map.ifunc0(self.q)
        return numpy.exp(-towpi*1.j*vfunc /self.h)
    def evolve(self):
        freeop = self.free_operator(isShift=True)
        kickop = self.kick_operator(isShift=False)
        vec1 = kickop * self.ivec
        vec2 = numpy.fft.fft(vec1)
        vec1 = freeop * vec2
        vec2 = numpy.fft.ifft(vec1)
        return vec2
    def eigen_val(self):
        pass
        print self.range
    def set_range(self, range, hdim):
        self.range = range
        self.hdim = hdim
        self.h = (self.range[0][1] - self.range[0][0]) * (self.range[1][1] - self.range[1][0])/float(self.hdim)
        self.q = numpy.arange(self.range[0][0], self.range[0][1], (self.range[0][1] - self.range[0][0])/self.hdim)
        self.p = numpy.arange(self.range[1][0], self.range[1][1], (self.range[1][1] - self.range[1][0])/self.hdim)
    def get_range(self):
        return self.range, self.hdim
    def set_vrange(self, vrange, grid):
        self.rep.set_vrange(vrange, grid)
    def husimi_rep(self, target):
        return self.rep.hsm_rep(target)
        
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
 
    def set_inipacket(self, state, *args):
        if type(state) != str: raise ValueError
        if state in ('q') and len(args) == 1:
            self.qmap.set_state(args[0], None, 'q')
        elif state in ('p') and len(args) == 1:
            self.qmap.set_state(None, args[0], 'p')
        elif state in ('cs') and len(args) == 2:
            print len(args)
            self.qmap.set_state(args[0], args[1], 'cs')
        else: raise ValueError
    def evolves(self, iter, dt):
        self.qmap.evolve()
    def get_prep(self):
        pass
    def get_qrep(self):
        pass
    def get_hsm_rep(self):
        pass
    def test(self):
        self.set_inipacket('cs',0.5, 0.5)
        x = numpy.arange(0.0,1.0,1.0/50)
        y = numpy.arange(0.0,1.0,1.0/50)
        X, Y = numpy.meshgrid(x,y)
        self.qmap.set_vrange([(0.0,1.0),(0.0, 1.0)], (50, 50))
        hsm_data = self.qmap.husimi_rep(self.qmap.ivec)
        from mpl_toolkits.mplot3d import Axes3D
        self.fig = pylab.figure()
        ax = Axes3D(self.fig)        
        ax.plot_wireframe(X, Y, hsm_data)
        pylab.show()

        
        
if __name__ == '__main__':
    map = StandardMap(k=2.7)
    #Space(2, False)x
    qmap = QmapSystem(map)
    qmap.test()