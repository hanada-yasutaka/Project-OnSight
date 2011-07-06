import wx
import wx.xrc
import Utils
import maps.MapSystem,maps.TimeStatistics
import numpy

from MainPanel import _SubPanel

class RecurrenceTimePanel(_SubPanel):
	def __init__(self,parent,mapsystem,title):
		_SubPanel.__init__(self,parent,mapsystem,title)
		
		#### Loading XRC file and Setting the panel
		xmlresource=wx.xrc.XmlResource("OnSight/data/xrc/recurrencetimepanel.xrc")
		self.panel=xmlresource.LoadPanel(self,"recurrencetimepanel")
		
		sizer=wx.BoxSizer()
		sizer.Add(self.panel,proportion=1,flag= wx.ALL | wx.EXPAND)
		self.SetSizer(sizer)
		
		#### Creating TextCtrls and StaticTexts 
		axislabel=Utils.getAxisLabel(self.mapsystem)
		
		proportion_st=0
		proportion_tc=1
		style_tc=wx.TE_RIGHT
		flag_st=flag_tc=wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL
		
		input=[[axislabel[d]+': ', 'min ', 0.0, 'max ', 1.0] for d in range(self.mapsystem.dim)]
		
		sizer1=wx.xrc.XRCCTRL(self.panel,'StaticLine1').GetContainingSizer()
		self.TCListRect=Utils._putTextCtrlFlexGrid(self.panel,sizer1.GetChildren()[2].GetSizer(),input,
			proportion_st=proportion_st,flag_st=flag_st,style_tc=style_tc,proportion_tc=proportion_tc,flag_tc=flag_tc)
		
		input=[[axislabel[d]+': ', 'center ', 0.0] for d in range(self.mapsystem.dim)]
		input.append(['','edge ',1.0])
		
		self.TCListBox=Utils._putTextCtrlFlexGrid(self.panel,sizer1.GetChildren()[3].GetSizer(),input,
			proportion_st=proportion_st,flag_st=flag_st,style_tc=style_tc,proportion_tc=proportion_tc,flag_tc=flag_tc)
		
		input=[[axislabel[d]+': ', 'center ', 0.0] for d in range(self.mapsystem.dim)]
		input.append(['','radius ',1.0])
		
		self.TCListCircle=Utils._putTextCtrlFlexGrid(self.panel,sizer1.GetChildren()[4].GetSizer(),input,
			proportion_st=proportion_st,flag_st=flag_st,style_tc=style_tc,proportion_tc=proportion_tc,flag_tc=flag_tc)
		
		for i in range(3): sizer1.Show(i+2,i==0)
		
		#### Event Handling
		def OnSpinCtrlSample(event):
			self.sample=event.GetInt()
		def OnSpinCtrlIteration(event):
			self.iteration=event.GetInt()
		def OnRadioBoxType(event):
			self.type=event.GetSelection()
			sizer1=wx.xrc.XRCCTRL(self.panel,'StaticLine1').GetContainingSizer()
			for i in range(3):
				sizer1.Show(i+2, i==self.type)
			self.panel.Layout()
		def OnButtonDraw(event):
			self.SetRegion()
			self.recurrencetime.calc(self.sample,self.iteration)
			wx.xrc.XRCCTRL(self.panel,'TextCtrlAverage').SetValue(str(self.recurrencetime.average))
			self.distplotpanel.plot(self.recurrencetime.axis,self.recurrencetime.dist,'-')
			self.cumplotpanel.plot(self.recurrencetime.axis,self.recurrencetime.cum,'-')
		
		self.Bind(wx.EVT_SPINCTRL, OnSpinCtrlSample, wx.xrc.XRCCTRL(self.panel,'SpinCtrlSample'))
		self.Bind(wx.EVT_SPINCTRL, OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration'))
		self.Bind(wx.EVT_RADIOBOX, OnRadioBoxType, wx.xrc.XRCCTRL(self.panel,'RadioBoxType'))
		self.Bind(wx.EVT_BUTTON, OnButtonDraw, wx.xrc.XRCCTRL(self.panel,'ButtonDraw'))
		
		#### Creating PlotPanel and RecurrenceTime, Setting default values
		self.distplotpanel=parent.GetParent().MakePlotPanel(self.title+' Distrbution')
		self.cumplotpanel=parent.GetParent().MakePlotPanel(self.title+' Cumulative Distrbution')
		
		self.recurrencetime=maps.TimeStatistics.RecurrenceTime(self.mapsystem)
		
		self.sample=wx.xrc.XRCCTRL(self.panel,'SpinCtrlSample').GetValue()
		self.iteration=wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
		self.type=wx.xrc.XRCCTRL(self.panel,'RadioBoxType').GetSelection()
		
		self.SetRegion()
		
	def SetRegion(self):
		if self.type==0:
			self.recurrencetime.setRegionRect([(l[0].value,l[1].value) for l in self.TCListRect])
		if self.type==1:
			data=[l[0].value for l in self.TCListBox]
			center=data[0:-1]
			edge=data[-1]
			self.recurrencetime.setRegionBox(maps.MapSystem.Point(self.mapsystem.dim, data=center),edge)
		if self.type==2:
			data=[l[0].value for l in self.TCListCircle]
			center=data[0:-1]
			radius=data[-1]
			self.recurrencetime.setRegionCircle(maps.MapSystem.Point(self.mapsystem.dim, data=center),radius)
		
