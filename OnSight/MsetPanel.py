import wx
import wx.xrc
import numpy
import Utils
import maps.MapSystem, maps.CompPathIntegration

from MainPanel import _SubPanel



class MsetPanel(_SubPanel):
    def __init__(self, parent, mapsystem, title):
        _SubPanel.__init__(self, parent, mapsystem, title)
        

        #### Loading XRC file and Setting the panel
        xmlresource=wx.xrc.XmlResource("OnSight/data/xrc/msetpanel.xrc")
        self.panel=xmlresource.LoadPanel(self,"msetpanel")
        
        sizer=wx.BoxSizer()
        sizer.Add(self.panel,proportion=1,flag= wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)
        
        ### Creating PlotPanel, Setting default values
        self.plotpanel = parent.GetParent().MakePlotPanel(self.title)
        
        
        self.map = self.mapsystem.map
        self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
        self.initial_p = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlInital_p').GetValue())
        self.branchsearch = maps.CompPathIntegration.BranchSearch(self.map, self.initial_p, self.iteration)            
        self.plotpanel.OnPress=self.OnPress        
        
        self.RBoxBranch = 0
        self.q1 = self.q2 = None
        self.Reserve = []
        
        wx.xrc.XRCCTRL(self.panel,'StaticTextPreference').SetLabel('Preference: iteration=%d p_0 = %.2f' % (self.iteration,self.initial_p))
        ###
        
        
        
        def OnSpinCtrlIteration(event):
            self.iteration = event.GetInt()
            print event.GetInt() # for debug
        def OnTextCtrlInital_p(event):
            self.initial_p = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlInital_p').GetValue())
            print self.initial_p # for debug
        def OnDrawMset(event):
            self.get_mset_range()
            data = self.branchsearch.get_mset(self.xi_min, self.xi_max, self.eta_min, self.eta_max, self.grid)      
            self.plotpanel.plot(data[0], data[1],',k')
            self.plotpanel.draw()
        def OnRadioBoxBranch(event):
            self.RBoxBranch = event.GetSelection()
        def OnTestSearch(event):
            if self.q1 != None and self.q2 != None:
                self.ReservationBranch(self.q1, self.q2)
            else:
                raise ValueError, 'q1=%s, q2=%s' % (self.q1, self.q2)
            
        if wx.Platform != '__WXMAC__':
            self.Bind(wx.EVT_SPINCTRL,OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        else:
           self.Bind(wx.EVT_TEXT, OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        self.Bind(wx.EVT_TEXT,OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        self.Bind(wx.EVT_TEXT_ENTER, OnTextCtrlInital_p,  wx.xrc.XRCCTRL(self.panel, 'TextCtrlInital_p'))
        self.Bind(wx.EVT_BUTTON, OnDrawMset, wx.xrc.XRCCTRL(self.panel,'DrawMset'))
        self.Bind(wx.EVT_RADIOBOX, OnRadioBoxBranch, wx.xrc.XRCCTRL(self.panel,'RadioBoxBranch'))
        self.Bind(wx.EVT_BUTTON, OnTestSearch , wx.xrc.XRCCTRL(self.panel, 'ButtonTestSearch'))


#                wx.xrc.XRCCTRL(self.panel,'TextCtrlRemain').SetValue(str(len(self.mapsystem.Remain)))


        self.get_mset_range()
        self.DrawMset()


    def get_mset_range(self):
        self.xi_min  = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlxi_min').GetValue())
        self.xi_max  = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlxi_max').GetValue())
        self.eta_min = float(wx.xrc.XRCCTRL(self.panel,'TextCtrleta_min').GetValue())
        self.eta_max = float(wx.xrc.XRCCTRL(self.panel,'TextCtrleta_max').GetValue())
        self.grid = int(wx.xrc.XRCCTRL(self.panel,'TextCtrlgrid').GetValue())
        self.plotpanel.xlim = (self.xi_min, self.xi_max)
        self.plotpanel.ylim = (self.eta_min, self.eta_max)
        self.plotpanel.setlim()
    def DrawMset(self):
        self.mset_data = self.branchsearch.get_mset(self.xi_min,self.xi_max,self.eta_min,self.eta_max,self.grid)
        self.plotpanel.plot(self.mset_data[0],self.mset_data[1],',k')
        self.plotpanel.draw()
        #print maps.CompPathIntegration.Mset.test(self.mapsystem.map)
    def OnPress(self,xy):
        
        if self.RBoxBranch == 0:
            self.q1 = complex(xy[0] + 1.j*xy[1])
            wx.xrc.XRCCTRL(self.panel, 'StaticTextRightBranch').SetLabel(':%.3f+i%.3f' % (self.q1.real, self.q1.imag))
        else:
            self.q2 = complex(xy[0] + 1.j*xy[1])
            wx.xrc.XRCCTRL(self.panel, 'StaticTextLeftBranch').SetLabel(':%.3f+i%.3f' % (self.q2.real, self.q2.imag))
    def ReservationBranch(self, q1, q2):
        section = self.branchsearch.bisection(q1, q2, self.initial_p, self.iteration)
        self.plotpanel.replot(section.real, section.imag,'o', markersize=10)
        self.plotpanel.draw()
        self.Reserve.append(numpy.array([q1, q2]))