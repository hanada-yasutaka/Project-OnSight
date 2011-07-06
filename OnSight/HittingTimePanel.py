import wx
import wx.xrc
import Utils
import maps.MapSystem,maps.TimeStatistics
import numpy

from MainPanel import _SubPanel

class HittingTimePanel(_SubPanel):
	def __init__(self,parent,mapsystem,title):
		_SubPanel.__init__(self,parent,mapsystem,title)
		
		#### Loading XRC file and Setting the panel
		xmlresource=wx.xrc.XmlResource("OnSight/data/xrc/hittingtimepanel.xrc")
		self.panel=xmlresource.LoadPanel(self,"hittingtimepanel")
		
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
		sizer2=wx.xrc.XRCCTRL(self.panel,'StaticLine2').GetContainingSizer()
		self.TCListRectStart=Utils._putTextCtrlFlexGrid(self.panel,sizer1.GetChildren()[2].GetSizer(),input,
			proportion_st=proportion_st,flag_st=flag_st,style_tc=style_tc,proportion_tc=proportion_tc,flag_tc=flag_tc)
		self.TCListRectEnd=Utils._putTextCtrlFlexGrid(self.panel,sizer2.GetChildren()[2].GetSizer(),input,
			proportion_st=proportion_st,flag_st=flag_st,style_tc=style_tc,proportion_tc=proportion_tc,flag_tc=flag_tc)
		
		input=[[axislabel[d]+': ', 'center ', 0.0] for d in range(self.mapsystem.dim)]
		input.append(['','edge ',1.0])
		
		self.TCListBoxStart=Utils._putTextCtrlFlexGrid(self.panel,sizer1.GetChildren()[3].GetSizer(),input,
			proportion_st=proportion_st,flag_st=flag_st,style_tc=style_tc,proportion_tc=proportion_tc,flag_tc=flag_tc)
		self.TCListBoxEnd=Utils._putTextCtrlFlexGrid(self.panel,sizer2.GetChildren()[3].GetSizer(),input,
			proportion_st=proportion_st,flag_st=flag_st,style_tc=style_tc,proportion_tc=proportion_tc,flag_tc=flag_tc)
		
		input=[[axislabel[d]+': ', 'center ', 0.0] for d in range(self.mapsystem.dim)]
		input.append(['','radius ',1.0])
		
		self.TCListCircleStart=Utils._putTextCtrlFlexGrid(self.panel,sizer1.GetChildren()[4].GetSizer(),input,
			proportion_st=proportion_st,flag_st=flag_st,style_tc=style_tc,proportion_tc=proportion_tc,flag_tc=flag_tc)
		self.TCListCircleEnd=Utils._putTextCtrlFlexGrid(self.panel,sizer2.GetChildren()[4].GetSizer(),input,
			proportion_st=proportion_st,flag_st=flag_st,style_tc=style_tc,proportion_tc=proportion_tc,flag_tc=flag_tc)
		
		for i in range(3):
			sizer1.Show(i+2,i==0)
			sizer2.Show(i+2,i==0)
		
		#### Event Handling
		def OnSpinCtrlSample(event):
			self.sample=event.GetInt()
		def OnSpinCtrlIteration(event):
			self.iteration=event.GetInt()
		def OnRadioBoxTypeStart(event):
			self.typeStart=event.GetSelection()
			sizer1=wx.xrc.XRCCTRL(self.panel,'StaticLine1').GetContainingSizer()
			for i in range(3):
				sizer1.Show(i+2, i==self.typeStart)
			self.panel.Layout()
		def OnRadioBoxTypeEnd(event):
			self.typeEnd=event.GetSelection()
			sizer1=wx.xrc.XRCCTRL(self.panel,'StaticLine2').GetContainingSizer()
			for i in range(3):
				sizer1.Show(i+2, i==self.typeEnd)
			self.panel.Layout()
		def OnButtonDraw(event):
			self.SetStart()
			self.SetEnd()
			self.hittingtime.calc(self.sample,self.iteration)
			wx.xrc.XRCCTRL(self.panel,'TextCtrlAverage').SetValue(str(self.hittingtime.average))
			self.distplotpanel.plot(self.hittingtime.axis,self.hittingtime.dist,'-')
			self.cumplotpanel.plot(self.hittingtime.axis,self.hittingtime.cum,'-')
		
		self.Bind(wx.EVT_SPINCTRL, OnSpinCtrlSample, wx.xrc.XRCCTRL(self.panel,'SpinCtrlSample'))
		self.Bind(wx.EVT_SPINCTRL, OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration'))
		self.Bind(wx.EVT_RADIOBOX, OnRadioBoxTypeStart, wx.xrc.XRCCTRL(self.panel,'RadioBoxTypeStart'))
		self.Bind(wx.EVT_RADIOBOX, OnRadioBoxTypeEnd, wx.xrc.XRCCTRL(self.panel,'RadioBoxTypeEnd'))
		self.Bind(wx.EVT_BUTTON, OnButtonDraw, wx.xrc.XRCCTRL(self.panel,'ButtonDraw'))
		
		#### Creating PlotPanel and hittingTime, Setting default values
		self.distplotpanel=parent.GetParent().MakePlotPanel(self.title+' Distrbution')
		self.cumplotpanel=parent.GetParent().MakePlotPanel(self.title+' Cumulative Distrbution')
		
		self.hittingtime=maps.TimeStatistics.HittingTime(self.mapsystem)
		
		self.sample=wx.xrc.XRCCTRL(self.panel,'SpinCtrlSample').GetValue()
		self.iteration=wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
		self.typeStart=wx.xrc.XRCCTRL(self.panel,'RadioBoxTypeStart').GetSelection()
		self.typeEnd=wx.xrc.XRCCTRL(self.panel,'RadioBoxTypeEnd').GetSelection()
		
		self.SetStart()
		self.SetEnd()
		
	def SetStart(self):
		if self.typeStart==0:
			self.hittingtime.setStartRect([(l[0].value,l[1].value) for l in self.TCListRectStart])
		if self.typeStart==1:
			data=[l[0].value for l in self.TCListBoxStart]
			center=data[0:-1]
			edge=data[-1]
			self.hittingtime.setStartBox(maps.MapSystem.Point(self.mapsystem.dim, data=center),edge)
		if self.typeStart==2:
			data=[l[0].value for l in self.TCListCircleStart]
			center=data[0:-1]
			radius=data[-1]
			self.hittingtime.setStartCircle(maps.MapSystem.Point(self.mapsystem.dim, data=center),radius)
		
	def SetEnd(self):
		if self.typeEnd==0:
			self.hittingtime.setEndRect([(l[0].value,l[1].value) for l in self.TCListRectEnd])
		if self.typeEnd==1:
			data=[l[0].value for l in self.TCListBoxEnd]
			center=data[0:-1]
			edge=data[-1]
			self.hittingtime.setEndBox(maps.MapSystem.Point(self.mapsystem.dim, data=center),edge)
		if self.typeEnd==2:
			data=[l[0].value for l in self.TCListCircleEnd]
			center=data[0:-1]
			radius=data[-1]
			self.hittingtime.setEndCircle(maps.MapSystem.Point(self.mapsystem.dim, data=center),radius)
		
