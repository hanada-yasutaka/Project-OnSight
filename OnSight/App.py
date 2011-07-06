import os, sys

import wx
import wx.aui
import wx.lib.scrolledpanel

ID_MENU_FILE_CLOSEALL = wx.NewId()
ID_MENU_WINDOW_FULLSCREEN = wx.NewId()
ID_MENU_WINDOW_NEXT = wx.NewId()
ID_MENU_WINDOW_PREVIOUS = wx.NewId()

FileWildCard="OnSight data file (*.ost)|*.ost|All files (*.*)|*.*"

import MainPanel
import SettingPanel
import PlotPanel

import Utils

import maps.MapSystem

#---------------------------------------------------------------------------
class _SubFrame(wx.aui.AuiMDIChildFrame):
	def __init__(self,parent,title=None):
		self.SaveFile=None
		self.isSaved=False
		
		wx.aui.AuiMDIChildFrame.__init__(self,parent,-1,title=title,style=wx.DEFAULT_FRAME_STYLE)
		self.ParentClientWindow=parent.ClientWindow
		
		self.Manager=wx.aui.AuiManager()
		self.Manager.SetManagedWindow(self)
		
		self.isActive=True
		self.Manager.Update()
		self.PerspectiveCurrent=self.Manager.SavePerspective()
		
		self.Bind(wx.EVT_CLOSE, parent.OnClose)
		self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
		
	def OnActivate(self,event):
		for i in range( self.ParentClientWindow.GetPageCount() ):
			#NOTE: 	this exception handling avoids an error which occurs when a new page is created and activated.
			#		A newly-created SubFrame, at the moment of creation, is regarded as AuiMDIChildFrame, which has no HideAllPanes method.
			try:
				self.ParentClientWindow.GetPage(i).HideAllPanes()
			except:
				pass
		
		self.isActive=True
		self.LoadPerspective()
		
	def SavePerspective(self):
		self.PerspectiveCurrent=self.Manager.SavePerspective()
		
	def LoadPerspective(self):
		self.Manager.LoadPerspective(self.PerspectiveCurrent)
		self.Manager.Update()
		
	def HideAllPanes(self):
		if self.isActive:
			self.SavePerspective()
			self.isActive=False
		for pane in self.Manager.GetAllPanes():
			pane.Hide()
		self.Manager.Update()

#---------------------------------------------------------------------------
class SubFrame(_SubFrame):
	def __init__(self,parent,mapsystem):
		self.mapsystem=mapsystem
		self.MapName=self.mapsystem.map.__class__.__name__
		
		self.statusbar=parent.GetStatusBar()
		
		_SubFrame.__init__(self,parent,title=self.MapName)
		
		self.plotpanels=[]
		self.mainpanel=MainPanel.MainPanel(self)
		self.Manager.AddPane(self.mainpanel, wx.aui.AuiPaneInfo().Name("MainPanel").CenterPane())
		
		self.parameterpanel=SettingPanel.SettingPanel(self)
		self.Manager.AddPane(self.parameterpanel, wx.aui.AuiPaneInfo().Name("SettingPanel").Caption("Settings").Top().Layer(0).Floatable(False).CloseButton(False).BestSize(wx.Size(480,160)).MinSize(wx.Size(400,100)) )
		
		
		self.Manager.Update()
		self.PerspectiveCurrent=self.Manager.SavePerspective()
		
		menubar=parent.CreateBaseMenuBar()
		for (menu,label) in menubar.GetMenus():
			if label=='Window':
				menu.AppendSeparator()
				item=menu.Append(-1,'Plot Panel Viewer')
				self.Bind(wx.EVT_MENU,self.OnPlotPanelViewer,item)
		
		menu=self.mainpanel.CreateMenuMain()
		menubar.Insert(1,menu,"Functions")
		
		self.SetMenuBar(menubar)
		
	def OnPlotPanelViewer(self,event):
		panes=[]
		captions=[]
		showns=[]
		dockeds=[]
		for pane in self.Manager.GetAllPanes():
			if pane.name=='Viewer': return
			if pane.name.find('PlotPanel')==0: # choose panes whose name starts with 'PlotPanel'.
				panes.append(pane)
				captions.append(pane.caption)
				showns.append(pane.IsShown())
				dockeds.append(pane.IsDocked())
		
		if len(captions)>0:
			panel=wx.Panel(self,-1)
			sizer=wx.BoxSizer(wx.VERTICAL)
			sizer.Add(wx.StaticText(panel,-1,'Plot Panel'),0,wx.EXPAND|wx.ALL)
			checklistbox=wx.CheckListBox(panel, -1, (80, 50), choices=captions)
			sizer.Add(checklistbox,1,wx.EXPAND|wx.ALL)
			panel.SetSizer(sizer)
			for i,shown in enumerate(showns): checklistbox.Check(i,shown)
			
			def OnCheck(event):
				i=event.GetSelection()
				if checklistbox.IsChecked(i): panes[i].Show()
				else: panes[i].Hide()
				self.Manager.Update()
			panel.Bind(wx.EVT_CHECKLISTBOX,OnCheck,checklistbox)
			
			
			self.Manager.AddPane(panel,wx.aui.AuiPaneInfo().Name('Viewer').Caption('Plot Panel Viewer').Float().Dockable(False).DestroyOnClose(True).FloatingPosition(wx.Point(100, 100)).BestSize(wx.Size(320,240)) )
			self.Manager.Update()
		
	def MakePlotPanel(self,caption):
		plotpanel=PlotPanel.PlotPanel(self)
		name="PlotPanel"+str(plotpanel.GetId()) # AuiPaneInfo's name cannot be duplicated. Appending a unique number, plotpanel's ID. 
		PaneInfo=wx.aui.AuiPaneInfo().Name(name).Caption(caption).Dock().Layer(5).FloatingPosition(wx.Point(100, 100)).CloseButton(True).PinButton(True).MinimizeButton(True).MaximizeButton(True).BestSize(wx.Size(360,360)).MinSize(wx.Size(160,160)).TopDockable(False).BottomDockable(False).RightDockable(False)
		self.Manager.AddPane(plotpanel, PaneInfo )
		
		self.Manager.Update()
		
		self.plotpanels.append(plotpanel)
		return plotpanel
		
	def ClearPlotPanel(self):
		for plotpanel in self.plotpanels:
			plotpanel.clear()
			plotpanel.draw()


#---------------------------------------------------------------------------

class MainFrame(wx.aui.AuiMDIParentFrame):
	def __init__(self, parent, title):
		wx.aui.AuiMDIParentFrame.__init__(self, parent, -1, title, size = (1080, 720),style=wx.DEFAULT_FRAME_STYLE)
		self.SetMinSize((640,480))
		
		# this works only in MSW
		#self.Tile(wx.VERTICAL)
		
		# Change tab look-and-feel
		art=wx.aui.AuiSimpleTabArt().Clone()
		#art=wx.aui.PyAuiTabArt().Clone()
		self.SetArtProvider(art)
		
		menubar=self.CreateBaseMenuBar()
		self.SetMenuBar(menubar)
		
		self.UpdateBaseMenu()
		
		self.CreateStatusBar(3)
		
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		
		self.ClientWindow=self.GetClientWindow()
		
		#### debug 
		#~ mapsystem=maps.MapSystem.MapSystem(maps.MapSystem.StandardMap(2.0))
		mapsystem=maps.MapSystem.MapSystem(maps.MapSystem.PiecewiseLinearStandard(2.0))
		mapsystem.setPeriodic([(True,1.0),(True,1.0)])
		frame=self.CreateSubFrame(mapsystem)
		frame.Show()
		self.UpdateBaseMenu()
		#### debug 
		
	def CreateBaseMenuBar(self):
		menubar=wx.MenuBar()
		
		# Create file menu
		menuFile=wx.Menu()
		menuFile.AppendItem(wx.MenuItem(menuFile,wx.ID_NEW))
		menuFile.AppendSeparator()
		menuFile.AppendItem(wx.MenuItem(menuFile,wx.ID_OPEN))
		menuFile.AppendItem(wx.MenuItem(menuFile,wx.ID_SAVE))
		menuFile.AppendItem(wx.MenuItem(menuFile,wx.ID_SAVEAS))
		menuFile.AppendSeparator()
		menuFile.AppendItem(wx.MenuItem(menuFile,wx.ID_CLOSE))
		menuFile.Append(ID_MENU_FILE_CLOSEALL,"Close All\tShift-Ctrl-W")
		menuFile.AppendSeparator()
		menuFile.AppendItem(wx.MenuItem(menuFile,wx.ID_PREFERENCES))
		menuFile.AppendSeparator()
		menuFile.AppendItem(wx.MenuItem(menuFile,wx.ID_EXIT))
		
		self.Bind(wx.EVT_MENU, self.OnNew, id=wx.ID_NEW)
		self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
		self.Bind(wx.EVT_MENU, self.OnSave, id=wx.ID_SAVE)
		self.Bind(wx.EVT_MENU, self.OnSaveAs, id=wx.ID_SAVEAS)
		self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_CLOSE)
		self.Bind(wx.EVT_MENU, self.OnCloseAll, id=ID_MENU_FILE_CLOSEALL)
		self.Bind(wx.EVT_MENU, self.OnPreferences, id=wx.ID_PREFERENCES)
		self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
		
		file=wx.MenuItem(menuFile,wx.ID_EXIT)
		type(file)
		menubar.Append(menuFile,"File")
		
		# Remove default window menu
		self.SetWindowMenu(None)
		
		# Create window menu
		menuWindow=wx.Menu()
		menuWindow.Append(ID_MENU_WINDOW_FULLSCREEN,"Full Screen\tAlt-F")
		menuWindow.AppendSeparator()
		menuWindow.Append(ID_MENU_WINDOW_NEXT,"Next Window\tCtrl-PgDn")
		menuWindow.Append(ID_MENU_WINDOW_PREVIOUS,"Previous Window\tCtrl-PgUp")
		
		self.Bind(wx.EVT_MENU,self.OnFullScreen,id=ID_MENU_WINDOW_FULLSCREEN)
		self.Bind(wx.EVT_MENU,self.OnNextWindow,id=ID_MENU_WINDOW_NEXT)
		self.Bind(wx.EVT_MENU,self.OnPreviousWindow,id=ID_MENU_WINDOW_PREVIOUS)

		menubar.Append(menuWindow,"Window")
		
		# Create help menu
		menuHelp=wx.Menu()
		menuHelp.AppendItem(wx.MenuItem(menuFile,wx.ID_ABOUT))
		self.Bind(wx.EVT_MENU,self.OnAbout,id=wx.ID_ABOUT)
		
		menubar.Append(menuHelp,"Help")
		
		return menubar


	def UpdateBaseMenu(self):
		HasChild=(self.GetActiveChild()!=None)
		
		menubar=self.GetMenuBar()
		menubar.Enable(wx.ID_SAVE,HasChild)
		menubar.Enable(wx.ID_SAVEAS,HasChild)
		menubar.Enable(wx.ID_CLOSE,HasChild)
		menubar.Enable(ID_MENU_FILE_CLOSEALL,HasChild)
		
		#TODO next/previous window menu should be disable when child is single
		menubar.Enable(ID_MENU_WINDOW_NEXT,HasChild)
		menubar.Enable(ID_MENU_WINDOW_PREVIOUS,HasChild)

	def CreateSubFrame(self,mapsystem):
		return SubFrame(self,mapsystem)

	def OnNew(self,event):
		mapwizard=Utils.MapWizard(self)
		
		if mapwizard.StartWizard():
			frame=self.CreateSubFrame(mapwizard.mapsystem)
			frame.Show()
			self.UpdateBaseMenu()
		
	def OnOpen(self,event):
		dlg=wx.FileDialog(self, message="Open file ..", defaultDir=os.getcwd(),defaultFile="",wildcard=FileWildCard,style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
		if dlg.ShowModal()==wx.ID_OK:
			LoadFile=dlg.GetPath()
			#TODO exception handling
			mapsystem=maps.MapSystem.MapSystem(maps.MapSystem.PiecewiseLinearStandard(2.0))
			frame=self.CreateSubFrame(mapsystem)
			frame.SaveFile=LoadFile
			frame.Show()
			self.UpdateBaseMenu()
		dlg.Destroy()
		
	def OnSave(self,event):
		child=self.GetActiveChild()
		if not child==None:
			if child.SaveFile==None:
				if not self.SetSaveFile(child): return False
			
			try:
				#TODO save settings and data to file
				return True
			except:
				pass
				#TODO make message telling save failure
			return False
		
		return True
		
	def SetSaveFile(self,child):
		dlg=wx.FileDialog(self, message="Save file as ..", defaultDir=os.getcwd(),defaultFile="",wildcard=FileWildCard,style=wx.SAVE)
		savefileset=(dlg.ShowModal()==wx.ID_OK)
		if savefileset: child.SaveFile=dlg.GetPath()
		
		#TODO append extension if not given
		
		dlg.Destroy()
		return savefileset

	def OnSaveAs(self,event):
		child=self.GetActiveChild()
		if not child==None:
			child.SaveFilePath=None
			self.OnSave(event)
		
	def OnClose(self,event):
		child=self.GetActiveChild()
		closed=True
		if not child==None:
			#### debug 
			#~ dlg=wx.MessageDialog(self, 'Do you want to save before leave?','',wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
			#~ result=dlg.ShowModal()
			#~ dlg.Destroy()
			result=wx.ID_NO
			#### debug 
			
			if result==wx.ID_YES:
				if self.OnSave(event):
					child.Destroy()
					self.UpdateBaseMenu()
					closed=True
				else:
					closed=False
			elif result==wx.ID_NO:
				child.Destroy()
				self.UpdateBaseMenu()
				closed=True
			elif result==wx.ID_CANCEL: closed=False
		
		return closed
	
	def OnCloseAll(self,event):
		closed=True
		while not self.GetActiveChild()==None:
			closed=self.OnClose(event)
			if not closed: break
		self.UpdateBaseMenu()
		return closed

	def OnPreferences(self,event):
		#TODO create preferences dialog
		pass
	
	def OnExit(self,event):
		closed=self.OnCloseAll(event)
		if closed: self.Destroy()
		
	def OnFullScreen(self,event):
		self.ToggleFullScreen()
	
	def OnNextWindow(self,event):
		self.ActivateNext()

	def OnPreviousWindow(self,event):
		self.ActivatePrevious()
	def OnAbout(self,event):
		info=wx.AboutDialogInfo()
		info.SetName("OnSight")
		info.SetDevelopers(["A. Akaishi", "Y. Hanada"])
		#TODO complete description
		info.SetDescription("-dynamical systems-")
		info.SetVersion("0.01")
		
		wx.AboutBox(info)
		
	def ToggleFullScreen(self):
		self.ShowFullScreen(not self.IsFullScreen())

#---------------------------------------------------------------------------

class MainApp(wx.App):
	def OnInit(self):
		
		#TODO create splash window here
		#TODO create dialog to confirm packages and its version
		
		self.SetAppName("onsight")
		frame=MainFrame(None, "OnSight")
		frame.Show()
		
		return True

#---------------------------------------------------------------------------

