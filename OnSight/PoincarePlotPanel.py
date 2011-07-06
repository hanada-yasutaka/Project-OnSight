import wx
import wx.xrc
import numpy
import maps.MapSystem

from MainPanel import _SubPanel

import Utils

class PoincarePlotPanel(_SubPanel):
	def __init__(self,parent,mapsystem,title):
		_SubPanel.__init__(self,parent,mapsystem,title)
		#### Loading XRC file and Setting the panel
		xmlresource=wx.xrc.XmlResource("OnSight/data/xrc/poincareplotpanel.xrc")
		self.panel=xmlresource.LoadPanel(self,"poincareplotpanel")
		
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
		def OnRadioBoxRandom(event):
			self.random=(event.GetSelection()==0)
		def OnCheckBoxTrajectory(event):
			self.trajectory=event.IsChecked()
			wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(enable=1-self.trajectory)
			wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(enable=1-self.trajectory)
		def OnButtonDraw(event):
			self.SetInitialPoints()
			self.mapsystem.evolves(self.iteration)
			self.Draw()
		def OnButtonPrev(event):
			if self.iteration<=0: return
			self.iteration= self.iteration-1
			wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').SetValue(self.iteration)
			OnButtonDraw(event)
		def OnButtonNext(event):
			self.iteration= self.iteration+1
			wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').SetValue(self.iteration)
			OnButtonDraw(event)
			
			
		self.Bind(wx.EVT_SPINCTRL, OnSpinCtrlSample, wx.xrc.XRCCTRL(self.panel,'SpinCtrlSample'))
		self.Bind(wx.EVT_SPINCTRL, OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration'))
		self.Bind(wx.EVT_RADIOBOX, OnRadioBoxType, wx.xrc.XRCCTRL(self.panel,'RadioBoxType'))
		self.Bind(wx.EVT_RADIOBOX, OnRadioBoxRandom, wx.xrc.XRCCTRL(self.panel,'RadioBoxRandom'))
		self.Bind(wx.EVT_CHECKBOX, OnCheckBoxTrajectory, wx.xrc.XRCCTRL(self.panel,'CheckBoxTrajectory'))
		self.Bind(wx.EVT_BUTTON, OnButtonPrev, wx.xrc.XRCCTRL(self.panel,'ButtonPrev'))
		self.Bind(wx.EVT_BUTTON, OnButtonNext, wx.xrc.XRCCTRL(self.panel,'ButtonNext'))
		self.Bind(wx.EVT_BUTTON, OnButtonDraw, wx.xrc.XRCCTRL(self.panel,'ButtonDraw'))
		
		#### Creating PlotPanel, Setting default values
		self.plotpanel=parent.GetParent().MakePlotPanel(self.title)
		
		self.plotpanel.OnPress=self.OnPress
		
		self.sample=wx.xrc.XRCCTRL(self.panel,'SpinCtrlSample').GetValue()
		self.iteration=wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
		self.type=wx.xrc.XRCCTRL(self.panel,'RadioBoxType').GetSelection()
		self.random=(wx.xrc.XRCCTRL(self.panel,'RadioBoxRandom').GetSelection()==0)
		self.trajectory=wx.xrc.XRCCTRL(self.panel,'CheckBoxTrajectory').IsChecked()
		
		self.SetInitialPoints()
		self.mapsystem.evolves(self.iteration)
		self.Draw()
		
	def SetInitialPoints(self):
		self.mapsystem.setTrajectory(self.trajectory)
		
		p=maps.MapSystem.Point(self.mapsystem.dim)
		if self.type==0:
			maps.TimeStatistics._makeRectPoint(p,[(l[0].value,l[1].value) for l in self.TCListRect],self.sample)
			self.mapsystem.setInit(p)
		if self.type==1:
			data=[l[0].value for l in self.TCListBox]
			center=maps.MapSystem.Point(self.mapsystem.dim,data=data[0:-1])
			edge=data[-1]
			maps.TimeStatistics._makeBoxPoint(p,center,edge,self.sample)
			self.mapsystem.setInit(p)
		if self.type==2:
			data=[l[0].value for l in self.TCListCircle]
			center=maps.MapSystem.Point(self.mapsystem.dim,data=data[0:-1])
			radius=data[-1]
			maps.TimeStatistics._makeCirclePoint(p,center,radius,self.mapsystem.phasespace.DistanceEuc,self.sample)
			self.mapsystem.setInit(p)
		
	def Draw(self):
		xy=numpy.array(self.mapsystem.Trajectory[0]).transpose() if self.trajectory else numpy.array(self.mapsystem.P.data).transpose()[0]
		self.plotpanel.plot(xy[0],xy[1],',')
		for i in range(1,len(self.mapsystem.Remain)):
			xy=numpy.array(self.mapsystem.Trajectory[i]).transpose().tolist() if self.trajectory else numpy.array(self.mapsystem.P.data).transpose()[i]
			self.plotpanel.replot(xy[0],xy[1],',')
		self.plotpanel.draw()
		
		wx.xrc.XRCCTRL(self.panel,'TextCtrlRemain').SetValue(str(len(self.mapsystem.Remain)))
		
	def OnPress(self,xy):
		self.mapsystem.setTrajectory(self.trajectory)
		self.mapsystem.setInit(maps.MapSystem.Point(self.mapsystem.dim,data=[xy[0],xy[1]]))
		self.mapsystem.evolves(self.iteration)
		
		xy=numpy.array(self.mapsystem.Trajectory[0]).transpose() if self.trajectory else numpy.array(self.mapsystem.P.data).transpose()[0]
		self.plotpanel.replot(xy[0],xy[1],',')
		self.plotpanel.draw()
	
