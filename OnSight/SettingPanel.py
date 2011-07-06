import string

import wx
import wx.lib.scrolledpanel
import Utils

sliderSize=(200, -1)
sliderMinValue=0
sliderMaxValue=100
sliderValue=0

choiceSize=(80, -1)

class NumericValidator(wx.PyValidator):
	def __init__(self):
		wx.PyValidator.__init__(self)
		self.Bind(wx.EVT_CHAR, self.OnChar)
		
	def Clone(self):
		return NumericValidator()
		
	def OnChar(self,event):
		key = event.GetKeyCode()
		if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
			event.Skip()
			return
		
		if chr(key) in string.digits+'.'+'-':
			event.Skip()
			return
		return

class ParameterPanel(wx.Panel):
	def __init__(self,parent,mapsystem):
		wx.Panel.__init__(self,parent,-1)
		self.ParameterLabel=Utils.getParameterLabel(mapsystem)
		
		self.Para=mapsystem.Para
		self.parameters=[p for p in mapsystem.Para.para]
		
		# parameter box
		sizer=wx.StaticBoxSizer(wx.StaticBox(self,-1,u'Parameter'),wx.VERTICAL)
		
		radiobox=wx.RadioBox(self, -1,choices=['Slider','Value'],style=wx.RA_HORIZONTAL | wx.NO_BORDER)
		self.Bind(wx.EVT_RADIOBOX, self.EventParameterBox, radiobox)
		
		sizer.Add(radiobox,0,wx.ALIGN_LEFT|wx.ALIGN_TOP)
		sizer.Add(self.CreateParameterBoxSlider(),1,wx.EXPAND|wx.ALL)
		sizer.Add(self.CreateParameterBoxValue(),1,wx.EXPAND|wx.ALL)
		
		sizer.Show(1,True)
		sizer.Show(2,False)
		sizer.Layout()
		
		self.SetSizer(sizer)
		
	def CreateParameterBoxSlider(self):
		sizer=wx.FlexGridSizer(self.Para.num,3)
		self.sliderIds=[]
		self.texts=[]
		self.textIds=[]
		self.MinValue=[0.0 for i in range(self.Para.num)]
		self.MaxValue=[10.0 for i in range(self.Para.num)]
		
		for i in range(self.Para.num):
			label=wx.StaticText(self,-1,self.ParameterLabel[i]+' = ')
			
			textId=wx.NewId()
			self.textIds.append(textId)
			text=wx.TextCtrl(self,textId,value=str(self.Para.para[i]),style=wx.TE_RIGHT | wx.TE_READONLY)
			self.texts.append(text)
			
			if self.Para.range[i][0] is not None: self.MinValue[i]=min(self.Para.range[i][0],self.parameters[i])
			if self.Para.range[i][1] is not None: self.MaxValue[i]=max(self.Para.range[i][1],self.parameters[i])
			
			sliderId=wx.NewId()
			self.sliderIds.append(sliderId)
			sliderValue=int((sliderMaxValue-sliderMinValue) * (self.parameters[i]-self.MinValue[i])/(self.MaxValue[i]-self.MinValue[i]))
			slider=wx.Slider(self, sliderId, value=sliderValue, minValue=sliderMinValue, maxValue=sliderMaxValue, size=sliderSize,style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
			self.Bind(wx.EVT_SLIDER, self.OnSlider, slider)
			
			sizer.Add(label,0,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			sizer.Add(text,1,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			sizer.Add(slider,1,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
		
		return sizer
		
	def OnSlider(self,event):
		for i,id in enumerate(self.sliderIds):
			if id == event.GetEventObject().GetId():
				self.parameters[i]=self.MinValue[i]+(self.MaxValue[i]-self.MinValue[i])*event.GetInt()/float(sliderMaxValue-sliderMinValue)
				self.SetState(self.parameters)
		
	def CreateParameterBoxValue(self):
		sizer=wx.FlexGridSizer(self.Para.num,3)
		self.inputs=[]
		self.inputIds=[]
		self.buttonIds=[]
		for i in range(self.Para.num):
			label=wx.StaticText(self,-1,self.ParameterLabel[i]+' = ')
			
			inputId=wx.NewId()
			self.inputIds.append(inputId)
			input=wx.TextCtrl(self,inputId,value=str(self.Para.para[i]),size=(200,-1),style=wx.TE_RIGHT,validator=NumericValidator())
			self.inputs.append(input)
			self.Bind(wx.EVT_TEXT,self.OnInput,input)
			
			buttonId=wx.NewId()
			self.buttonIds.append(buttonId)
			button=wx.Button(self,buttonId,label='Math')
			
			sizer.Add(label,0,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			sizer.Add(input,1,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			sizer.Add(button,1,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
		
		return sizer
		
	def OnInput(self,event):
		for i,id in enumerate(self.inputIds):
			if id == event.GetEventObject().GetId():
				inputstr=self.inputs[i].GetValue()
				try:
					self.parameters[i]=float( inputstr )
				except ValueError:
					if inputstr=='':
						self.parameters[i]=0.0
					else:
						self.inputs[i].SetValue(str(self.parameters[i]))
		
	def EventParameterBox(self,event):
		if event.GetInt()==0:
			self.GetSizer().Show(1,True)
			self.GetSizer().Show(2,False)
		elif event.GetInt()==1:
			self.GetSizer().Show(1,False)
			self.GetSizer().Show(2,True)
		self.SetState(self.parameters)
		self.Layout()
		
	def SetState(self,parameters):
		for i in range(self.Para.num):
			self.texts[i].SetValue(str(parameters[i]))
			self.inputs[i].SetValue(str(parameters[i]))
		
	def OnApply(self):
		self.Para.para=[self.parameters[i] for i in range(self.Para.num)]
		
class BoundaryConditionPanel(wx.Panel):
	def __init__(self,parent,mapsystem):
		wx.Panel.__init__(self,parent,-1)
		self.AxisLabel=Utils.getAxisLabel(mapsystem)
		
		self.mapsystem=mapsystem
		self.phasespace=mapsystem.phasespace
		self.Psetting=[p for p in mapsystem.Psetting]
		self.Bsetting=[p for p in mapsystem.Bsetting]
		
		self.bsizer=wx.StaticBoxSizer(wx.StaticBox(self,-1,'Boundary Condition'),wx.VERTICAL)
		self.bsizer.Add(self.CreateBoundaryConditionBox(),1,wx.EXPAND|wx.ALL)
		
		self.SetState(self.Psetting,self.Bsetting)
		
		self.SetSizer(self.bsizer)
		
	def CreateBoundaryConditionBox(self):
		sizer=wx.BoxSizer(wx.VERTICAL)
		
		self.choiceIds=[]
		self.choices=[]
		self.periodIds=[]
		self.periods=[]
		self.checkIds=[]
		self.checks=[]
		self.boundIds=[]
		self.bounds=[]
		self.bcsizers=[]
		
		conditions=['None','Periodic','Bounded']
		for i in range(self.phasespace.dim):
			label=wx.StaticText(self,-1,self.AxisLabel[i]+' : ')
			
			choiceId=wx.NewId()
			self.choiceIds.append(choiceId)
			choice=wx.Choice(self,choiceId,size=choiceSize,choices=conditions)
			self.choices.append(choice)
			self.Bind(wx.EVT_CHOICE, self.OnChoice, choice)
			
			labelperiod=wx.StaticText(self,-1,'Period : ')
			
			periodId=wx.NewId()
			self.periodIds.append(periodId)
			period=wx.TextCtrl(self,periodId,value='',size=(40,-1),style=wx.TE_RIGHT,validator=NumericValidator())
			self.periods.append(period)
			
			periodsizer=wx.BoxSizer(wx.HORIZONTAL)
			periodsizer.Add(labelperiod,0,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			periodsizer.Add(period,0,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			
			numBounds=2 if not self.phasespace.isComplex else 4
			labels=['Lower : ','Upper : '] if not self.phasespace.isComplex else ['Lower : ','Upper : ','LowerI : ','UpperI : ']
			boundsizer=wx.BoxSizer(wx.HORIZONTAL)
			for num in range(numBounds):
				checkId=wx.NewId()
				self.checkIds.append(checkId)
				check=wx.wx.CheckBox(self,checkId,labels[num],style=wx.ALIGN_RIGHT)
				self.checks.append(check)
				self.Bind(wx.EVT_CHECKBOX,self.OnCheck,check)
				boundsizer.Add(check,0,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
				
				boundId=wx.NewId()
				self.boundIds.append(boundId)
				bound=wx.TextCtrl(self,boundId,value='',size=(40,-1),style=wx.TE_RIGHT,validator=NumericValidator())
				self.bounds.append(bound)
				boundsizer.Add(bound,0,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			
			bcsizer=wx.BoxSizer(wx.HORIZONTAL)
			self.bcsizers.append(bcsizer)
			
			bcsizer.Add(label,0,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			bcsizer.Add(choice,0,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			bcsizer.Add(periodsizer,0,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			bcsizer.Add(boundsizer,0,wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
			
			sizer.Add(bcsizer,0)
		
		return sizer
		
	def SetState(self,Psetting,Bsetting):
		for i in range(self.phasespace.dim):
			isPeriodic=Psetting[i][0]
			isBounded=Bsetting[i][0] | Bsetting[i][2] if not self.phasespace.isComplex else Bsetting[i][0] | Bsetting[i][2] | Bsetting[i][4] | Bsetting[i][6]
			if isPeriodic:
				selection=1
			elif isBounded:
				selection=2
			else:
				selection=0
			self.choices[i].SetSelection(selection)
			self.BCSizerShow(i,selection)
			
			if Psetting[i][0]: self.periods[i].SetValue(str(Psetting[i][1]))
			
			
			numBounds=2 if not self.phasespace.isComplex else 4
			
			for num in range(numBounds):
				index=i*numBounds+num
				self.checks[index].SetValue(Bsetting[i][num*2])
				if Bsetting[i][num*2]: self.bounds[index].SetValue(str(Bsetting[i][num*2+1]))
				else: self.bounds[index].Enable(False)
		
	def GetState(self):
		Psetting=[]
		Bsetting=[]
		for i in range(self.phasespace.dim):
			selection=self.choices[i].GetSelection()
			
			if selection==1:
				try:
					period=float( self.periods[i].GetValue() )
				except ValueError:
					message='Unable to set period for '+self.AxisLabel[i]+'. Input numerical value.'
					dlg=wx.MessageDialog(self,message,style=wx.OK | wx.ICON_INFORMATION)
					dlg.ShowModal()
					dlg.Destroy()
					raise ValueError
				pcondition=(True,period)
			else:
				pcondition=(False,0.0)
			Psetting.append(pcondition)
			
			numBounds=2 if not self.phasespace.isComplex else 4
			if selection==2:
				bcondition=[]
				for j in range(numBounds):
					checked=self.checks[i*numBounds+j].IsChecked()
					bcondition.append(checked)
					if checked:
						try:
							bound=float( self.bounds[i*numBounds+j].GetValue() )
						except ValueError:
							message='Unable to set bound for '+self.AxisLabel[i]+'. Input numerical value.'
							dlg=wx.MessageDialog(self,message,style=wx.OK | wx.ICON_INFORMATION)
							dlg.ShowModal()
							dlg.Destroy()
							raise ValueError
					else:
						bound=0.0
					bcondition.append(bound)
				bcondition=tuple(bcondition)
			else:
				bcondition=[]
				for j in range(numBounds):
					bcondition.append(False)
					bcondition.append(0.0)
				bcondition=tuple(bcondition)
			Bsetting.append(bcondition)
		
		return Psetting,Bsetting
	
	def OnCheck(self,event):
		for i,id in enumerate(self.checkIds):
			if id==event.GetEventObject().GetId():
				self.bounds[i].Enable(event.IsChecked())
				self.bounds[i].SetValue('0.0')
		
	def OnChoice(self,event):
		if event.GetId() in self.choiceIds:
			i=self.choiceIds.index(event.GetId())
			selection=event.GetInt()
			self.BCSizerShow(i,selection)
		
	def BCSizerShow(self,i,selection):
		if selection==0:
			self.bcsizers[i].Show(2,False)
			self.bcsizers[i].Show(3,False)
		elif selection==1:
			self.bcsizers[i].Show(2,True)
			self.bcsizers[i].Show(3,False)
		elif selection==2:
			self.bcsizers[i].Show(2,False)
			self.bcsizers[i].Show(3,True)
		self.bcsizers[i].Layout()
		
	def OnApply(self):
		try:
			self.Psetting,self.Bsetting=self.GetState()
			self.mapsystem.setPeriodic(self.Psetting)
			self.mapsystem.setBounded(self.Bsetting)
		except ValueError:
			raise ValueError
		
class SettingPanel(wx.lib.scrolledpanel.ScrolledPanel):
	def __init__(self,parent):
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self,parent,-1)
		
		self.pPanel=ParameterPanel(self,parent.mapsystem)
		self.bPanel=BoundaryConditionPanel(self,parent.mapsystem)
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		hsizer.Add(self.pPanel, proportion=1, flag=wx.EXPAND|wx.ALL,border=5)
		hsizer.Add(self.bPanel, proportion=1, flag=wx.EXPAND|wx.ALL,border=5)
		
		vsizer=wx.BoxSizer(wx.VERTICAL)
		vsizer.Add(hsizer, proportion=1, flag=wx.EXPAND|wx.ALL)
		
		button=wx.Button(self,wx.ID_APPLY)
		self.Bind(wx.EVT_BUTTON,self.OnApply,button)
		vsizer.Add(button, proportion=0, flag=wx.ALIGN_RIGHT)
		
		self.SetSizer(vsizer)
		
	def OnApply(self,event):
		try:
			self.pPanel.OnApply()
			self.bPanel.OnApply()
			self.GetParent().ClearPlotPanel()
		except ValueError:
			pass
