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
                
        self.q1 = None
        self.Reserve = []
        self.checkedbranchonly = False
        
        wx.xrc.XRCCTRL(self.panel,'StaticTextPreference').SetLabel('Preference: iteration=%d, p_0 = %.2f' % (self.iteration,self.initial_p))

        
        ### Event methods
        # general notebook

        def OnApply(event):
            self.Initialization()
            self.GetMset()
            self.DrawMset()
            self.plotpanel.draw()
        def OnSpinCtrlIteration(event):
            self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
        def OnTextCtrlInitial_p(event):
            self.initial_p = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlInital_p').GetValue())
        def OnDrawMset(event):
            self.GetMset()
            self.DrawMset()
            if len(self.branchsearch.branches) != 0:
                self.BranchDraw()
            self.plotpanel.draw()
        def OnCheckBoxBranchOnly(event):
            self.checkedbranchonly = event.IsChecked()
            if self.checkedbranchonly:
#                self.plotpanel.clear()
                self.BranchDraw(False)
            else:
                self.plotpanel.plot(self.mset_data[0],self.mset_data[1],',k')
                self.BranchDraw()
            self.plotpanel.draw()
        # branch data notebook

        def OnCheckListBranch(event):
            index = event.GetSelection()
            if self.checklistbranch.IsChecked(index):
                self.checkedindex.append(index)
            else:
                self.checkedindex.remove(index)
            self.checkedindex.sort()
            print self.checklistindex, self.checklistlabel, self.checkedindex
        def OnSearch(event):
            for q in self.Reserve:
                self.GetBranch(q)
        def OnGetRealBranch(event):
            if 'Branch0' not in self.checklistbranch.GetStrings():
                self.branchsearch.get_realbranch()
                self.checklistbranch.Append('Branch0')
                self.checklistlabel.append('Branch0')
                self.checklistindex.append(0)
                self.DrawMset()
                self.BranchDraw()
                self.plotpanel.draw()
            # to do if real branch exist
        def OnDeleteBranch(event):
            print self.checklistindex, self.checklistlabel
            count = 0
            index = []
            self.checkedindex.sort()
            for i in self.checkedindex:
                print i
                self.checklistbranch.Delete(i-count)
                self.checklistindex.remove(i)
                self.checklistlabel.remove('Branch%d'%i)
                count +=1
                index.append(i)
            for i in index:
                self.checkedindex.remove(i) 

            
                                    

        ### General notebook
        
        
        if wx.Platform != '__WXMAC__':
            self.Bind(wx.EVT_SPINCTRL,OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        else:
            self.Bind(wx.EVT_TEXT, OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        self.Bind(wx.EVT_TEXT_ENTER, OnTextCtrlInitial_p,  wx.xrc.XRCCTRL(self.panel, 'TextCtrlInital_p'))
        self.Bind(wx.EVT_BUTTON, OnApply, wx.xrc.XRCCTRL(self.panel, 'ButtonApply')) 
        self.Bind(wx.EVT_BUTTON, OnDrawMset, wx.xrc.XRCCTRL(self.panel,'ButtonDrawMset'))
        #self.Bind(wx.EVT_RADIOBOX, OnRadioBoxBranch, wx.xrc.XRCCTRL(self.panel,'RadioBoxBranch'))
        
        ### Branch Data notebook
        self.checklistindex = []
        self.checkedindex = []
        self.checklistlabel = []
        self.checklistbranch = wx.xrc.XRCCTRL(self.panel, 'CheckListBranch')
        self.Bind(wx.EVT_CHECKLISTBOX, OnCheckListBranch, self.checklistbranch)
        self.Bind(wx.EVT_BUTTON, OnGetRealBranch, wx.xrc.XRCCTRL(self.panel, 'ButtonGetRealBranch'))
        self.Bind(wx.EVT_CHECKBOX, OnCheckBoxBranchOnly, wx.xrc.XRCCTRL(self.panel, 'CheckBoxBranchOnly'))
      #  self.Bind(wx.EVT_BUTTON, OnSearch, wx.xrc.XRCCTRL(self.panel, 'ButtonSearch'))
        self.Bind(wx.EVT_BUTTON, OnDeleteBranch, wx.xrc.XRCCTRL(self.panel, 'ButtonDeleteBranch'))
        

        self.GetMset()
        self.DrawMset()
        self.plotpanel.draw()

    def get_mset_range(self):
        self.xi_min  = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlxi_min').GetValue())
        self.xi_max  = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlxi_max').GetValue())
        self.eta_min = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrleta_min').GetValue())
        self.eta_max = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrleta_max').GetValue())
        self.grid = int(wx.xrc.XRCCTRL(self.panel,'TextCtrlgrid').GetValue())
        self.plotpanel.xlim = (self.xi_min, self.xi_max)
        self.plotpanel.ylim = (self.eta_min, self.eta_max)
        self.plotpanel.setlim()
    def GetMset(self):
        self.get_mset_range()
        self.mset_data = self.branchsearch.get_mset(self.xi_min,self.xi_max,self.eta_min,self.eta_max,self.grid)
    def DrawMset(self):
        self.plotpanel.plot(self.mset_data[0],self.mset_data[1],',k')
        if len(self.branchsearch.branches) != 0:
            #self.branchsearch.get_realbranch()
            self.BranchDraw()
            #self.checklistbranch.Append('Branch%d' % len(self.Reserve))
            #self.checklistindex.append(0)
            #self.checklistlabel.append('Branch0')
        #print self.checklistlabel
    def OnPress(self,xy):
        q = complex(xy[0] + 1.j*xy[1])
        wx.xrc.XRCCTRL(self.panel, 'StaticTextRightBranch').SetLabel('click:%s' % (self.q1))
        self.TestBranchSearch(q, True)
        self.checklistbranch.Append('Branch%d' % len(self.Reserve))
        self.checklistlabel.append('Branch%d' % len(self.Reserve))
        self.checklistindex.append(len(self.Reserve))
    def GetBranch(self, q):
        self.branchsearch.branches = []
        self.branchsearch.search_neary_branch(q, isTest=False)
        self.BranchDraw()
    def TestBranchSearch(self, q, isTest):
        self.branchsearch.search_neary_branch(q, isTest=True)
        self.BranchDraw()
        self.plotpanel.draw()
        self.Reserve.append(numpy.array([q]))

    def BranchDraw(self, isDrawMset=True):
        self.plotpanel.clear()
        self.get_mset_range()
        if isDrawMset:
            self.plotpanel.plot(self.mset_data[0], self.mset_data[1],'k,')        
        for i in range(len(self.branchsearch.branches)):
            data = self.branchsearch.branches[i]
            self.plotpanel.axes.annotate('%d' % (i) , xy=(data[len(data)/2].real, data[len(data)/2].imag),  xycoords='data',
                                         xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
            self.plotpanel.replot(data.real, data.imag,'.', markersize=10)
    def Initialization(self):
        self.branchsearch = maps.CompPathIntegration.BranchSearch(self.map, self.initial_p, self.iteration)            
        self.q1 = None
        self.Reserve = []
        self.checkedbranchonly = False
        wx.xrc.XRCCTRL(self.panel,'StaticTextPreference').SetLabel('Preference: iteration=%d, p_0 = %.2f' % (self.iteration,self.initial_p))
        


