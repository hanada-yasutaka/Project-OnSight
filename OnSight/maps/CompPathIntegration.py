#!/usr/bin/env python
# -*- coding:utf-8 ~*-

from MapSystem import *
import numpy
#import pylab

twopi=2*numpy.pi

class Mset(Space):
    def __init__(self, map):
        map.isComplex = True  
        self.Psetting = map.Psetting
        Space.__init__(self, map.dim, map.isComplex)
        self.map = map
       # self.map.Psetting = [(False,0.0),(False,0.0)] 
        self.mset_data = numpy.array([])
        self.point = Point(map.dim,map.isComplex)
        self.ms = MapSystem(self.map)    
    def mset(self, p, iter, grid, xmin=0.0, xmax=1.0, ymin=-0.5, ymax=0.5, yShift=True):
        p = numpy.array([p+0.j for i in range(grid)])
        x = numpy.arange(xmin, xmax, (xmax - xmin)/grid)
        y = numpy.arange(ymin, ymax, (ymax - ymin)/grid)
        if yShift == True:
            self.get_sign_inversion(iter, p, x, y, grid)
        else:
            #todo 
            self.get_sign_inversion(iter, p, x, y, grid)

    def get_sign_inversion(self, iter, p, x, y, grid):
        for dy in y:
            iy = numpy.array([dy for i in range(grid) ])
            q = x + 1.j*iy
            data = self.evolves(q, p, iter)    
            index = self.where_sign_inversion(data[1].imag)
            for i in index:
                point = (q[i-1].real + q[i].real) /2.0  + 1.j*dy
                self.mset_data = numpy.append(self.mset_data, point)
            if numpy.abs(dy)<=(y.max()-y.min())/grid:
                real = numpy.arange(x.min(), x.max(), (x.max() - x.min())/grid) + 0.j
                self.mset_data = numpy.append(self.mset_data,real)

    def evolves(self, q, p, iter, Psetting=[(False,0.0),(False,0.0)] ):
        #self.map.Psetting = Psetting
        self.ms = MapSystem(self.map)
        self.ms.setPeriodic(Psetting)
        point = Point(self.map.dim, self.map.isComplex, [q,p])
        self.ms.setInit(point)
        self.ms.setMaxImag(None)
        self.ms.evolves(iter)
        return self.ms.P.data

    def where_sign_inversion(self, x):
        x1 = numpy.insert(x, 0, 0.0)
        x2 = numpy.insert(x,len(x),0.0)
        return numpy.where(x1*x2 < 0)[0]
    def get_mset(self):
        return self.mset_data.real, self.mset_data.imag

    
class BranchSearch(object):
    def __init__(self, map, p, iter):
        if type(iter) != int or iter <= 0 : raise ValueError, 'iter > 0 and integer'
        map.isComplex = True        
        self.map = map
        self.iter = iter
        self.p = p + 0.0j
        self.Psetting=self.map.Psetting
        #todo fixed: it didn't work as I had expected, after change psetting on OnSight.
        #i.e., Harper map  
        self.mset = Mset(self.map)
        self.worm_start_point = []
        self.branches = [] 
        self.lset = []   
        self.action = [] 
        
        self.branch_data = []
        self.cut_branches_data = []
        
        self.cut_index = []
    def get_realbranch(self, sample=500):
        x = numpy.arange(0.0, 1.0, 1.0/sample) + 0.0j
        self.branches.insert(0,x)
    def get_lset(self, isPeriod=True):
        if len(self.lset) != 0: self.lset =[]
        for branch in self.branches:
            lset = self.evolves(branch, self.p, self.iter, isPeriod)
            self.lset.append(lset)
    def get_action(self):
        if len(self.branches) == 0: raise ValueError, 'self.branches is empty'
        if len(self.action) != 0: self.action = []
        for branch in self.branches:
            S = numpy.zeros(len(branch),numpy.complex128)
            p = numpy.array([self.p for i in range(len(branch))])
            qp0 = numpy.array([branch, p])
            for i in range(self.iter):
                qp1 = self.mset.evolves(qp0[0], qp0[1], 1)
                S +=  self.map.ifunc1(qp1[1]) + self.map.ifunc0(qp0[0]) + qp0[0]*(qp1[1]-qp0[1])
                qp0 = qp1
            self.action.append(S)
        
    def save_branch(self, th, path):
        import os
        self.get_lset()
        self.get_action()
        for i in range(len(self.branches)):
            filename = '%s/Branch%s.dat' % (path, i+th)
            index = range(len(self.branches[i]))
            data = numpy.array([index,
                         self.branches[i].real, self.branches[i].imag,
                         self.lset[i][0].real, self.lset[i][1].real,
                         self.lset[i][0].imag, self.lset[i][1].imag,
                         self.action[i].real, self.action[i].imag
                        ])
            numpy.savetxt('%s' % filename, data.transpose())
            file = open('%s' % filename, 'a')
            file.write('# 0.index, 1.Re[q_0], 2.Im[q_0], 3.Re[q_n], 4.Re[p_n], 5.Im[q_n], 6.Im[p_n], 7.Re[S], 8.Im[S]\n')
            file.write('# index,\t set M_t%d \t set L_t%d\t action_%d\n' % (self.iter, self.iter, self.iter))
            file.close()
        

    def search_neary_branch(self, x, r=1e-3, wsample=100, wr=1e-4, wsamplemax =1e4, isTest=False):
        self.isTest=isTest
        while True:
            circle = self.make_circle(x,r)
            index = self.where_sign_inversion(circle, self.p, self.iter)
            if len(index) == 0: r = 3.0*r
            elif len(index) > 2: r = 0.5*r
            else:
                err = None 
                break
        section = self.bisection(circle[index[0]-1], circle[index[0]], self.p, self.iter)
        self.worm_start_point.append(section)
        self.get_branch(section, wsample, wr, wsamplemax, isTest=isTest)
        n=1.0
        while len(self.branches[len(self.branches)-1]) < 10:
            print wr*n  
            if n < 1e-5:
                print 'Branch Serach Error'
                err = True
                break
            n = n*0.5
            self.branches.pop()
            self.get_branch(section, wsample, wr*n, 1e5, isTest=isTest)
        return err
    def get_branch(self, start_point, sample=100, r = 0.0001, sample_max=1e5, isTest=False):
        self.isTest=isTest
        branch = numpy.array([])        
        point1 = self.get_branch_section(self.p, self.iter, start_point, r, 2)
        branch0 = self.worming(start_point, point1[1], point1[0][0], point1[1], self.p, self.iter, sample, sample_max)
        branch1 = self.worming(start_point, point1[1], point1[0][1], point1[1], self.p, self.iter, sample, sample_max)
        branch = numpy.append(branch, branch0[::-1]) # append in the inverse order
        branch = numpy.append(branch, point1[0][0])  
        branch = numpy.append(branch, start_point)         # initial bisection point
        branch = numpy.append(branch, point1[0][1]) # append in the order
        branch = numpy.append(branch, branch1)
        self.branches.append(branch)

    def worming(self, p1, r1, p2, r2, y, iter,sample,sample_max):
        print '##Now Worming, not Warning##'
        worming_number = halve = ch_sam = 0 # for counter
        branch = numpy.array([])

        while r2 > 1e-8 and sample < sample_max :
            d = numpy.abs(p1 - p2)
            beta = numpy.arccos((r2**2 + d**2 - r1**2) / (2.0*r2*d ) ) # Low of cosines
            alpha = numpy.angle(p2 - p1) # argument
            theta = numpy.linspace(-numpy.pi + alpha + beta, numpy.pi + alpha - beta, sample)
            semi_circle = r2*numpy.exp(1.j*theta) + p2 
            data = self.evolves(semi_circle, y, iter)
            index = self.mset.where_sign_inversion(data[1].imag)  
            if len(index) != 1:
                r2 =r2*0.5
                halve +=1
            elif numpy.abs(data[1][index -1] -data[1][index]) > 1e-4:
                sample = sample*2
                ch_sam = 1
            else:
                point = self.bisection(semi_circle[index-1], semi_circle[index], y ,iter)
                branch = numpy.append(branch,point)
                p1,r1 = p2, r2
                p2,r2 = point, r2
                worming_number +=1
                if worming_number % 100 == 0 or ch_sam !=0:
                    print '%dth worm:(r,sample)=(%.0e,%d)' % (worming_number, r2, sample),\
                    '|[Im(P_n)]|~%.0e' % numpy.abs(data[1][index-1].imag - data[1][index].imag)
                #if self.isTest and worming_number > 5000: break 
                if self.isTest and ( sample > 10000 or worming_number > 5000) : break 
            ch_sam = 0

        return branch 

    def get_branch_section(self, y, iter, center, radius, intersection=1):
        if intersection not in [1,2]: raise ValueError, 'intersection = 1 or 2'
        sec_data=[]
        while True:
            circle = self.make_circle(center, radius)
            index = self.where_sign_inversion(circle, y ,iter)
            if len(index) != intersection:
                radius = radius*0.5
                if radius < 1e-16:
                    raise ValueError, 'worming radius shrinking is Stop! r=%f' % radius
            else:
                for i in index:
                    x1, x2 = circle[i-1], circle[i]
                    center = self.bisection(x1, x2, y, iter)
                    sec_data.append(center)
                break
        if intersection == 2 and numpy.abs(sec_data[0].imag) - numpy.abs(sec_data[1].imag) > 0:
            sec_data = sec_data[::-1]
        return sec_data, radius
            
    def make_circle(self, p, r, sample=100, theta_min=0.0, theta_max=twopi):
        theta = numpy.arange(0, twopi, twopi/sample)
        z = r*numpy.exp(1.j*theta) + p
        return z

    def bisection(self, x1, x2, y, iter, distance=1e-10):
        y = y + 0.0j
        while numpy.abs(x1 - x2)> distance:
            xm = (x1 + x2)/2.0
            p1 = self.mset.evolves(x1, y, iter)
            p2 = self.mset.evolves(x2, y, iter)
            pm = self.mset.evolves(xm, y, iter)
            if p1[1].imag * p2[1].imag > 0.0:
                raise ValueError, 'Can not bisection, Re[p1_{%d}],Re[p2_{%d}] are same sign.' % (iter, iter)
            if p1[1].imag * pm[1].imag > 0.0:
                x1 = xm
            else:
                x2 = xm
        xm = (x1 + x2)/2.0
        return xm
    def evolves(self, x, y ,iter, isPeriod=False):
        y = numpy.array([y for i in range(len(x)) ])
        if isPeriod:
            data = self.mset.evolves(x, y, iter, self.Psetting)
        else:
            data = self.mset.evolves(x, y, iter, ([False, 0.0],[False, 0.0])) 
        return data
    def where_sign_inversion(self,x, y, iter):
        data = self.evolves(x, y, iter)
        return self.mset.where_sign_inversion(data[1].imag)
    def get_mset(self, xi_min, xi_max, eta_min, eta_max, grid):
        mset = Mset(self.map)
        mset.mset(self.p, self.iter, grid, xi_min, xi_max, eta_min, eta_max)
        return mset.get_mset()
    def get_map(self, map, xmin, xmax, ymin, ymax, sample, iter):

        map.Psetting = self.Psetting
        ms = MapSystem(map, True)
        ms.setPeriodic(map.Psetting)
        x = numpy.random.random(sample)
        y = numpy.arange(ymin, ymax, (ymax - ymin)/sample)
        point = Point(map.dim, map.isComplex, [x,y])
        ms.setInit(point)
        ms.evolves(iter)
        data = [[],[]]
        for i in range(1,len(ms.Remain)):
            data[0].append(numpy.array(ms.Trajectory[i]).transpose()[0])
            data[1].append(numpy.array(ms.Trajectory[i]).transpose()[1])
        return data


    def get_pruning_branch(self, branch_data, cut_pmin=-10.0, cut_pmax=10.0, isChain=False):
        import pylab
        if numpy.sum(numpy.abs(branch_data[2].imag) < 1e-16) == len(branch_data[2].imag):
            index = numpy.arange(len(branch_data[2].imag))
        elif isChain :
            index = self.adhoc_branch_pruning(branch_data)
        else:
            count = 0
            index = []
            for x in branch_data[1][1].real:
                #if x > cut_pmin and x < cut_pmax and branch_data[2][count].imag >= 0:
                if branch_data[2][count].imag >= 0.0:
                    index.append(count)
                count += 1
            index = numpy.array(index)
        self.cut_index.append(index)
        self.cut_branches_data.append([branch_data[0][index], [branch_data[1][0][index], branch_data[1][1][index]], branch_data[2][index]])
    def difference(self, x):
        inf = numpy.float('inf')
        x1 = numpy.insert(x, 0, 0.0)
        x2 = numpy.insert(x, len(x), 0.0)
        diff = x1 - x2
        diff = numpy.delete(diff, 0)
        diff = numpy.delete(diff, len(diff)-1)
        diff = numpy.insert(diff, len(diff)-1, inf)
        return diff
    def adhoc_branch_pruning(self, branch_data):
        diff1 = self.difference(branch_data[2].imag)
        diff_p= self.difference(branch_data[1][1].real)
        diff2 = self.difference(diff1)
        diff = diff2/diff_p/diff_p

        index = numpy.where(numpy.abs(diff)<1e-2)[0] 

        if len(index) == 0: cutoff_index = []
        else: cutoff_index = numpy.where(branch_data[2].imag > branch_data[2][index.min()].imag)[0]

        return cutoff_index
    def hand_branch_pruning(self, start, end, th):
        index = numpy.arange(start, end)
        branch_data = self.branch_data[th]
        branch = branch_data[0][index]
        lset = [branch_data[1][0][index], branch_data[1][1][index]]
        action = branch_data[2][index]
        self.cut_branches_data[th] = [branch, lset, action]
    def get_semiwave(self, branch_data, qmin, qmax, pmin, pmax, hdim):
        dp = (pmax - pmin)/hdim
        h = (pmax - pmin)*(qmax - qmin)/hdim
        semi_wave = numpy.zeros(hdim, numpy.complex128)
        for i in range(hdim):
            p = pmin + i*dp
            index = numpy.where(numpy.abs(branch_data[1][1].real - p)<dp)[0]
            weight = 0.0+0.0j
            if len(index) > 0:
                for j in index:
                    weight += numpy.exp(twopi*1.j*(branch_data[2][j])/h)
            semi_wave[i] = weight
        return semi_wave

    