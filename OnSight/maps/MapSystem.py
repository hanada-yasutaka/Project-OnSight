#       MapSystem.py
#       
#       Copyright 2011 Akira Akaishi <akira.akaishi@gmail.com>
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

twopi=2*numpy.pi

def _fmod(x):
	return x-numpy.floor(x)

def _fMod1(x,y=1.0):
	return _fmod(x)

def _fModC1(x,y=1.0):
	return _fmod(x.real)+x.imag*1j
def _fMod(x,y):
	return y*_fmod(x/y)

def _fModC(x,y):
	return _fMod(x.real,y)+x.imag*1j

class Space(object):
	def __init__(self,dim,isComplex):
		self.dim=dim
		self.isComplex=isComplex

class Point(Space):
	"""
	The Point class stores coordinate data of point(s) as well as dimensionality.
	TODO: add operation methods
	"""
	def __init__(self,dim,isComplex=False,data=None):
		if data!=None and dim!=len(data):
			raise TypeError
			return
		Space.__init__(self,dim,isComplex)
		
		self.data=[numpy.array([0.0+0.0j]) if isComplex else numpy.array([0.0]) for i in range(self.dim)] if (data==None) else data

class Parameter(object):
	def __init__(self,n=0):
		self.num=n
		self.para=[0.0 for i in range(n)]
		self.range=[(None,None) for i in range(n)]

class Map(Space):
	"""
	Base class of maps, a new map should inherit Map class and
	override `func` method, which will define a function from 
	`pIn.data` to `pOut.data`.
	"""
	def __init__(self,dim,isComplex):
		Space.__init__(self,dim,isComplex)
		
		self.pIn=Point(self.dim,self.isComplex)
		self.pOut=Point(self.dim,self.isComplex)
		self.Para=Parameter()
	
	def setIn(self,p):
		if (self.dim,self.isComplex)!=(p.dim,p.isComplex): raise TypeError
		self.pIn.data=[numpy.array(p.data[i] if numpy.iterable(p.data[i]) else [p.data[i]]) for i in range(p.dim)]
		self.pOut.data=[numpy.zeros(len(self.pIn.data[i])) for i in range(p.dim)]
	
	def getIn(self):
		return self.pIn
	
	def getOut(self):
		return self.pOut
		
	def getPara(self):
		return self.Para
		
	def swap(self):
		dataTemp=[d for d in self.pIn.data]
		self.pIn.data=[d for d in self.pOut.data]
		self.pOut.data=dataTemp
	
	def pull(self):
		self.pIn.data=[d for d in self.pOut.data]
	
	def func(self):
		pass
		
	def map(self,p):
		self.setIn(p)
		self.func()
		return self.getOut()
		
	def evol(self):
		self.func()
		self.pull()
		

"""1-dimensional maps"""
class Quadra(Map):
	def __init__(self,c=2.0,isComplex=False):
		Map.__init__(self,1,isComplex=isComplex)
		self.Para=Parameter(1)
		self.Para.para[0]=c
	
	def func(self):
		self.pOut.data[0]=self.pIn.data[0]**2.0+self.Para.para[0]

class Bernoulli2(Map):
	def __init__(self,p=0.4,isComplex=False):
		Map.__init__(self,1,isComplex=isComplex)
		self.Para=Parameter(1)
		self.Para.para[0]=p
		self.Para.range[0]=(0.0,1.0)
		
		self.Psetting=[(True,1.0)]
		
	def func(self):
		b=self.pIn.data[0]<self.Para.para[0]
		
		self.pOut.data[0]=b*(self.pIn.data[0]/self.Para.para[0]) + (~b)*(self.pIn.data[0]-self.Para.para[0])/(1.0-self.Para.para[0])
	
class BernoulliK(Map):
	"""
	TODO: define the map
	"""
	def __init__(self,k=3,isComplex=False):
		Map.__init__(self,1,isComplex=isComplex)
		self.Para=Parameter(int(k)-1)
		for i in range(self.Para.num):
			self.Para.para[i]=1.0/float(k)
			self.Para.range[i]=(0.0,1.0)
		
		self.Psetting=[(True,1.0)]

def intermittent(a,b,x):
	return x*(1.0+numpy.power(x/a,b)*(1.0-a)/a)

class PomeauManneville(Map):
	def __init__(self,b=0.5,p=0.5,isComplex=False):
		Map.__init__(self,1,isComplex=isComplex)
		self.Para=Parameter(2)
		self.Para.para[0]=p
		self.Para.range[0]=(0.0,1.0)
		self.Para.para[1]=b
		self.Para.range[1]=(0.0,None)
		
		self.Psetting=[(True,1.0)]
		
	def func(self):
		b=self.pIn.data[0]<self.Para.para[0]
		
		self.pOut.data[0]=b*(intermittent(self.Para.para[0],self.Para.para[1],self.pIn.data[0])) + (~b)*(self.pIn.data[0]-self.Para.para[0])/(1.0-self.Para.para[0])
		
class ModifiedBernoulli(Map):
	def __init__(self,b=0.5,p=0.5,isComplex=False):
		Map.__init__(self,1,isComplex=isComplex)
		self.Para=Parameter(2)
		self.Para.para[0]=p
		self.Para.range[0]=(0.0,1.0)
		self.Para.para[1]=b
		self.Para.range[1]=(0.0,None)
		
		self.Psetting=[(True,1.0)]
		
	def func(self):
		b=self.pIn.data[0]<self.Para.para[0]
		
		self.pOut.data[0]=b*(intermittent(self.Para.para[0],self.Para.para[1],self.pIn.data[0])) + (~b)*(1.0-intermittent(1.0-self.Para.para[0],self.Para.para[1],1.0-self.pIn.data[0]))
		
class ModifiedBernoulliAsym(Map):
	def __init__(self,b0=0.5,b1=0.5,p=0.5,isComplex=False):
		Map.__init__(self,1,isComplex=isComplex)
		self.Para=Parameter(3)
		self.Para.para[0]=p
		self.Para.range[0]=(0.0,1.0)
		self.Para.para[1]=b0
		self.Para.range[1]=(0.0,None)
		self.Para.para[2]=b1
		self.Para.range[2]=(0.0,None)
		
		self.Psetting=[(True,1.0)]
		
	def func(self):
		b=self.pIn.data[0]<self.Para.para[0]
		
		self.pOut.data[0]=b*(intermittent(self.Para.para[0],self.Para.para[1],self.pIn.data[0])) + (~b)*(1.0-intermittent(1.0-self.Para.para[0],self.Para.para[2],1.0-self.pIn.data[0]))

'''symplectic 2-dimensional maps'''
class Symplectic2d(Map):
	"""
	Base class of 2-dimensional symplectic maps. The `func` method is overridden.
	A new 2-dim symp. map override `func0` and `func1` method.
	"""
	def __init__(self,isComplex):
		Map.__init__(self,2,isComplex=isComplex)
		
	def func(self):
		self.pOut.data[1]=self.pIn.data[1]-self.func0(self.pIn.data[0])
		self.pOut.data[0]=self.pIn.data[0]+self.func1(self.pOut.data[1])
		
	def func0(self,x):
		return x
	
	def func1(self,x):
		return x
		
	def dfunc0(self,x):
		return 1.0
		
	def dfunc1(self,x):
		return 1.0
		
	def ifunc0(self,x):
		return 0.5*x*x
		
	def ifunc1(self,x):
		return 0.5*x*x

'''family of standard map'''
class StandardMap(Symplectic2d):
	def __init__(self,k=1.0,isComplex=False):
		Symplectic2d.__init__(self,isComplex=isComplex)
		self.Para=Parameter(1)
		self.Para.para[0]=k
		self.Para.range[0]=(0.0,None)
		
		self.Psetting=[(True,1.0),(False,0.0)]
		
	def func0(self,x):
		return self.Para.para[0]/twopi*numpy.sin(x*twopi)
		
	def dfunc0(self,x):
		return self.Para.para[0]*numpy.cos(x*twopi)
		
	def ifunc0(self,x):
		return -self.Para.para[0]/twopi/twopi*numpy.cos(x*twopi)

class PiecewiseLinearStandard(Symplectic2d):
	def __init__(self,k=1.0,isComplex=False):
		Symplectic2d.__init__(self,isComplex=isComplex)
		self.Para=Parameter(1)
		self.Para.para[0]=k
		self.Para.range[0]=(0.0,None)
		
		self.Psetting=[(True,1.0),(False,0.0)]
	def func0(self,x):
		b0=x<0.25
		b1=(x<0.75) & (~b0)
		b2=x>0.75
		return self.Para.para[0]*(b0*x + b1*(0.5-x) + b2*(x-1.0))
		
	def dfunc0(self,x):
		b=(x>0.25) & (x<0.75)
		return self.Para.para[0]*(1.0-2.0*b)
		
	def ifunc0(self,x):
		b0=x<0.25
		b1=(x<0.75) & (~b0)
		b2=x>0.75
		return self.Para.para[0]*(b0*( 0.5*x*x ) + b1*( 0.0625-0.5*(0.5-x)*(0.5-x) ) + b2*( 0.5*(x-1.0)*(x-1.0) ))

class SharpenStandard(Symplectic2d):
	def __init__(self,k=1.0,e=0.5,isComplex=False):
		Symplectic2d.__init__(self,isComplex=isComplex)
		self.Para=Parameter(2)
		self.Para.para[0]=k
		self.Para.range[0]=(0.0,None)
		self.Para.para[1]=numpy.clip(e,0.0,1.0)
		self.Para.range[1]=(0.0,1.0)
		
		self.Psetting=[(True,1.0),(False,0.0)]
	def func0(self,x):
		return self.Para.para[0]/twopi*numpy.arcsin(self.Para.para[1]*numpy.sin(twopi*x))/self.Para.para[1]
		
	def dfunc0(self,x):
		return self.Para.para[0]*numpy.cos(twopi*x)/numpy.sqrt(1.0-(self.Para.para[1]*numpy.sin(twopi*x))**2)

class TruncatedStandard(Symplectic2d):
	def __init__(self,k=1.0,n=1,isComplex=False):
		Symplectic2d.__init__(self,isComplex=isComplex)
		self.Para=Parameter(2)
		self.Para.para[0]=k
		self.Para.range[0]=(0.0,None)
		self.Para.para[1]=int(n)
		self.Para.range[1]=(0.0,None)
		
		self.Psetting=[(True,1.0),(False,0.0)]
	def func0(self,x):
		px=x*twopi
		y=numpy.sin(px)
		for i in range(1,int(self.Para.para[1])+1):
			y+=scipy.factorial2(2*i-1)/scipy.factorial2(2*i)/(2*i+1)*numpy.sin(px)**(2*i+1)
		return self.Para.para[0]/twopi*y
		
	def dfunc0(self,x):
		px=x*twopi
		y=numpy.ones(len(x))
		for i in range(1,self.Para.para[1]+1):
			y+=scipy.factorial2(2*i-1)/scipy.factorial2(2*i)*numpy.sin(px)**(2*i)
		return self.Para.para[0]*numpy.cos(px)*y

class QuadraticStandard(Symplectic2d):
	def __init__(self,k=1.0,isComplex=False):
		Symplectic2d.__init__(self,isComplex=isComplex)
		self.Para=Parameter(1)
		self.Para.para[0]=k
		self.Para.range[0]=(0.0,None)
	
		self.Psetting=[(True,1.0),(False,0.0)]
	def func0(self,x):
		b=x<0.5
		return self.Para.para[0]*( b*(-2.0*(x-0.25)**2+0.125) + (~b)*(2.0*(x-0.75)**2-0.125) )
		
	def dfunc0(self,x):
		b=x<0.5
		return self.Para.para[0]*( b*(-4.0*(x-0.25)) + (~b)*(4.0*(x-0.75)) )

class NQuadraticStandard(Symplectic2d):
	def __init__(self,k=1.0,n=1,isComplex=False):
		Symplectic2d.__init__(self,isComplex=isComplex)
		self.Para=Parameter(2)
		self.Para.para[0]=k
		self.Para.range[0]=(0.0,None)
		self.Para.para[1]=n
		self.Para.range[1]=(0.0,None)
	
		self.Psetting=[(True,1.0),(False,0.0)]
	def func0(self,x):
		b=x<0.5
		n=self.Para.para[1]
		return self.Para.para[0]*(b*(-2.0**(4.0*n-3.0)/n *(x-0.25)**(2*n)+0.125/n) + (~b)*(2.0**(4.0*n-3.0)/n *(x-0.75)**(2*n)-0.125/n) )
		
	def dfunc0(self,x):
		b=x<0.5
		n=self.Para.para[1]
		return self.Para.para[0]*(b*(-2.0**(4.0*n-3.0)/n *(2*n) *(x-0.25)**(2*n-1)) + (~b)*(2.0**(4.0*n-3.0)/n *(2*n) *(x-0.75)**(2*n-1)) )

class ShudoStandard(StandardMap):
	def __init__(self,k=1.2,pd=5.0,omega=1.0,nu=3.0,isComplex=False):
		StandardMap.__init__(self,isComplex=isComplex)
		self.Para=Parameter(4)
		self.Para.para[0]=k
		self.Para.range[0]=(0.0,None)
		self.Para.para[1]=pd
		self.Para.range[1]=(0.0,None)
		self.Para.para[2]=omega
		self.Para.range[2]=(None,None)
		self.Para.para[3]=nu
		self.Para.range[3]=(0.0,None)
	
	def func0(self,x):
		return -self.Para.para[0]*numpy.sin(x*twopi)
		
	def dfunc0(self,x):
		return -self.Para.para[0]*numpy.cos(x*twopi)*twopi
		
	def ifunc0(self,x):
		return self.Para.para[0]*numpy.cos(x*twopi)/twopi
	
	def func1(self,x):
		g=numpy.power(x/self.Para.para[1],2*self.Para.para[3])
		return ( x*g*(1+self.Para.para[3]+g)/(1+g)/(1+g)+self.Para.para[2] )/twopi
		
	def dfunc1(self,x):
		g=numpy.power(x/self.Para.para[1],2*self.Para.para[3])
		return g*(g*g+( (2.0-self.Para.para[3])*g + (1.0+self.Para.para[3]) )*(1.0+2.0*self.Para.para[3]) )/twopi/numpy.power(1.0+g,3.0)
		
	def ifunc1(self,x):
		g=numpy.power(x/self.Para.para[1],2*self.Para.para[3])
		return ( x*x*0.5*g/(1+g) + self.Para.para[2]*x )/twopi

class HypTanStandard(StandardMap):
	def __init__(self,k=2.0, s=4.173, beta=100.0, d=0.4, omega=0.6418,isComplex=False):
		# to do
		# When this map are called in onsight, raise Warning: overflow
		# But func0 and func1 is not overflow...
		StandardMap.__init__(self,isComplex=isComplex)
		self.Para=Parameter(5)
		self.Para.para[0] = k
		self.Para.range[0] = (0.0, None)
		self.Para.para[1] = s
		self.Para.range[1] = (0.0, None)
		self.Para.para[2] = beta
		self.Para.range[2] = (0.0, None)
		self.Para.para[3] = d
		self.Para.range[3] = (0.0, None)
		self.Para.para[4] = omega
		self.Para.range[4] = (0.0, None)
		
	def func0(self, x):
		return -self.Para.para[0]*numpy.sin(x*twopi)/twopi
	
	def dfunc0(self, x):	
		return -self.Para.para[0]*numpy.cos(x*twopi)
	
	def ifunc0(self, x):
		return self.Para.para[0]*numpy.cos(x*twopi)/twopi/twopi

	def func1(self, x):
		g = x - self.Para.para[3]
		s = self.Para.para[1]
		beta = self.Para.para[2]
		return s/2*g*(1+numpy.tanh(beta*g)) + s*g*g*beta/4.0/(numpy.cosh(beta*g)**2) + self.Para.para[4]
	def ifunc1(self, x):
		g = x - self.Para.para[3]
		s = self.Para.para[1]
		beta = self.Para.para[2]
		return s/2*g*(1+numpy.tanh(beta*g)) + self.Para.para[4]*g

	def dfunc1(self, x):
		g = x - self.Para.para[3]
		s = self.Para.para[1]
		beta = self.Para.para[2]
		return s/2*(1+numpy.tanh(beta*g)) + s*x*beta/(numpy.cosh(beta*g)**2) - s/2*x*x*beta*numpy.sinh(beta*g)/(numpy.cosh(beta*g)**3) 
	
class KeplerMap(StandardMap):
	def __init__(self,k=1.0,a=1.0,isComplex=False):
		StandardMap.__init__(self,isComplex=isComplex)
		self.Para=Parameter(2)
		self.Para.para[0]=k
		self.Para.range[0]=(0.0,None)
		self.Para.para[1]=a
		self.Para.range[0]=(0.0,None)
		
		if not self.isComplex: self.Bsetting=[(False,0.0,False,0.0),(True,0.0,False,0.0)]
		
	def func1(self,x):
		return self.Para.para[1]* numpy.power(x,-1.5)
		
	def dfunc1(self,x):
		return self.Para.para[1]*(-1.5)*x**(-2.5)
		
	def ifunc1(self,x):
		return self.Para.para[1]* numpy.power(x,-0.5) / -0.5

class KeplerGeneral(KeplerMap):
	def __init__(self,k=1.0,a=1.0,p=1.5,isComplex=False):
		KeplerMap.__init__(self,isComplex=isComplex)
		self.Para=Parameter(3)
		self.Para.para[0]=k
		self.Para.range[0]=(0.0,None)
		self.Para.para[1]=a
		self.Para.range[1]=(0.0,None)
		self.Para.para[2]=p
		self.Para.range[2]=(0.0,None)
		
	def func1(self,x):
		return self.Para.para[1]* numpy.power(x,-self.Para.para[2])
		
	def dfunc1(self,x):
		return self.Para.para[1]*(-self.Para.para[2])*x**(-self.Para.para[2]-1.0)
		
	def ifunc1(self,x):
		return self.Para.para[1]* numpy.power(x,-self.Para.para[2]+1.0) / (-self.Para.para[2]+1.0)

class HarperMap(StandardMap):
	def __init__(self,k=1.0,isComplex=False):
		StandardMap.__init__(self,k=k,isComplex=isComplex)
		
		self.Psetting=[(True,1.0),(True,1.0)]
		
	def func1(self,x):
		return self.func0(x)
		
	def dfunc1(self,x):
		return self.dfunc0(x)
		
	def ifunc1(self,x):
		return self.ifunc1(x)
		
class PiecewiseLinearHarper(PiecewiseLinearStandard):
	def __init__(self,k=1.0,isComplex=False):
		PiecewiseLinearStandard.__init__(self,k=k,isComplex=isComplex)
		
		self.Psetting=[(True,1.0),(True,1.0)]
		
	def func1(self,x):
		return self.func0(x)
		
	def dfunc1(self,x):
		return self.dfunc0(x)
		
	def ifunc1(self,x):
		return self.ifunc1(x)
		
class SharpenHarper(SharpenStandard):
	def __init__(self,k=1.0,e=0.5,isComplex=False):
		SharpenStandard.__init__(self,k=k,e=e,isComplex=isComplex)
		
		self.Psetting=[(True,1.0),(True,1.0)]
		
	def func1(self,x):
		return self.func0(x)
		
	def dfunc1(self,x):
		return self.dfunc0(x)
		
	def ifunc1(self,x):
		return self.ifunc1(x)

'''general two-dimensional maps '''
class BakerMap(Map):
	def __init__(self,isComplex=False):
		Map.__init__(self,2,isComplex=isComplex)
		
		self.Psetting=[(True,1.0),(True,1.0)]
		
	def func(self):
		b=self.pIn.data[0]>0.5
		
		self.pOut.data[0]=2.0*self.pIn.data[0] + b*(-1.0)
		self.pOut.data[1]=0.5*self.pIn.data[1] + b*0.5

class HenonMap(Map):
	def __init__(self,a=2.0,b=1.0,isComplex=False):
		Map.__init__(self,2,isComplex=isComplex)
		self.Para=Parameter(2)
		self.Para.para[0]=a
		self.Para.para[1]=b
		
	def func(self):
		self.pOut.data[0]=self.Para.para[0]-self.Para.para[1]*self.pIn.data[1]-self.pIn.data[0]**2
		self.pOut.data[1]=self.pIn.data[0]
	
class IkedaMap(Map):
	def __init__(self,R=1.0,C1=0.4,C2=0.9,C3=6.0,isComplex=False):
		Map.__init__(self,2,isComplex=isComplex)
		self.Para=Parameter(4)
		self.Para.para[0]=R
		self.Para.para[1]=C1
		self.Para.para[2]=C2
		self.Para.para[3]=C3
		
	def func(self):
		t=self.Para.para[1]-self.Para.para[3]/(1.0+self.pIn.data[0]**2+self.pIn.data[1]**2)
		self.pOut.data[0]=self.Para.para[0]+self.Para.para[2]*(self.pIn.data[0]*numpy.cos(t)-self.pIn.data[1]*numpy.sin(t))
		self.pOut.data[1]=                  self.Para.para[2]*(self.pIn.data[0]*numpy.sin(t)+self.pIn.data[1]*numpy.cos(t))
		
'''symplectic 4-dimensional maps'''
class Symplectic4d(Map):
	"""
	Base class of 4-dimensional symplectic maps. Variable `data[0]` is conjugate 
	to `data[1]` and `data[2]` to `data[3]`.
	"""
	def __init__(self,isComplex):
		Map.__init__(self,4,isComplex=isComplex)
		
	def func(self):
		self.pOut.data[1]=self.pIn.data[1]-self.func0(self.pIn.data[0],self.pIn.data[2])
		self.pOut.data[0]=self.pIn.data[0]+self.func1(self.pOut.data[1],self.pOut.data[3])
		self.pOut.data[3]=self.pIn.data[3]-self.func2(self.pIn.data[2],self.pIn.data[0])
		self.pOut.data[2]=self.pIn.data[2]+self.func3(self.pOut.data[3],self.pOut.data[1])
		
	def func0(self,x,y):
		return x 
	def func1(self,x,y):
		return x 
	def func2(self,x,y):
		return x 
	def func3(self,x,y):
		return x 

class FroeschleMap(Symplectic4d):
	def __init__(self,k1=1.0,k2=1.0,l=1.0,isComplex=False):
		Symplectic4d.__init__(self,isComplex=isComplex)
		self.Para=Parameter(3)
		self.Para.para[0]=k1
		self.Para.range[0]=(0.0,None)
		self.Para.para[1]=k2
		self.Para.range[1]=(0.0,None)
		self.Para.para[2]=l
		
		self.Psetting=[(True,1.0),(False,0.0),(True,1.0),(False,0.0)]
	
	def func0(self,x,y):
		return (self.Para.para[0]*numpy.sin(x*twopi)+self.Para.para[2]*numpy.sin((x-y)*twopi))/twopi
		
	def func2(self,x,y):
		return (self.Para.para[1]*numpy.sin(x*twopi)+self.Para.para[2]*numpy.sin((x-y)*twopi))/twopi
	

class PhaseSpace(Space):
	"""
	Phase space class. Periodic boundary condition is applied by `putPeriodic`
	method, which operates its argument `pIn` instance. `putBounded` method, 
	either `_PutBounded` or `_PutBounded`, is used to define a upper/lower 
	boundary of phase space. Data of the points which go beyond the boundary 
	is removed.
	"""
	def __init__(self,dim,isComplex=False):
		Space.__init__(self,dim=dim,isComplex=isComplex)
		
		self.Pconditions=[]
		if self.isComplex: self.putBounded=self._PutBoundedC
		else: self.putBounded=self._PutBounded
		self.Bconditions=[]
		
		self.Distance=self.DistanceEuc
	
	def DistanceEuc(self,p1,p2):
		return numpy.sqrt(numpy.sum(self._distance(p1,p2)**2,axis=0))
	
	def DistanceLin(self,p1,p2):
		return numpy.max(numpy.abs(self._distance(p1,p2)),axis=0)
	
	def _distance(self,p1,p2):
		distance=[]
		for d in range(self.dim):
			if d in [c[0] for c in self.Pconditions]:
				(period,Mod)=c[1:]
				distance.append(Mod((p1.data[d]-p2.data[d])+period*0.5,period)-period*0.5)
			else:
				distance.append(p1.data[d]-p2.data[d])
		return numpy.array(distance)
	
	def setPeriod(self,d,period):
		if d>=self.dim or d<0: return
		
		if period==1.0:
			Mod=_fModC1 if self.isComplex else _fMod1
		else:
			Mod=_fModC if self.isComplex else _fMod
		
		if d not in (c[0] for c in self.Pconditions):
			self.Pconditions.append((d,period,Mod))
		else:
			i=self.Pconditions.index([c for c in self.Pconditions if c[0]==d][0])
			self.Pconditions[i]=(d,period,Mod)
	
	def unsetPeriod(self,d):
		if d>=self.dim or d<0: return
		
		delindex=[]
		for i in range(len(self.Pconditions)):
			if d==self.Pconditions[i][0]: delindex.append(i)
		
		for i in delindex: del self.Pconditions[i]
	
	def putPeriodic(self,pIn):
		for c in self.Pconditions:
			(d,period,Mod)=c
			pIn.data[d]=Mod(pIn.data[d],period)
		
	def setBound(self,d,smallbig,ri,threshold):
		if d>=self.dim or d<0: return
		
		if threshold:
			if (d,smallbig,ri) not in ( (c[0],c[1],c[2]) for c in self.Bconditions):
				self.Bconditions.append((d,smallbig,ri,threshold))
			else:
				i=self.Bconditions.index([c for c in self.Bconditions if (c[0],c[1],c[2])==(d,smallbig,ri)][0])
				self.Bconditions[i]=(d,smallbig,ri,threshold)
		else:
			self.unsetBound(d,smallbig,ri)
	
	def unsetBound(self,d,smallbig,ri):
		if d>=self.dim or d<0: return
		
		delindex=[]
		for i in range(len(self.Bconditions)):
			c=self.Bconditions[i]
			if (d,smallbig,ri)==(c[0],c[1],c[2]): delindex.append(i)
		
		for i in delindex: del self.Bconditions[i]
	# The following 8 methods, {,un}set{Upper,Lower}{,I}, are wrapper for {,un}setBound.
	def setUpper(self,d,threshold):
		self.setBound(d,True,True,threshold)
		
	def setLower(self,d,threshold):
		self.setBound(d,False,True,threshold)
		
	def setUpperI(self,d,threshold):
		self.setBound(d,True,False,threshold)
		
	def setLowerI(self,d,threshold):
		self.setBound(d,False,False,threshold)
	
	def unsetUpper(self,d):
		self.unsetBound(d,True,True)
	
	def unsetLower(self,d):
		self.unsetBound(d,False,True)
	
	def unsetUpperI(self,d):
		self.unsetBound(d,True,False)
	
	def unsetLowerI(self,d):
		self.unsetBound(d,False,False)
	
	def _PutBounded(self,pIn):
		check=numpy.ones(pIn.data[0].shape,bool)
		
		for (d,smallbig,ri,threshold) in self.Bconditions:
			check = check * ((pIn.data[d]>threshold) ^ (smallbig))
		
		index=numpy.where(check)
		pIn.data=[d[index] for d in pIn.data]
		
		if index!=None: return index

	def _PutBoundedC(self,pIn):
		check=numpy.ones(pIn.data[0].shape,bool)
		
		for (d,smallbig,ri,threshold) in self.Bconditions:
			if ri: check = check * ( (pIn.data[d].real>threshold) ^ (smallbig) )
			else: check = check * ( (pIn.data[d].imag>threshold) ^ (smallbig) )
		index=numpy.where(check)
		pIn.data=[d[index] for d in pIn.data]
		
		if index!=None: return index
		
class Hole(Point):
	def __init__(self,dim,isComplex=False,distance=None,center=None,size=None):
		Point.__init__(self,dim,isComplex)
		
		if distance!=None: self.setDistance(distance)
		if center!=None: self.setCenter(center)
		if size!=None: self.setSize(size)
	
	def setDistance(self,distance):
		self.distance=distance
	
	def setCenter(self,center):
		self.data=center.data
		
	def setSize(self,size):
		self.size=size
		
	def put(self,pIn):
		centers=Point(self.dim,self.isComplex)
		n=len(pIn.data[0])
		centers.data=[numpy.ones(n)*self.data[d] for d in range(self.dim)]
		d=self.distance(pIn,centers)
		index=numpy.where(d>self.size)
		pIn.data=[d[index] for d in pIn.data]
		return index

class HoleStripe(Space):
	def __init__(self,dim,isComplex=False):
		Space.__init__(self,dim,isComplex)
		
		self.conditions=[]
		
	def setStripe(self,d,min,max):
		if d>=self.dim or d<0: return
		if min > max: (min,max)=(max,min)
		
		if d not in (c[0] for c in self.conditions):
			self.conditions.append((d,min,max))
		else:
			i=self.conditions.index([c for c in self.conditions if c[0]==d][0])
			self.conditions[i]=(d,min,max)
		
	def put(self,pIn):
		con=numpy.zeros(len(pIn.data[0]),numpy.bool)
		for c in self.conditions:
			(d,min,max)=c
			con=con | (pIn.data[d]<min) | (pIn.data[d]>max)
		
		index=numpy.where(con)
		pIn.data=[d[index] for d in pIn.data]
		return index
	
class Perturbation(Space):
	"""
	TODO: define perturbation
	"""
	def __init__(self,dim,isComplex=False):
		Space.__init__(self,dim,isComplex)
		
	def setPerturb(self):
		pass
		
	def put(self,pIn):
		pass


class MapSystem(Space):
	"""
	Map system class. You are recommended to use this MapSystem class to 
	operate and manipurate a map with periodic/bounded boundary conditions.
	`PInit` keeps initial coordinate data and `Remain` stores index of 
	remaining point.
	"""
	def __init__(self,map,trajectory=False):
		Space.__init__(self,map.dim,map.isComplex)
		self.map=map
		
		self.MapName=map.__class__.__name__
		
		self.P=map.pIn
		self.Para=map.Para
		
		self.PInit=Point(self.dim,self.isComplex)
		self.Remain=[]
		self.Trajectory=[]
		
		self.phasespace=PhaseSpace(self.dim,self.isComplex)
		self.holes=[]
		self.perturbations=[]
		
		if hasattr(self.map,'Psetting'):self.Psetting=map.Psetting
		else: self.Psetting=[(False,0.0) for d in range(self.dim)]
		
		self.maxImag=100
		
		# (LBounded,Lbound,UBounded,Ubound) if not is complex else (LBounded,Lbound,UBounded,Ubound,LBoundedI,LboundI,UBoundedI,UboundI)
		if hasattr(self.map,'Bsetting'):self.Bsetting=map.Bsetting
		else: self.Bsetting=[(False,0.0,False,0.0) if not self.isComplex else (False,0.0,False,0.0,True,-self.maxImag,True,self.maxImag) for d in range(self.dim)]
		
		self.setPeriodic(self.Psetting)
		self.setBounded(self.Bsetting)
		
		self.setTrajectory(trajectory)
		
	def setTrajectory(self,trajectory):
		if trajectory: self.evolve=self._evolveTrajectory
		else: self.evolve=self._evolve
		
		
	def setMaxImag(self,maximag):
		#TODO
		self.maxImag=maximag
		if self.maxImag:
			for d in range(self.dim):
				self.phasespace.setUpperI(d, self.maxImag)
				self.phasespace.setLowerI(d,-self.maxImag)
		else:
			for d in range(self.dim):
				self.phasespace.unsetUpperI(d)
				self.phasespace.unsetLowerI(d)
		
	def setInit(self,p):
		self.map.setIn(p)
		self.phasespace.putPeriodic(self.map.pIn)
		self.PInit.data=[d for d in self.map.pIn.data]
		self.Remain=numpy.arange(len(self.map.pIn.data[0]))
		self.Trajectory=[]
		for i in self.Remain:
			self.Trajectory.append([[self.map.pIn.data[d][i] for d in range(self.map.pIn.dim)]])
	
	def _evolve(self):
		self.map.evol()
		
		self.phasespace.putPeriodic(self.map.pIn)
		
		index=self.phasespace.putBounded(self.map.pIn)
		if index!=None: self.Remain=self.Remain[index]
		
		for h in self.holes:
			index=h.put(self.map.pIn)
			if index!=None: self.Remain=self.Remain[index]
		
		for p in self.perturbations:
			index=p.put(self.map.pIn)
			if index!=None: self.Remain=self.Remain[index]
		
	def _evolveTrajectory(self):
		self._evolve()
		for (n,i) in enumerate(self.Remain):
			self.Trajectory[i].append([self.map.pIn.data[d][n] for d in range(self.map.pIn.dim)])
		
	def evolves(self,n):
		for i in range(n): self.evolve()
	
	def setPeriodic(self,Psetting):
		for d in range(self.dim):
			(isPeriodic,period)=Psetting[d]
			if isPeriodic:
				self.phasespace.setPeriod(d,period)
			else:
				self.phasespace.unsetPeriod(d)
		self.Psetting=Psetting
	
	def setBounded(self,Bsetting):
		for d in range(self.dim):
			'''
			bsetting=Bsetting[d]
			for n in range(len(bsetting)/2):
				if n<2:
					if bsetting[n*2]: self.phasespace.setBound(d,n%2,n/2,bsetting[n*2+1])
					else: self.phasespace.unsetBound(d,n%2,n/2)
				else:
					b=min(bsetting[n*2+1], self.maxImag) if bsetting[n*2] else self.maxImag
					self.phasespace.setBound(d,n%2,n/2,b)
			'''
			# The following part in this for-loop is equivalent to the commented part above.
			# This may be easy-to-understand.
			if not self.isComplex: (LBounded,Lbound,UBounded,Ubound)=Bsetting[d]
			else: (LBounded,Lbound,UBounded,Ubound,LBoundedI,LboundI,UBoundedI,UboundI)=Bsetting[d]
			
			if LBounded:
				self.phasespace.setLower(d,Lbound)
			else: 
				self.phasespace.unsetLower(d)
			if UBounded:
				self.phasespace.setUpper(d,Ubound)
			else:
				self.phasespace.unsetUpper(d)
			
			if self.isComplex:	
				if LBoundedI and LboundI>-self.maxImag:
					self.phasespace.setLowerI(d,LboundI)
				else: 
					self.phasespace.setLowerI(d,-self.maxImag)
				
				if UBoundedI and UboundI< self.maxImag:
					self.phasespace.setUpperI(d,UboundI)
				else:
					self.phasespace.setUpperI(d,self.maxImag)
		
		if self.isComplex: self.setMaxImag(self.maxImag)
		self.Bsetting=Bsetting
			
	def addHoleBox(self,center,size):
		self.holes.append( Hole(self.dim,self.isComplex,self.phasespace.DistanceLin,center,size) )
	
	def addHoleCircle(self,center,size):
		self.holes.append( Hole(self.dim,self.isComplex,self.phasespace.DistanceEuc,center,size) )
	
	def addHoleStripe(self,setting):
		h=HoleStripe(self.dim,self.isComplex)
		for d in range(self.dim):
			(hasHole,min,max)=setting[d]
			if hasHole: h.setStripe(d,min,max)
		self.holes.append(h)
		
	def clearHoles(self):
		self.holes=[]
		
	def addPerturbation(self):
		p=Perturbation(self.dim,self.isComplex)
		#p.setPerturb()
		self.perturbations.append(p)
		
	def clone(self,trajectory=False):
		mapsystem=MapSystem(self.map.__class__(isComplex=self.isComplex),trajectory)
		mapsystem.setPeriodic(self.Psetting)
		mapsystem.setBounded(self.Bsetting)
		mapsystem.Para.para=[p for p in self.Para.para]
		return mapsystem
	


