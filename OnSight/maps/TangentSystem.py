#       TangentSystem.py
#       
#       Copyright 2011 akaishi <akaishi@akaishi-VirtualBox>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
"""

TODO: complete the description
**Usage**

"""

import numpy
import scipy

from MapSystem import Point, Map, MapSystem
twopi=2*numpy.pi

class TangentMap(Map):
	def __init__(self,map):
		Map.__init__(self,map.dim,map.isComplex)
		self.Para=map.Para
		
		self.dpIn=self.pIn
		self.dpOut=self.pOut
	def dfunc(self,p):
		pass
		
	def devol(self,p):
		self.dfunc(p)
		self.pull()
		
class dSymplectic2d(TangentMap):
	def __init__(self,map):
		TangentMap.__init__(self,map)
		
	def dfunc(self,p):
		df0=   self.dfunc0(p.data[0])
		df1= - self.dfunc1(p.data[1])
		self.dpOut.data[1]=        self.dpIn.data[1] +           df0 * self.dpIn.data[0]
		self.dpOut.data[0]=  df1 * self.dpIn.data[1] + (1.0+df0*df1) * self.dpIn.data[0]
	
	def dfunc0(self,x):
		return 1.0
		
	def dfunc1(self,x):
		return 1.0

class dStandardMap(dSymplectic2d):
	def __init__(self,map):
		dSymplectic2d.__init__(self,map)
		
	def dfunc0(self,x):
		return self.Para.para[0]*numpy.cos(x*twopi)

class dPiecewiseLinearStandard(dSymplectic2d):
	def __init__(self,map):
		dSymplectic2d.__init__(self,map)
		
	def dfunc0(self,x):
		b=(x>0.25) & (x<0.75)
		return self.Para.para[0]*(1.0-2.0*b)

class dSharpenStandard(dSymplectic2d):
	def __init__(self,map):
		dSymplectic2d.__init__(self,map)
		
	def dfunc0(self,x):
		return self.Para.para[0]*numpy.cos(twopi*x)/numpy.sqrt(1.0-(self.Para.para[1]*numpy.sin(twopi*x))**2)

class dTruncatedStandard(dSymplectic2d):
	def __init__(self,map):
		dSymplectic2d.__init__(self,map)
		
	def dfunc0(self,x):
		px=x*twopi
		y=numpy.ones(len(x))
		for i in range(1,self.Para.para[1]+1):
			y+=scipy.factorial2(2*i-1)/scipy.factorial2(2*i)*numpy.sin(px)**(2*i)
		return self.Para.para[0]*numpy.cos(px)*y

class dQuadraticStandard(dSymplectic2d):
	def __init__(self,map):
		dSymplectic2d.__init__(self,map)
		
	def dfunc0(self,x):
		b=x<0.5
		return self.Para.para[0]*( b*(-4.0*(x-0.25)) + (~b)*(4.0*(x-0.75)) )

class dNQuadraticStandard(dSymplectic2d):
	def __init__(self,map):
		dSymplectic2d.__init__(self,map)
		
	def dfunc0(self,x):
		b=x<0.5
		n=self.Para.para[1]
		return self.Para.para[0]*(b*(-2.0**(4.0*n-3.0)/n *(2*n) *(x-0.25)**(2*n-1)) + (~b)*(2.0**(4.0*n-3.0)/n *(2*n) *(x-0.75)**(2*n-1)) )

class dKeplerMap(dStandardMap):
	def __init__(self,map):
		dStandardMap.__init__(self,map)
		
	def dfunc1(self,x):
		return self.Para.para[1]*(-1.5)*x**(-2.5)
		
class dKeplerGeneral(dKeplerMap):
	def __init__(self,map):
		dKeplerMap.__init__(self,map)
		
	def dfunc1(self,x):
		return self.Para.para[1]*(-self.Para.para[2])*x**(-self.Para.para[2]-1.0)

class dHenonMap(TangentMap):
	def __init__(self,map):
		TangentMap.__init__(self,map)
		
	def dfunc(self,p):
		self.dpOut.data[0]=-2.0*p.data[0]*self.dpIn.data[0] - self.Para.para[1]*self.dpIn.data[1]
		self.dpOut.data[1]= self.dpIn.data[0]

class dSymplectic4d(TangentMap):
	def __init__(self,map):
		TangentMap.__init__(self,map)
		
	def dfunc(self,p):
		df00=   self.dfunc00(p.data[0],p.data[2])
		df02=   self.dfunc02(p.data[0],p.data[2])
		df11= - self.dfunc11(p.data[1],p.data[3])
		df13= - self.dfunc13(p.data[1],p.data[3])
		df22=   self.dfunc22(p.data[2],p.data[0])
		df20=   self.dfunc20(p.data[2],p.data[0])
		df33= - self.dfunc33(p.data[3],p.data[1])
		df31= - self.dfunc31(p.data[3],p.data[1])
		
		self.dpOut.data[1]=      self.dpIn.data[1] +                                                 df00*self.dpIn.data[0] +                        df02*self.dpIn.data[2]
		self.dpOut.data[3]=                               self.dpIn.data[3] +                        df20*self.dpIn.data[0] +                        df22*self.dpIn.data[2]
		self.dpOut.data[0]= df11*self.dpIn.data[1] + df13*self.dpIn.data[3] + (1.0+(df11*df00+df13*df20))*self.dpIn.data[0] +       (df11*df02+df13*df22)*self.dpIn.data[2]
		self.dpOut.data[2]= df31*self.dpIn.data[1] + df33*self.dpIn.data[3] +       (df31*df00+df33*df20)*self.dpIn.data[0] + (1.0+(df31*df02+df33*df22))*self.dpIn.data[2]
		
	def dfunc00(self,x,y):
		return 1.0
	def dfunc02(self,x,y):
		return 0.0
	def dfunc11(self,x,y):
		return 1.0
	def dfunc13(self,x,y):
		return 0.0
	def dfunc20(self,x,y):
		return 0.0
	def dfunc22(self,x,y):
		return 1.0
	def dfunc31(self,x,y):
		return 0.0
	def dfunc33(self,x,y):
		return 1.0
	
class dFroeschle(dSymplectic4d):
	def __init__(self,map):
		dSymplectic4d.__init__(self,map)

	def dfunc00(self,x,y):
		return self.Para.para[0]*numpy.cos(x*twopi)+self.Para.para[2]*numpy.cos((x-y)*twopi)
	def dfunc02(self,x,y):
		return                                     -self.Para.para[2]*numpy.cos((x-y)*twopi)
	def dfunc22(self,x,y):
		return self.Para.para[1]*numpy.cos(x*twopi)+self.Para.para[2]*numpy.cos((x-y)*twopi)
	def dfunc20(self,x,y):
		return                                     -self.Para.para[2]*numpy.cos((x-y)*twopi)


class TangentSystem(object):
	def __init__(self,mapsystem):
		nameMap=type(mapsystem.map).__name__
		
		try:
			self.dMapClass=eval('d'+nameMap)
			self.hasdMap=True
		except NameError:
			self.dMapClass=None
			self.hasdMap=False
		
		self.mapsystem=mapsystem
		self.numVec=0
		
	def setInitVec(self,numVec):
		if self.hasdMap:
			self.numVec=min(max(numVec,1),self.mapsystem.dim)
			
			self.dMaps=[self.dMapClass(self.mapsystem.map) for n in range(self.numVec)]
			sample=len(self.mapsystem.map.pIn.data[0])
			
			self.Norm=[numpy.zeros(sample) for n in range(self.numVec)]
			self.Sum=[numpy.zeros(sample) for n in range(self.numVec)]
			self.Lyapunov=[numpy.zeros(sample) for n in range(self.numVec)]
			self.Count=0
			
			p=Point(self.mapsystem.dim,self.mapsystem.isComplex)
			
			for n in range(self.numVec):
				p.data=[numpy.random.random(sample)-0.5 for d in range(p.dim)]
				self.dMaps[n].setIn(p)
				
				self.Norm[n]=self.calcNorm(self.dMaps[n].dpIn.data)
				self.dMaps[n].dpIn.data=numpy.array(self.dMaps[n].dpIn.data)/self.Norm[n]
	
	def calcNorm(self,data):
		return numpy.sqrt(self.calcInnerProduct(data,data))
		
	def calcInnerProduct(self,data1,data2):
		tdata1=numpy.array(data1).transpose()
		tdata2=numpy.array(data2).transpose()
		return numpy.array([numpy.vdot(tdata1[i],tdata2[i]) for i in range(len(tdata1))])
	
	def evolve(self):
		self.mapsystem.evolve()
		self.Count+=1
		
		for n in range(self.numVec):
			self.dMaps[n].dpIn.data=numpy.array([d[self.mapsystem.Remain] for d in self.dMaps[n].dpIn.data])
			self.dMaps[n].devol(self.mapsystem.P)
		
		sample=len(self.dMaps[0].dpIn.data[0])
		for n in range(self.numVec):
			for m in range(n):
				ip=self.calcInnerProduct(self.dMaps[n].dpIn.data,self.dMaps[m].dpIn.data)
				self.dMaps[n].dpIn.data -= ip*self.dMaps[m].dpIn.data
			
			self.Norm[n]=self.calcNorm(self.dMaps[n].dpIn.data)
			self.dMaps[n].dpIn.data=numpy.array(self.dMaps[n].dpIn.data)/self.Norm[n]
			
			for sam in range(sample):
				if sam in self.mapsystem.Remain[0]:
					self.Sum[n][sam]+=numpy.log(self.Norm[n][sam])
				else:
					self.Sum[n][sam]=0.0
				self.Lyapunov[n][sam]=self.Sum[n][sam]/float(self.Count)
		
		

