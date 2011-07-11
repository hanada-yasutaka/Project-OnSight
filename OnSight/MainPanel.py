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


from PoincarePlotPanel import PoincarePlotPanel
from RecurrenceTimePanel import RecurrenceTimePanel
from SurvivalTimePanel import SurvivalTimePanel
from HittingTimePanel import HittingTimePanel
from MsetPanel import MsetPanel



panels={
	'Poincare Plot':PoincarePlotPanel,
	'Recurrence Time':RecurrenceTimePanel,
	'Survival Time':SurvivalTimePanel,
	'Hitting Time':HittingTimePanel,
	'Mset':MsetPanel
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
	
