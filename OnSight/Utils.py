import wx
import string

import wx.html
import os

import wx.wizard
import maps.MapSystem

class NumericValidator(wx.PyValidator):
	def __init__(self):
		wx.PyValidator.__init__(self)
		def OnChar(event):
			key = event.GetKeyCode()
			if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
				event.Skip()
				return
			
			if chr(key) in string.digits+'.'+'-':
				event.Skip()
				return
			return
		
		self.Bind(wx.EVT_CHAR, OnChar)
		
	def Clone(self):
		return NumericValidator()

class NumericTextCtrl(wx.TextCtrl):
	def __init__(self,parent,**kwargs):
		wx.TextCtrl.__init__(self,parent,**kwargs)
		self.value=0.0
		def OnText(event=None):
			if self.GetValue()=='':
				self.value=0.0
				return
			try:
				self.value=float( self.GetValue() )
			except ValueError:
				wx.TextCtrl.SetValue(str(self.value))
		OnText()
		parent.Bind(wx.EVT_TEXT, OnText, self)
		self.SetValidator(NumericValidator())
		
	def SetValue(self, value):
		wx.TextCtrl.SetValue(self,value)
		try:
			self.value=float( value )
		except ValueError:
			self.value=0.0

def _putTextCtrlFlexGrid(window,sizer,inputarray,style_st=0,proportion_st=0,flag_st=0,style_tc=0,proportion_tc=0,flag_tc=0):
	
	fgsizer=wx.FlexGridSizer(len(inputarray),len(inputarray[0]))
	
	tclist=[]
	
	for input in inputarray:
		list=[]
		for inp in input:
			if type(inp)==str:
				obj=wx.StaticText(window,label=inp,style=style_st)
				fgsizer.Add(obj,proportion_st,flag_st)
			else:
				obj=NumericTextCtrl(window,value=str(inp),style=style_tc)
				fgsizer.Add(obj,proportion_tc,flag_tc)
				list.append(obj)
		tclist.append(list)
	
	sizer.Add(fgsizer,1,wx.ALL)
	
	return tclist

class Description(wx.Panel):
	nodescription = """<html><body>
	<h2>No Description Page Found</h2>
	
	<p>Unable to open html page for a given map.
	
	</body></html>
	"""
	def __init__(self,parent):
		wx.Panel.__init__(self,parent,-1)
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		
		self.back=wx.Button(self,-1,"Back")
		self.Bind(wx.EVT_BUTTON, self.OnBack, self.back)
		hsizer.Add(self.back,1,wx.GROW|wx.ALL)
		
		self.forward=wx.Button(self,-1,"Forward")
		self.Bind(wx.EVT_BUTTON, self.OnForward, self.forward)
		hsizer.Add(self.forward,1,wx.GROW|wx.ALL)
		
		sizer=wx.BoxSizer(wx.VERTICAL)
		sizer.Add(hsizer,0,wx.GROW)
		
		self.htmlwindow=wx.html.HtmlWindow(self,-1)
		sizer.Add(self.htmlwindow,1,wx.EXPAND)
		
		self.SetSizer(sizer)
		
		
	def LoadDescription(self,MapName):
		self.LoadPage('description/'+MapName)
		
	def LoadInfo(self,MapName):
		self.LoadPage('info/'+MapName)
		
	def LoadPage(self,path):
		filename = os.path.join(os.getcwd(), 'OnSight/data/html/'+path+'.html')
		if os.path.exists(filename) and os.path.isfile(filename):
			self.htmlwindow.LoadPage(filename)
		else:
			self.htmlwindow.SetPage(self.nodescription)
		
	def updateButton(self):
		self.back.Enable(self.htmlwindow.HistoryCanBack())
		self.forward.Enable(self.htmlwindow.HistoryCanForward())
		
	def OnBack(self,event):
		if not self.htmlwindow.HistoryBack():
			wx.MessageBox("No more items in history!")
		self.updateButton()
		
	def OnForward(self,event):
		if not self.htmlwindow.HistoryForward():
			wx.MessageBox("No more items in history!")
		self.updateButton()


classification={
	'1D Maps':{
		'':['Quadra'],
		'Bernoulli':{
			'':['Bernoulli2','BernoulliK']
		},
		'Intermittent':{
			'':['PomeauManneville','ModifiedBernoulli','ModifiedBernoulliAsym']
		}
	},
	'2D Maps':{
		'':['BakerMap','HenonMap','IkedaMap'],
		'SymplecticMap':{
			'':['HarperMap','PiecewiseLinearHarper','SharpenHarper'],
			'Standard Map':{
				'':['StandardMap','PiecewiseLinearStandard','SharpenStandard','TruncatedStandard','QuadraticStandard','NQuadraticStandard','ShudoStandard']
			},
			'Kepler Map':{
				'':['KeplerMap','KeplerGeneral']
			}
		}
	},
	'4D Maps':{
		'SymplecticMap':{
			'':['FroeschleMap']
		}
	}
}

class MapWizard(wx.wizard.Wizard):
	defaultmap='StandardMap'
	def __init__(self,parent):
		wx.wizard.Wizard.__init__(self,parent)
		self.mapsystem=None
		
		self.page1=wx.wizard.WizardPageSimple(self)
		
		treectrl=wx.TreeCtrl(self.page1,-1)
		root=treectrl.AddRoot('Maps')
		def AddItem(tree,node,book):
			for key,item in book.items():
				if key=='':
					for i in item:
						tree.AppendItem(node,i)
				else:
					branch=tree.AppendItem(node,key)
					AddItem(tree,branch,item)
		
		AddItem(treectrl,root,classification)
		treectrl.Expand(root)
		treectrl.SortChildren(root)
		
		if wx.Platform != '__WXMAC__':
			child=treectrl.GetFirstChild(root)[0]
			treectrl.SortChildren(child)
			for n in range(treectrl.GetChildrenCount(root,recursively=False)-1):
				child=treectrl.GetNextVisible(child)
				treectrl.SortChildren(child)
			
			treectrl.Expand(treectrl.GetNextVisible(treectrl.GetFirstChild(root)[0]))
		
		def OnSelect(event):
			itemid=event.GetItem()
			if itemid and not treectrl.ItemHasChildren(itemid):
				MapName=treectrl.GetItemText(itemid)
				self.textctrl.SetValue(MapName)
				self.description.LoadInfo(MapName)
		
		self.page1.Bind(wx.EVT_TREE_SEL_CHANGED, OnSelect, treectrl)
		
		MapName=self.defaultmap
		
		self.description=Description(self.page1)
		self.description.LoadInfo(MapName)
		
		self.textctrl=wx.TextCtrl(self.page1,-1,MapName,style=wx.TE_READONLY)
		#~ self.checkbox=wx.CheckBox(self.page1,-1,'Complex: ',style=wx.ALIGN_RIGHT)
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		hsizer.Add(self.textctrl,1,wx.EXPAND | wx.ALL,border=5)
		#~ hsizer.Add(self.checkbox,1,wx.EXPAND,border=5)
		sizer=wx.BoxSizer(wx.VERTICAL)
		sizer.Add(treectrl,1,wx.EXPAND | wx.ALL,border=5)
		sizer.Add(hsizer,0,wx.EXPAND | wx.ALL,border=5)
		
		s=wx.BoxSizer(wx.HORIZONTAL)
		s.Add(sizer,1,wx.EXPAND | wx.ALL,border=5)
		s.Add(self.description,2,wx.EXPAND | wx.ALL,border=5)
		
		self.page1.SetSizer(s)
		
		# Contents of page2 will be created when it appears on Wizard, namely when the method OnPageChanging is called
		self.page2=wx.wizard.WizardPageSimple(self)
		
		self.SetPageSize(wx.Size(720,480))
		
		self.FitToPage(self.page1)
		wx.wizard.WizardPageSimple_Chain(self.page1, self.page2)
		self.GetPageAreaSizer().Add(self.page1)
		
		self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING,self.OnPageChanging)
		self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED,self.OnPageChanged)
		
	def StartWizard(self):
		return self.RunWizard(self.page1)
		
	def OnPageChanging(self,event):
		if event.GetDirection():
			if event.GetPage()==self.page1:
				# Creating the contents of page2
				
				MapName=self.textctrl.GetValue()
				self.validMapName=hasattr(maps.MapSystem,MapName)
				if self.validMapName:
					self.mapsystem=maps.MapSystem.MapSystem(eval('maps.MapSystem.'+MapName)(isComplex=False))
					#~ self.mapsystem=maps.MapSystem.MapSystem(eval('maps.MapSystem.'+MapName)(isComplex=self.checkbox.IsChecked()))
					
					from SettingPanel import ParameterPanel,BoundaryConditionPanel
					
					self.parameterpanel=ParameterPanel(self.page2,self.mapsystem)
					self.boundaryconditionpanel=BoundaryConditionPanel(self.page2,self.mapsystem)
					sizer=wx.BoxSizer(wx.VERTICAL)
					sizer.Add(self.parameterpanel,1,wx.EXPAND|wx.ALL)
					sizer.Add(self.boundaryconditionpanel,1,wx.EXPAND|wx.ALL)
					self.page2.SetSizer(sizer)
				
			elif event.GetPage()==self.page2:
				# Applying the parameters and boundary conditions before page1 and page2 are destroyed.
				# Note that at the moment of finishing wizard, namely when wx.wizard.EVT_WIZARD_FINISHED raised, 
				# page1 and page2 are already destroyed, so that OnApply should be called here.
				try:
					self.parameterpanel.OnApply()
					self.boundaryconditionpanel.OnApply()
				except ValueError:
					pass
			
		else:
			self.page2.DestroyChildren()
			
	def OnPageChanged(self,event):
		if event.GetPage()==self.page2:
			if not self.validMapName:
				self.ShowPage(self.page1,goingForward=False)

labels={
	'Quadra':{'Axis':[r'z'],'Parameter':[r'c']},
	'Bernoulli2':{'Axis':[r'x'],'Parameter':[r'p']},
	'BernoulliK':{'Axis':[r'x']},
	'PomeauManneville':{'Axis':[r'x'],'Parameter':[r'p',r'b']},
	'ModifiedBernoulli':{'Axis':[r'x'],'Parameter':[r'p',r'b']},
	'ModifiedBernoulliAsym':{'Axis':[r'x'],'Parameter':[r'p',r'b_0',r'b_1']},
	'StandardMap':{'Axis':[r'q',r'p'],'Parameter':[r'k']},
	'PiecewiseLinearStandard':{'Axis':[r'q',r'p'],'Parameter':[r'k']},
	'SharpenStandard':{'Axis':[r'q',r'p'],'Parameter':[r'k',r'e']},
	'TruncatedStandard':{'Axis':[r'q',r'p'],'Parameter':[r'k',r'n']},
	'QuadraticStandard':{'Axis':[r'q',r'p'],'Parameter':[r'k']},
	'NQuadraticStandard':{'Axis':[r'q',r'p'],'Parameter':[r'k',r'n']},
	'ShudoStandard':{'Axis':[r'q',r'p'],'Parameter':[r'k',r'p_d',r'\omega',r'\nu']},
	'KeplerMap':{'Axis':[r'\phai',r'E'],'Parameter':[r'k',r'a']},
	'KeplerGeneral':{'Axis':[r'\phai',r'E'],'Parameter':[r'k',r'a',r'p']},
	'HarperMap':{'Axis':[r'q',r'p'],'Parameter':[r'k']},
	'PiecewiseLinearHarper':{'Axis':[r'q',r'p'],'Parameter':[r'k']},
	'SharpenHarper':{'Axis':[r'q',r'p'],'Parameter':[r'k',r'e']},
	'BakerMap':{'Axis':[r'x',r'y']},
	'HenonMap':{'Axis':[r'x',r'y'],'Parameter':[r'a',r'b']},
	'IkedaMap':{'Axis':[r'x',r'y'],'Parameter':[r'R',r'C_1',r'C_2',r'C_3']},
	'FroeschleMap':{'Axis':[r'q_1',r'p_1',r'q_2',r'p_2'],'Parameter':[r'k_1',r'k_2',r'l']}
	}

def getAxisLabel(mapsystem):
	try:
		axis=labels[mapsystem.MapName]['Axis']
		if len(axis)<mapsystem.map.Para.num:
			#TODO 
			pass
	except KeyError:
		axis=[]
		for i in range(1,mapsystem.dim+1):
			axis.append(r'x_'+str(i))
	return axis

def getParameterLabel(mapsystem):
	try:
		parameter=labels[mapsystem.MapName]['Parameter']
	except KeyError:
		parameter=[]
		for i in range(1,mapsystem.Para.num+1):
			parameter.append(r'p_'+str(i))
	return parameter
	
def getLabel(mapsystem):
	return getAxisLabel(mapsystem),getParameterLabel(mapsystem)


class FigureDialog(wx.Dialog):
	def __init__(self,parent,**kwargs):
		wx.Dialog.__init__(self,parent,**kwargs)
		
		import PlotPanel
		self.canvas,self.figure=PlotPanel.createCanvasFigure(self)
		
		self.axes=self.figure.gca()
		
		self.canvas.draw()
		
		sizer=wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1,flag=wx.SHAPED)
		
		btnsizer=wx.StdDialogButtonSizer()
		btnsizer.AddButton(wx.Button(self, wx.ID_OK))
		btnsizer.AddButton(wx.Button(self, wx.ID_CANCEL))
		btnsizer.Realize()
		
		sizer.Add(btnsizer, 0)
		
		self.SetSizer(sizer)
		

class RegionDialog(FigureDialog):
	def __init__(self,parent,type,**kwargs):
		FigureDialog.__init__(self,parent,**kwargs)
		
		self.type=type
		
		import tools.PatchDrawer
		
		if self.type == 0:
			self.rectangle=tools.PatchDrawer.RectangleDrawer(self.axes)
		if self.type == 1:
			self.box=tools.PatchDrawer.BoxDrawer(self.axes)
		if self.type == 2:
			self.circle=tools.PatchDrawer.CircleDrawer(self.axes)
		
		self.CenterOnScreen()
		
	def GetValues(self):
		if self.type == 0:
			xmin=min(self.rectangle.xy[0],self.rectangle.xy[0]+self.rectangle.width)
			xmax=max(self.rectangle.xy[0],self.rectangle.xy[0]+self.rectangle.width)
			
			ymin=min(self.rectangle.xy[1],self.rectangle.xy[1]+self.rectangle.height)
			ymax=max(self.rectangle.xy[1],self.rectangle.xy[1]+self.rectangle.height)
			return (xmin, xmax, ymin, ymax)
		if self.type == 1:
			return (self.box,xy[0], self.box.xy[1], self.box.edge)
		if self.type == 2:
			return (self.circle.xy[0], self.circle.xy[1], self.circle.radius)
