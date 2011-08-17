#!/usr/bin/env python

from MapSystem import *
import numpy
import numpy.fft
#import pylab


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

class WaveFunction(PhaseSpace2d):
    def __init__(self, range, hdim):
        PhaseSpace2d.__init__(self, range, hdim)
        self.vec = numpy.zeros(self.hdim, dtype=numpy.complex128)
    def del_q(self, q_in):
        if q_in == self.range[0][1]:
            q_in = self.range[0][0]
        d = self.range[0][1] - self.range[0][0]
        s = int(round(self.q.min()*self.hdim/d))
        qq = numpy.arange(s, s+self.hdim, 1, dtype=int)
        q_c = int(round(q_in*self.hdim/d))
        index = numpy.where(qq == q_c)[0]
        self.vec[index] = 1.0
        return self.vec
    def del_p(self, p_in):
        if p_in == self.range[1][1]:
            p_in = self.range[1][0]
        d = self.range[1][1] - self.range[1][0]
        s = int(round(self.p.min()*self.hdim/d))
        p_c = int(round(p_in*self.hdim/d))
        
        p_index = numpy.arange(s, s+self.hdim, 1, dtype=int)
        p_index = numpy.fft.fftshift(p_index)

        index1 = numpy.where(p_index == p_c)[0]
        index2 = numpy.where(p_index == index1)[0]

        self.vec[index2] = 1.0 
        vec = numpy.fft.ifft(self.vec)
        return vec.real*numpy.sqrt(len(vec)) + 1.j*vec.imag*numpy.sqrt(len(vec))

    def cs_qvec(self, q_c, p_c):
        d = self.range[0][1] - self.range[0][0]
        lqmin = self.range[0][0] - d
        lqmax = self.range[0][1] + d
        
        long_q = numpy.arange(lqmin, lqmax, (lqmax - lqmin)/(3.0 * self.hdim))
        q = numpy.linspace(self.range[0][0], self.range[0][1], self.hdim)
        
        coh_state = self.coherent_state_q(long_q, q_c, p_c)
        norm = numpy.sum(numpy.abs(coh_state)**2) 

        vec = numpy.zeros(self.hdim, dtype=numpy.complex128)        
        m = len(coh_state)/self.hdim
        coh_state2 = coh_state.reshape(m,len(q))
        
        for i in range(m):
            vec += coh_state2[i][::1]
        norm = numpy.sum(numpy.abs(vec)**2)
        self.vec = vec.real /numpy.sqrt(norm) + 1.j*vec.imag/numpy.sqrt(norm) 
        

        return self.vec
    def coherent_state_q(self, q_in, q_c, p_c):
        q = q_in/numpy.sqrt(self.h/towpi)
        z = q_c/numpy.sqrt(self.h/numpy.pi) + p_c*1.j/numpy.sqrt(self.h/numpy.pi)
        #z = q_c/numpy.sqrt(self.h/numpy.pi) - p_c*1.j/numpy.sqrt(self.h/numpy.pi)
        zz = z*z
        tmp = -numpy.abs(z)*numpy.abs(z)/2.0 \
            - (q*q + zz.real)/2.0 + numpy.sqrt(2.0)*q*z.real\
            + 1.j *( - zz.imag/2.0 + numpy.sqrt(2.0)*q*z.imag)         
        res = numpy.exp(tmp)*numpy.sqrt(2.0 / self.h)
        return res
    def quantized_linear_tori(self, p_c, k, omega):
        self.vec = (twopi/self.h)*(-k/(4.0*twopi*twopi*sin(numpy.pi*omega))*sin(twopi*(x-omega/2.0))+p_c*x)
        pass


class Operator(PhaseSpace2d):
    def __init__(self, map, range, hdim):
        PhaseSpace2d.__init__(self, range, hdim)
        self.map = map
        self.absetting = None
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
    def evolve(self, in_vec):
        freeop = self.free_operator(isShift=True)
        kickop = self.kick_operator(isShift=False)
        vec1 = kickop * in_vec
        out_vec = numpy.fft.fft(vec1)
        vec1 = freeop * out_vec
        self.fvec = numpy.fft.ifft(vec1)
        return self.fvec
    def evolve_open(self, in_vec):
        if self.absetting == None: raise TypeError
        freeop = self.free_operator(isShift=True)
        kickop = self.kick_operator(isShift=False)
        in_vec = self.absorb(self.q, self.absetting[0], in_vec)
        vec1 = kickop * in_vec
        out_vec = numpy.fft.fft(vec1)
        out_vec = self.absorb(numpy.fft.fftshift(self.p), self.absetting[1], out_vec)
        vec1 = freeop * out_vec
        out_vec = numpy.fft.ifft(vec1)
        self.fvec = self.absorb(self.q, self.absetting[0],out_vec)
        return self.fvec
    def absorb(self, x, absetting, vec):
        i = 0
        for setting in absetting:
            if not setting: break
            elif i != 0:
                index1 = set(numpy.where(x > setting[0])[0])
                index2 = set(numpy.where(x < setting[1])[0])
                index = list(index1.intersection(index2))
                vec[index] = 0.0
            i += 1
        return vec
    def set_absorb(self, absetting):
        self.absetting = absetting        
    def eigen_val(self):
        pass
        print self.range
class Representation(PhaseSpace2d):
    def __init__(self, range, hdim):
        PhaseSpace2d.__init__(self, range, hdim)
        self.wave = WaveFunction(range, hdim)
    def get_p_rep(self, vec):
        return self.q, vec
    def q_rep(self):
        pass
class Perturbation(Operator):
    def __init__(self, map, range, hdim):
        Operator.__init__(self, map, range, hdim)
    def set_perturbation(self, setting):
        list=['noise']
        if setting[0][0] not in list: raise TypeError
        if setting[0][0] == 'noise': self.perturbation = self.noise
        print self.perturbation
        self.setting = setting
    def free_operator(self, isShift=True):
        if isShift:
            sp = numpy.fft.fftshift(self.p)
            tfunc = self.map.ifunc1(sp)
            i=0
            for setting in self.setting[2]: 
                if not setting: break
                elif i != 0: tfunc = self.perturbation(sp, self.setting[0][1],setting[0], setting[1], tfunc)
                i += 1
        else:
            trunc = self.map.ifunc1(self.p)
            i=0
            for setting in self.setting[2]:
                if not setting: break
                elif i != 0: tfunc = self.perturbation(self.p, self.setting[0][1],setting[0], setting[1], tfunc)
                i += 1
        return numpy.exp(-twopi*1.j*tfunc/self.h)
    def kick_operator(self, isShift=False):
        if isShift:
            sq = numpy.fft.fftshift(self.q)
            vfunc = self.map.ifunc0(sq)
            i = 0
            for setting in self.setting[1]:
                if not setting: break
                elif i != 0: vfunc = self.perturbation(sp, self.setting[0][1], setting[0], setting[1], vfunc)
                i += 1
        else:
            vfunc = self.map.ifunc0(self.q)
            i=0
            for setting in self.setting[2]:
                if not setting: break
                elif i != 0: vfunc = self.perturbation(self.q, self.setting[0][1], setting[0], setting[1], vfunc)
        return numpy.exp(-towpi*1.j*vfunc /self.h)
    def noise(self, x, eps, pcut_min, pcut_max, func):
        index1 = set(numpy.where(x > pcut_min)[0])
        index2 = set(numpy.where(x < pcut_max)[0])
        index = list(index1.intersection(index2))
        for i in index:
            func[i] = func[i] + eps*numpy.random.random()
        return func    

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

class Statistics(PhaseSpace2d):
    def _init__(self, range, hdim, vecs,):
        PhaseSpace2d.__init__(self, range, hdim)
        self.vecs = vecs
        self.get_survival()
        self.get_average()
    def get_survival(self):
        self.survival = []
        for vec in self.vecs:
            norm = numpy.sum(numpy.abs(self.vec)**2)
            self.surv.append(norm)
    def get_average(self):
        self.average = []
    def get_variance(self):
        self.variance = []
    def get_mean_sqdis(self,ini_c):
        self.mean_sqdis = []
    def get_loc_survival(self, range):
        self.loc_surv = []
    
class QMap(PhaseSpace2d):
    def __init__(self, map):
        if isinstance(map, Symplectic2d) != True: raise TypeError
        try:
            setting = map.Psetting
            self.range=[]
            for set in setting:
                if set[0]: self.range.append((0.0, set[1]))
                else: self.range.append((0.0, 1.0))
        except: self.range = [(0.0, 1.0), (0.0, 1.0)]
        try: self.ABsetting = map.Bsetting
        except: self.ABsetting = [(False, []),(False,[])]

        self.map = map
        self.hdim = 100
        PhaseSpace2d.__init__(self, self.range, self.hdim)
        self.QMapName = map.__class__.__name__
        
        self.qvecs = []
        self.pvecs = []
        self.ivec = None
        self.fvec = None
        
        self.vrange = self.range
        self.grid = (50, 50)
        self.rep = PhaseSpaceRep(self.range, self.hdim)
        self.rep.set_vrange(self.range, (50,50))
    def setState(self, state, *args):
        self.wave = WaveFunction(self.range, self.hdim)
        self.state = state
        self.ini_c = args
        if state in ('q'): self.ivec = self.wave.del_q(args[0])
        elif state in ('p'):  self.ivec = self.wave.del_p(args[0])
        elif state in ('cs'):  self.ivec = self.wave.cs_qvec(args[0], args[1])
        elif state in ('qlt'): pass
        else: raise TypeError
        self.op = Operator(self.map, self.range, self.hdim)
        if self.ABsetting[0][0] or self.ABsetting[1][0]:
            self.evolv = self.op.evolve_open
        else:
            self.evolv = self.op.evolve   
    def evolve(self, iter):
        if self.ivec == None: raise ValueError
        invec = self.ivec
        for i in range(iter):
#            if TimeLine and i%dt == 0:
            self.qvecs.append(invec)
            outvec = self.evolv(invec)
            invec = outvec
        self.fvec = outvec
    def setPerturb(self, PEsetting):#, pesetting):
        self.PEsetting = [ ('noise', 1.0), (True, [0.2,0.3]), (True, [0.3, 0.5]) ]        
        self.op =  Perturbation(self.map, self.range, self.hdim)
        self.op.set_perturbation(pesetting)
        if self.ABsettin[0][0] or self.Absetting[1][0]:
            self.evolv = self.op.evolve_open
        self.evolv = self.op.evolve
    def setAbsorb(self, absetting):
        self.ABsetting = absetting
        self.op = Operator(self.map, self.range, self.hdim)
        self.op.set_absorb(self.ABsetting)
        self.evolv = self.op.evolve_open
    def setRange(self, qmin, qmax, pmin, pmax, hdim):
        self.ivec = None
        self.range = [(qmin, qmax), (pmin, pmax)]
        self.hdim = hdim
        self.h = (self.range[0][1] - self.range[0][0]) * (self.range[1][1] - self.range[1][0])/float(self.hdim)
        self.q = numpy.arange(self.range[0][0], self.range[0][1], (self.range[0][1] - self.range[0][0])/self.hdim)
        self.p = numpy.arange(self.range[1][0], self.range[1][1], (self.range[1][1] - self.range[1][0])/self.hdim)
        self.setVRange(qmin, qmax, pmin, pmax, 50,50)
    def get_range(self):
        qmin, qmax = self.range[0][0], self.range[0][1]
        pmin, pmax = self.range[1][0], self.range[1][1]
        return qmin, qmax, pmin, pmax, self.hdim
    def setVRange(self, vqmin, vqmax, vpmin, vpmax, col, row):
        self.vrange = [(vqmin, vqmax), (vpmin, vpmax)]
        self.grid = (col, row)
    def get_vrange(self):
        qmin, qmax = self.vrange[0][0], self.vrange[0][1]
        pmin, pmax = self.vrange[1][0], self.vrange[1][1]
        col, row = self.grid[0] , self.grid[1]
        return qmin, qmax, pmin, pmax, col, row

    def get_hsmdata(self, target):
        self.rep = PhaseSpaceRep(self.range, self.hdim)
        self.rep.set_vrange(self.vrange, self.grid)
        return self.rep.hsm_rep(target)
    def husimi_rep(self, target):
        self.rep = PhaseSpaceRep(self.range, self.hdim)
        self.rep.set_vrange(self.vrange, self.grid)
        hsm_data = self.rep.hsm_rep(target)
        import pylab
        from mpl_toolkits.mplot3d import Axes3D
        x = numpy.arange(self.rep.vrange[0][0], self.rep.vrange[0][1], (self.rep.vrange[0][1] - self.rep.vrange[0][0])/self.rep.grid[0])
        y = numpy.arange(self.rep.vrange[1][0], self.rep.vrange[1][1], (self.rep.vrange[1][1] - self.rep.vrange[1][0])/self.rep.grid[1])
        X, Y = numpy.meshgrid(x, y)
      
        #fig = pylab.figure()
        #ax = Axes3D(fig)
        #ax.plot_wireframe(X, Y, hsm_data)
        
        extent = (self.vrange[0][0], self.vrange[0][1],self.vrange[1][0],self.vrange[1][1])
        ax = pylab.subplot(1,1,1)
        #ax.imshow(hsm_data,cmap=pylab.cm.Oranges)#,extent=extent)
        #pylab.colorbar(mappable, cax, ax)
        #level = numpy.arange(0.0001, 1.0, 0.001)
        
        ax.contourf(X,Y,hsm_data, hold='on', color='k')
        pylab.show()
    def get_pvecs(self):
            for vec in self.xvec:
                v = self.x2p(vec)
                self.pvecs.append(v)
    def x2p(self, vec):
        vec1 = numpy.fft.fft(vec)
        vec2 = numpy.fft.fftshift(vec1)
        return vec2.real/numpy.sqrt(len(vec2)) + 1.j*vec2.imag/numpy.sqrt(len(vec2))
    def p2x(self, vec):
        vec1 = numpy.fft.fftshift(vec)
        vec2 = numpy.fft.ifft(vec1)
        return vec2.real*numpy.sqrt(len(vec1)) + 1.j*vec2.imag*numpy.sqrt(len(vec2))
#    def getStatistic(self):
#        if self.state in ('p','cs','qlt'):
#            self.get_pvecs()
#            self.statistic = Statistics(self.range, self.hdim, self.pvecs)
#        else:
#            self.statistic =Statistics(self.range, self.hdim, self.qvecs)


if __name__ == '__main__':
    import qmap_test