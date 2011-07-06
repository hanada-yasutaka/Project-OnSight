import MapSystem
import numpy

rect=0
circle=1
box=2

def _makeCirclePoint(p,center,radius,distance,sample):
	p.data=[numpy.array([]) for d in p.data]
	while len(p.data[0])<sample:
		sam=sample-len(p.data[0])
		pp=MapSystem.Point(p.dim,p.isComplex)
		pp.data=[(center.data[d]-radius)+2*radius*numpy.random.random(sam) for d in range(p.dim)]
		index=numpy.where(distance(center,pp)<radius)
		p.data=[numpy.hstack((p.data[d],pp.data[d][index])) for d in range(p.dim)]
	
def _makeRectPoint(p,rect,sample):
	p.data=[rect[d][0]+(rect[d][1]-rect[d][0])*numpy.random.random(sample) for d in range(p.dim)]
	
def _makeBoxPoint(p,center,radius,sample):
	_makeRectPoint(p,[[center.data[d]-radius,center.data[d]+radius] for d in range(center.dim)],sample)

class TimeStatistics(object):
	def __init__(self,mapsystem):
		self.mapsystem=mapsystem.clone()
		self.mapsystem.map.Para=mapsystem.map.Para
		self.mapsystem.setPeriodic(mapsystem.Psetting)
		self.mapsystem.setBounded(mapsystem.Bsetting)
		
	def _calcDistribution(self,sample,time):
		self.cum=numpy.zeros(time)
		for t in range(time):
			self.cum[t]=len(self.mapsystem.Remain)
			self.mapsystem.evolve()
		self.cum=self.cum/float(sample)
		self.dist=numpy.append(numpy.zeros(1),numpy.diff(self.cum))
		self.dist=self.dist/self.dist.sum()
		
		self.average=numpy.average(numpy.arange(time),weights=self.dist)
		self.axis=numpy.arange(time)
	
	def getStartPoint(self,type,sample):
		p=MapSystem.Point(self.mapsystem.dim,self.mapsystem.isComplex)
		if type==rect:
			_makeRectPoint(p,self.startRect,sample)
		elif type==circle:
			_makeCirclePoint(p,self.startCenter,self.startRadius,self.mapsystem.phasespace.DistanceEuc,sample)
		elif type==box:
			_makeBoxPoint(p,self.startCenter,self.startRadius,sample)
		
		return p
	
class SurvivalTime(TimeStatistics):
	def __init__(self,mapsystem):
		TimeStatistics.__init__(self,mapsystem)
		
		self.startType=None
		
	def setStartRect(self,startRect):
		self.startType=rect
		self.startRect=startRect
		
	def setStartCircle(self,startCenter,startRadius):
		self.startType=circle
		self.startCenter=startCenter
		self.startRadius=startRadius
		
	def setStartBox(self,startCenter,startRadius):
		self.startType=box
		self.startCenter=startCenter
		self.startRadius=startRadius
	
	def calc(self,sample,time):
		if self.startType==None: return
		
		self.mapsystem.setInit(self.getStartPoint(self.startType,sample))
		
		self._calcDistribution(sample,time)

class HittingTime(SurvivalTime):
	def __init__(self,mapsystem):
		SurvivalTime.__init__(self,mapsystem)
		
		self.startType=None
		self.endType=None
		
	def setEndRect(self,endRect):
		self.endType=rect
		self.mapsystem.clearHoles()
		
		if len(endRect)==self.mapsystem.dim:
			setting=[]
			for (min,max) in endRect:
				setting.append( (True,min,max) )
		else:
			raise TypeError
		self.mapsystem.addHoleStripe(setting)
		
	def setEndCircle(self,endCenter,endRadius):
		self.endType=circle
		self.mapsystem.clearHoles()
		
		self.mapsystem.addHoleCircle(endCenter,endRadius)
		
	def setEndBox(self,endCenter,endRadius):
		self.endType=box
		self.mapsystem.clearHoles()
		
		self.mapsystem.addHoleBox(endCenter,endRadius)
		
	def calc(self,sample,time):
		if self.startType==None or self.endType==None: return
		
		self.mapsystem.setInit(self.getStartPoint(self.startType,sample))
		
		self._calcDistribution(sample,time)
		
	
class RecurrenceTime(HittingTime):
	def __init__(self,mapsystem):
		HittingTime.__init__(self,mapsystem)
	
	def setRegionRect(self,regionRect):
		self.setStartRect(regionRect)
		self.setEndRect(regionRect)
		
	def setRegionCircle(self,regionCenter,regionRadius):
		self.setStartCircle(regionCenter,regionRadius)
		self.setEndCircle(regionCenter,regionRadius)
		
	def setRegionBox(self,regionCenter,regionRadius):
		self.setStartBox(regionCenter,regionRadius)
		self.setEndBox(regionCenter,regionRadius)
		
class MeetingTime(TimeStatistics):
	def __init__(self,mapsystem):
		TimeStatistics.__init__(self,mapsystem)
		
	def setPointCircle(self,center,radius):
		self.pointType=circle
		self.pointCenter=center
		self.pointRadius=radius
		
	def setPointBox(self,center,radius):
		self.pointType=box
		self.pointCenter=center
		self.pointRadius=radius
		
	def calc(self,sample,time):
		pass
		
