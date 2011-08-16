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
        return info
class Hole(PhaseSpace2d):
    def __init__(self, bsetting):
        self.bsetting = bsetting
        # example
        bsetting = [ (True, [0.0,0.1], [0.2,0.3]), (False, []) ]

class Perturbation(PhaseSpace2d):
    def __init__(self, persetting):
        self.persetting = persetting
        # example
        persetting = [ 'noise', (False, []), (True, [-0.5, 0.5]) ]


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
    def quantized_linear_tori(self, p_c, k, omega):
        x = (twopi/self.h)*(-k/(4.0*twopi*twopi*sin(numpy.pi*omega))*sin(twopi*(x-omega/2.0))+p_c*x)
        pass
class Operator(PhaseSpace2d):
    def __init__(self, range, hdim):
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
    def hsm_rep(self, terget):
        cs_dq = (self.vrange[0][1] - self.vrange[0][0]) / self.grid[0]
        cs_dp = (self.vrange[1][1] - self.vrange[1][0]) / self.grid[1]
        hsm_img = numpy.zeros((self.grid[0], self.grid[1]))
        for i in range(self.grid[1]):
            for j in range(self.grid[0]):
                cs_p = self.vrange[1][0] + i*cs_dp
                cs_q = self.vrange[0][0] + j*cs_dq
                cs_vec = self.wave.cs_qvec(cs_q, cs_p)
                sum = numpy.sum(terget*numpy.conj(cs_vec)) 
                hsm_img[i][j] = numpy.abs(sum) * numpy.abs(sum)
        return hsm_img
    def wigner_rep(self):
        pass

class Qmap(PhaseSpace2d):
    def __init__(self, map):
        if isinstance(map, Symplectic2d) != True: raise TypeError
        try:
            setting = map.Psetting
            self.range=[]
            for set in setting:
                if set[0]: self.range.append((0.0, set[1]))
                else: self.range.append((0.0, 1.0))
        except: self.range = [(0.0, 1.0), (0.0, 1.0)]
        try: self.Bsetting = map.Bsetting
        except: self.Bsetting = None

        self.map = map
        self.hdim = 100
        PhaseSpace2d.__init__(self, self.range, self.hdim)
        self.QMapName = map.__class__.__name__
        
        self.vecs = []
        self.ivec = None
        self.fvec = None
        
        self.vrange = self.range
        self.grid = (50, 50)
        self.rep = PhaseSpaceRep(self.range, self.hdim)
        self.rep.set_vrange(self.range, (50,50))
    def set_state(self, state, *args):
        self.wave = WaveFunction(self.range, self.hdim)
        if state in ('q'): self.ivec = self.wave.del_q(args[0])
        elif state in ('p'): pass #self.wave.del_p(p_c)
        elif state in ('cs'): self.ivec = self.wave.cs_qvec(args[0], args[1])
        elif state in ('qlt'): pass
        else: raise TypeError
    def free_operator(self, isShift=True):
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
    def evolve(self, iter, dt=1, TimeLine=True):
        #if self.Bsetting
        evol = self._evolve
        invec = self.ivec
        print TimeLine, dt
        for i in range(iter):
            if TimeLine and i%dt == 0:
                self.vecs.append(invec)
            outvec = evol(invec)
            invec = outvec
        self.fvec = outvec
    def _evolve(self, in_vec):
        freeop = self.free_operator(isShift=True)
        kickop = self.kick_operator(isShift=False)
        vec1 = kickop * in_vec
        out_vec = numpy.fft.fft(vec1)
        vec1 = freeop * out_vec
        self.fvec = numpy.fft.ifft(vec1)
        return self.fvec
    def _evolve_opne(self):
        pass
    def _evolve_perturb(self):
        pass
    def eigen_val(self):
        pass
        print self.range
    def set_range(self, qmin, qmax, pmin, pmax, hdim):
        self.range = [(qmin, qmax), (pmin, pmax)]
        self.hdim = hdim
        self.h = (self.range[0][1] - self.range[0][0]) * (self.range[1][1] - self.range[1][0])/float(self.hdim)
        self.q = numpy.arange(self.range[0][0], self.range[0][1], (self.range[0][1] - self.range[0][0])/self.hdim)
        self.p = numpy.arange(self.range[1][0], self.range[1][1], (self.range[1][1] - self.range[1][0])/self.hdim)
    def get_range(self):
        return self.range, self.hdim
    def set_vrange(self, vqmin, vqmax, vpmin, vpmax, col, row):
        self.vrange = [(vqmin, vqmax), (vpmin, vpmax)]
        self.grid = (col, row)
    def husimi_rep(self, target):
        self.rep = PhaseSpaceRep(self.range, self.hdim)
        self.rep.set_vrange(self.vrange, self.grid)
        hsm_data = self.rep.hsm_rep(target)
        import pylab
        from mpl_toolkits.mplot3d import Axes3D
        x = numpy.arange(self.rep.vrange[0][0], self.rep.vrange[0][1], (self.rep.vrange[0][1] - self.rep.vrange[0][0])/self.rep.grid[0])
        y = numpy.arange(self.rep.vrange[1][0], self.rep.vrange[1][1], (self.rep.vrange[1][1] - self.rep.vrange[1][0])/self.rep.grid[1])
        X, Y = numpy.meshgrid(x, y)
        fig = pylab.figure()
        ax = Axes3D(fig)        
        ax.plot_wireframe(X, Y, hsm_data)
        pylab.show()

        
if __name__ == '__main__':
    import qmap_test