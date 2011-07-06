import matplotlib.patches


class PatchDrawer(object):
	def __init__(self,axes):
		self.axes=axes
		self.canvas=axes.figure.canvas
		
		self.patch=None
		
		self.isConnected=False
		self.connect()
		
	def connect(self):
		if self.isConnected: return
		self.isConnected=True
		self.cid_press=self.canvas.mpl_connect('button_press_event', self.onpress)
		self.cid_release=self.canvas.mpl_connect('button_release_event', self.onrelease)
		self.cid_move=self.canvas.mpl_connect('motion_notify_event', self.onmove)
		
	def __del__(self):
		self.patch.set_visible(False)
		
	def disconnect(self):
		if not self.isConnected: return
		self.isConnected=False
		self.canvas.mpl_disconnect(self.cid_press)
		self.canvas.mpl_disconnect(self.cid_release)
		self.canvas.mpl_disconnect(self.cid_move)
		
	def set_visible(self,visible):
		self.patch.set_visible(visible)
		self.canvas.draw()
		
	def onpress(self,event):
		pass
		
	def onrelease(self,event):
		pass
		
	def onmove(self,event):
		pass
	#TODO: 

class RectangleDrawer(PatchDrawer):
	xy=(0.0,0.0)
	width=0.0
	height=0.0
	def __init__(self,axes):
		PatchDrawer.__init__(self,axes)
		self.patch=matplotlib.patches.Rectangle(self.xy,self.width,self.height,visible=False)
		self.axes.add_patch(self.patch)
		
		self.rectangle=self.patch
		
		self.dragged=False
		
	def onpress(self,event):
		if event.inaxes is None:
			self.dragged=False
			return
		self.dragged=True
		
		self.rectangle.set_visible(True)
		
		self.xy=(event.xdata,event.ydata)
		
	def onmove(self,event):
		if not self.dragged or event.inaxes is None: return
		
		self.width=event.xdata-self.xy[0]
		self.height=event.ydata-self.xy[1]
		
		self.drawrectangle()
		
	def onrelease(self,event):
		self.dragged=False
		if event.inaxes is None: return
		
		self.width=event.xdata-self.xy[0]
		self.height=event.ydata-self.xy[1]
		
		self.drawrectangle()
		
	def drawrectangle(self):
		self.rectangle.set_xy(self.xy)
		self.rectangle.set_width(self.width)
		self.rectangle.set_height(self.height)
		
		self.canvas.draw()
		
class BoxDrawer(RectangleDrawer):
	center=(0.0,0.0)
	def __init__(self,axes):
		RectangleDrawer.__init__(self,axes)
		
	def onpress(self,event):
		if event.inaxes is None:
			self.dragged=False
			return
		self.dragged=True
		
		self.rectangle.set_visible(True)
		
		self.xy=(event.xdata,event.ydata)
		self.center=self.xy
		
	def onmove(self,event):
		if not self.dragged or event.inaxes is None: return
		
		edge=max(abs(self.center[0]-event.xdata),abs(self.center[1]-event.ydata))
		self.width=2*edge
		self.height=2*edge
		
		self.xy=(self.center[0]-edge,self.center[1]-edge)
		
		self.drawrectangle()
		
	def onrelease(self,event):
		self.dragged=False
		if event.inaxes is None: return
		
		edge=max(abs(self.center[0]-event.xdata),abs(self.center[1]-event.ydata))
		self.width=2*edge
		self.height=2*edge
		
		self.xy=(self.center[0]-edge,self.center[1]-edge)
		
		self.drawrectangle()

class CircleDrawer(PatchDrawer):
	xy=(0.0,0.0)
	radius=0.0
	def __init__(self,axes):
		PatchDrawer.__init__(self,axes)
		self.circle=matplotlib.patches.Circle(self.xy,radius=self.radius,visible=False)
		self.axes.add_patch(self.circle)
		
		self.dragged=False
		
	def drawcircle(self):
		self.circle.set_radius(self.radius)
		
		self.canvas.draw()
		
	def onpress(self,event):
		if event.inaxes is None:
			self.dragged=False
			return
		self.dragged=True
		self.xy=(event.xdata,event.ydata)
		
		if self.circle in self.axes.patches:
			self.axes.patches.remove(self.circle)
		del self.circle
		self.circle=matplotlib.patches.Circle(self.xy,radius=self.radius,visible=False)
		self.circle.set_visible(True)
		self.axes.add_patch(self.circle)
		
	def onmove(self,event):
		if not self.dragged or event.inaxes is None: return
		
		self.radius=( (event.xdata-self.xy[0])**2.0 + (event.ydata-self.xy[1])**2.0 )**0.5
		
		self.drawcircle()
		
	def onrelease(self,event):
		self.dragged=False
		if event.inaxes is None: return
		
		self.radius=( (event.xdata-self.xy[0])**2.0 + (event.ydata-self.xy[1])**2.0 )**0.5
		
		self.drawcircle()
