import matplotlib
#matplotlib.use('WXAgg')
#matplotlib.use('macosx')
matplotlib.use('GTKAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wx import _load_bitmap

from matplotlib.figure import Figure

import wx
import wx.lib.scrolledpanel

class MyNavigationToolbar(NavigationToolbar2Wx):
	def __init__(self,canvas):
		NavigationToolbar2Wx.__init__(self,canvas)
		self.canvas=canvas
		
		self.AddSeparator()
		self.IdConnect=wx.NewId()
		self.AddSimpleTool(self.IdConnect, _load_bitmap('stock_refresh.xpm'),'Connect',isToggle=True)
		self._connect=False
		
		self.IdClear=wx.NewId()
		self.AddSimpleTool(self.IdClear, _load_bitmap('stock_close.xpm'),'Clear')
		
		self.Bind(wx.EVT_TOOL, self.OnConnect, id=self.IdConnect)
		self._connect=None
		self._disconnect=None
		self.Bind(wx.EVT_TOOL, self.OnClear, id=self.IdClear)
		self._clear=None
		self._getlim=None
		
		self.Bind(wx.EVT_TOOL, self.myback, id=self._NTB2_BACK)
		self.Bind(wx.EVT_TOOL, self.myforward, id=self._NTB2_FORWARD)
		self.Bind(wx.EVT_TOOL, self.myzoom, id=self._NTB2_ZOOM)
		self.Bind(wx.EVT_TOOL, self.mypan, id=self._NTB2_PAN)
		
		self.Realize()
		
	def myback(self,*args):
		NavigationToolbar2Wx.back(self,*args)
		if callable(self._getlim): self._getlim()
		
	def myforward(self,*args):
		NavigationToolbar2Wx.forward(self,*args)
		if callable(self._getlim): self._getlim()
		
	def mypan(self,*args):
		self.ToggleTool(self.IdConnect,False)
		if callable(self._disconnect): self._disconnect()
		NavigationToolbar2Wx.pan(self,*args)
		
	def myzoom(self,*args):
		self.ToggleTool(self.IdConnect,False)
		if callable(self._disconnect): self._disconnect()
		NavigationToolbar2Wx.zoom(self,*args)
		
	def OnConnect(self,event):
		self.ToggleTool(self._NTB2_PAN,False)
		self.ToggleTool(self._NTB2_ZOOM,False)
		if self._active=='PAN': NavigationToolbar2Wx.pan(self,event)
		if self._active=='ZOOM': NavigationToolbar2Wx.zoom(self,event)
		
		if self.GetToolState(self.IdConnect):
			if callable(self._connect): self._connect()
		else:
			if callable(self._disconnect): self._disconnect()
		if callable(self._getlim): self._getlim()
		
	def OnClear(self,event):
		if callable(self._clear): self._clear()
		

scales=['linear', 'log']
#~ scales=['linear', 'log', 'symlog']
_linear=0
_log=1
_symlog=2

class PlotPanel(wx.lib.scrolledpanel.ScrolledPanel):
	def __init__(self,parent):
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self,parent,-1)
		
		self.Manager=parent.Manager
		
		self.figure = Figure(figsize=(2,1.5))
		self.canvas = FigureCanvas(self, -1, self.figure)
        
		self.canvas.draw()
		
		sizer=wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1,flag=wx.SHAPED)
		self.SetSizer(sizer)
		
		#~ self.toolbar = NavigationToolbar2Wx(self.canvas)
		self.toolbar = MyNavigationToolbar(self.canvas)
		self.toolbar._connect=self.connect
		self.toolbar._disconnect=self.disconnect
		self.toolbar._clear=self.clear
		self.toolbar._getlim=self.getlim
		
		sizer.Add(self.toolbar,0,wx.ALIGN_TOP)
		
		self.OnPress=None
		
		self.isConnected=False
		
		self.xlim=(None,None)
		self.ylim=(None,None)
		
		self.xscale=_linear
		self.yscale=_linear
		
		self.canvas.mpl_connect('key_press_event',self.OnKey)
		self.canvas.mpl_connect('motion_notify_event',self.OnMove)
		
		
	def OnMove(self,event):
		try:
			statusbar=self.GetParent().statusbar
		except:
			return
		if event.inaxes is None:
			statusbar.SetStatusText("",statusbar.GetFieldsCount()-1)
		else:
			statusbar.SetStatusText(str(event.xdata)+", "+str(event.ydata),statusbar.GetFieldsCount()-1)
		
	def OnKey(self,event):
		if event.key == 'd':
			self.Dock()
		
		if event.key == 'f':
			self.Float()
		
		if event.inaxes is None: return
		
		if event.key == 'e':
			self.setlimNone()
			self.draw()
		
		if event.key == 'x':
			self.togglexscale()
			self.draw()
		
		if event.key == 'y':
			self.toggleyscale()
			self.draw()
		
	def togglexscale(self):
		self.xscale=(self.xscale+1)%len(scales)
		if hasattr(self,'axes'): self.axes.set_xscale( scales[self.xscale] )
		
	def toggleyscale(self):
		self.yscale=(self.yscale+1)%len(scales)
		if hasattr(self,'axes'): self.axes.set_yscale( scales[self.yscale] )
		
	def connect(self):
		if not self.isConnected:
			self.cid_press=self.canvas.mpl_connect('button_press_event', self.onpress)
			self.isConnected=True
		
	def disconnect(self):
		if self.isConnected:
			self.canvas.mpl_disconnect(self.cid_press)
			self.isConnected=False
		
	def draw(self):
		self.canvas.draw()
		
	def getlim(self):
		for a in self.canvas.figure.get_axes():
			self.xlim=a.get_xlim()
			self.ylim=a.get_ylim()
		
	def setlim(self):
		for a in self.canvas.figure.get_axes():
			a.set_xlim(self.xlim[0],self.xlim[1])
			a.set_ylim(self.ylim[0],self.ylim[1])
		
	def clear(self):
		if hasattr(self,'axes'): self.axes.clear()
		self.setlimNone()
		
		self.draw()
		
	def setlimNone(self):
		self.xlim=(None,None)
		self.ylim=(None,None)
		self.setlim()
		
	def plot(self,*args,**kwargs):
		self.Show()
		
		self.clear()
		self.axes=self.figure.add_subplot(111)
		self.replot(*args,**kwargs)
		
	def replot(self,*args,**kwargs):
		self.axes.plot(*args,**kwargs)
		self.setlim()
		
	def onpress(self,event):
		if event.inaxes is None:return
		if self.OnPress is not None and callable(self.OnPress):
			try:
				self.OnPress( (event.xdata,event.ydata) )
			except:
				pass
	
	def Show(self,show=True):
		self.Manager.GetPane(self).Show(show)
		self.Manager.Update()
	
	def Dock(self):
		self.Manager.GetPane(self).Dock()
		self.Manager.Update()
		
	def Float(self):
		self.Manager.GetPane(self).Float()
		self.Manager.Update()
