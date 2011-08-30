import wx
import wx.lib.scrolledpanel
import Utils
import numpy


class _SubPanel(wx.lib.scrolledpanel.ScrolledPanel):
	def __init__(self,parent,mapsystem,title):
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self,parent,-1)
		
		self.SetupScrolling()
		
		self.mapsystem=mapsystem.clone()
		self.mapsystem.Para=mapsystem.Para
		self.mapsystem.map.Para=mapsystem.Para
		self.mapsystem.phasespace=mapsystem.phasespace
		self.title=title
		
	def LogWrite(self,message):
		self.GetParent().GetParent().LogWrite(message)
		
	def GetDEBUG(self):
		return self.GetParent().GetParent().GetDEBUG()


from PoincarePlotPanel import PoincarePlotPanel
from RecurrenceTimePanel import RecurrenceTimePanel
from SurvivalTimePanel import SurvivalTimePanel
from HittingTimePanel import HittingTimePanel
from MsetPanel import MsetPanel
from QuantumPanel import QuantumPanel
from QmapEigenPanel import QmapEigenPanel



panels={
	'Poincare Plot':PoincarePlotPanel,
	'Recurrence Time':RecurrenceTimePanel,
	'Survival Time':SurvivalTimePanel,
	'Hitting Time':HittingTimePanel,
	'M set':MsetPanel,
	'Quantum Map':QuantumPanel,
	'Qmap Eigen':QmapEigenPanel
}

class MainPanel(wx.Notebook):
	def __init__(self,parent): 

		wx.Notebook.__init__(self,parent,-1)
		self.parent=parent
		
		description=Utils.Description(self)
		description.LoadDescription(parent.mapsystem.MapName)
		self.AddPage(description,"Description")
		
		self.mapsystem=parent.mapsystem
		
		#### debug 
		panelname='Poincare Plot'
		#~ panelname='Recurrence Time'
		self.AddPage(panels[panelname](self,self.mapsystem,panelname),panelname)
		self.SetSelection(self.GetPageCount()-1)
		#### debug 
		
	def CreateMenuMain(self):
		menu=wx.Menu()
		
		self.ids=[]
		for key in panels.keys():
			id=wx.NewId()
			item=menu.Append(id,key)
			self.parent.Bind(wx.EVT_MENU,self.OnNewPanel,id=id)
			self.ids.append(id)
		
		return menu
		
	def OnNewPanel(self,event):
		id=event.GetId()
		index=self.ids.index(id)
		label,panel=panels.items()[index]
		self.AddPage(panel(self,self.mapsystem,label),label)
		self.SetSelection(self.GetPageCount()-1)
		
		event.GetEventObject().Enable(id,False)
		
	def GetPages(self):
		pages={}
		for i in range(self.GetPageCount()):
			pages[self.GetPageText(i)]=self.GetPage(i)
		return pages
		
	
