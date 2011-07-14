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
        
        ### Setting default values
        self.map = self.mapsystem.map
        self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
        self.initial_p = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlInital_p').GetValue())
        self.branchsearch = maps.CompPathIntegration.BranchSearch(self.map, self.initial_p, self.iteration)            
        wx.xrc.XRCCTRL(self.panel,'StaticTextPreference').SetLabel('Preference: iteration=%d, p_0 = %.2f' % (self.iteration,self.initial_p))
        self.q1 = None
        self.Reserve = []

        ### Creating Mset PlotPanel,
        # move plot panel to under other plot panel after last modified 
        self.msetplot = parent.GetParent().MakePlotPanel(self.title)
        self.msetplot.OnPress=self.OnPress         
    
        ### Creating Lset Plot Panel
        self.lsetplot = parent.GetParent().MakePlotPanel(self.title)

        ### Event methods
# general notebook
        def OnApply(event):
            self.Initialization()
            self.GetMset()
            self.DrawMset()
            self.msetplot.draw()
        def OnSpinCtrlIteration(event):
            self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
        def OnTextCtrlInitial_p(event):
            self.initial_p = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlInital_p').GetValue())
        def OnDrawMset(event):
            self.GetMset()
            self.DrawMset()
            if len(self.branchsearch.branches) != 0:
                self.BranchDraw()
            self.msetplot.draw()
        def OnCheckBoxBranchOnly(event):
            if event.IsChecked():
                self.msetplot.clear()
                self.BranchDraw(isDrawMset=False)
            else:
 
                self.BranchDraw(isDrawMset=True)
            self.msetplot.draw()
# branch data notebook
        def OnDrawLset(event):
            self.GetLset()
            #self.DrawLset()
        def OnCheckBoxLsetOnly(event):
            print event.IsChecked()

        def OnCheckListBranch(event):
            index = event.GetSelection()
            if self.checklistbranch.IsChecked(index):
                self.checkedindex.append(index)
            else:
                self.checkedindex.remove(index)
            self.checkedindex.sort()
        def OnSearch(event):
            self.Reserve.pop(0)
            for q in self.Reserve:
                self.GetBranch(q)
        def OnGetRealBranch(event):
            if 'Branch0' not in self.checklistbranch.GetStrings():
                self.GetRealBranch()
                self.DrawMset()
                self.BranchDraw()
                self.msetplot.draw()
        def OnDeleteBranch(event):
            if 0 in self.checkedindex: raise TypeError, "Branch0 can't delete"
            if len(self.checkedindex) != 0:
                self.DeleteCheckedBranches()
            

        ### General notebook
        
        if wx.Platform != '__WXMAC__':
            self.Bind(wx.EVT_SPINCTRL,OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        else:
            self.Bind(wx.EVT_TEXT, OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        self.Bind(wx.EVT_TEXT_ENTER, OnTextCtrlInitial_p,  wx.xrc.XRCCTRL(self.panel, 'TextCtrlInital_p'))
        self.Bind(wx.EVT_BUTTON, OnApply, wx.xrc.XRCCTRL(self.panel, 'ButtonApply')) 
        self.Bind(wx.EVT_BUTTON, OnDrawMset, wx.xrc.XRCCTRL(self.panel,'ButtonDrawMset'))
        self.Bind(wx.EVT_CHECKBOX, OnCheckBoxBranchOnly, wx.xrc.XRCCTRL(self.panel, 'CheckBoxBranchOnly'))
        self.Bind(wx.EVT_BUTTON, OnDrawLset, wx.xrc.XRCCTRL(self.panel,'ButtonDrawLset'))
        self.Bind(wx.EVT_CHECKBOX, OnCheckBoxLsetOnly,   wx.xrc.XRCCTRL(self.panel, 'CheckBoxLsetOnly'))
        
        ### Branch Data notebook
        self.checklistindex = []
        self.checkedindex = []
        self.checklistlabel = []
        self.checklistbranch = wx.xrc.XRCCTRL(self.panel, 'CheckListBranch')
        self.Bind(wx.EVT_CHECKLISTBOX, OnCheckListBranch, self.checklistbranch)
        self.Bind(wx.EVT_BUTTON, OnGetRealBranch, wx.xrc.XRCCTRL(self.panel, 'ButtonGetRealBranch'))
        self.Bind(wx.EVT_BUTTON, OnSearch, wx.xrc.XRCCTRL(self.panel, 'ButtonSearch'))
        self.Bind(wx.EVT_BUTTON, OnDeleteBranch, wx.xrc.XRCCTRL(self.panel, 'ButtonDeleteBranch'))
        

        self.GetMset()
        self.DrawMset()
        self.msetplot.draw()

    def get_mset_range(self):
        xmin  = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlxi_min').GetValue())
        xmax  = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlxi_max').GetValue())
        ymin = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrleta_min').GetValue())
        ymax = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrleta_max').GetValue())
        grid = int(wx.xrc.XRCCTRL(self.panel,'TextCtrlgrid').GetValue())
        self.msetplot.xlim = (xmin, xmax)
        self.msetplot.ylim = (ymin,ymax)
        self.msetplot.setlim()
        return xmin, xmax, ymin, ymax,grid
    def get_lset_range(self):
        xmin = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrl_Lsetxmin').GetValue())
        xmax = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrl_Lsetxmax').GetValue())
        ymin = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrl_Lsetymin').GetValue())
        ymax = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrl_Lsetymax').GetValue())
        self.lsetplot.xlim = (xmin, xmax)
        self.lsetplot.ylim = (ymin, ymax)
        self.msetplot.setlim()
        print xmin,xmax, ymin,ymax
    def GetMset(self):
        range = self.get_mset_range()
        self.mset_data = self.branchsearch.get_mset(range[0],range[1],range[2],range[3],range[4])
    def GetLset(self):
        self.get_lset_range()
    def GetRealBranch(self):
        self.branchsearch.get_realbranch()
        self.checklistbranch.Append('Branch0')
        self.checklistlabel.append('Branch0')
        self.checklistindex.append(0)
        self.Reserve.append(numpy.array([]))
    def DrawMset(self):
        self.msetplot.plot(self.mset_data[0],self.mset_data[1],',k')
        if len(self.branchsearch.branches) != 0:
            self.BranchDraw()
    def OnPress(self,xy):
        if 'Branch0' not in self.checklistlabel: self.GetRealBranch()
        q = complex(xy[0] + 1.j*xy[1])
        wx.xrc.XRCCTRL(self.panel, 'StaticTextRightBranch').SetLabel('click:%s' % (q))
        self.GetBranch(q, isTest=True)
        self.checklistbranch.Append('Branch%d' % (len(self.Reserve)-1))
        self.checklistlabel.append('Branch%d' % (len(self.Reserve)-1))
        self.checklistindex.append((len(self.Reserve)-1))
    def GetBranch(self, q, isTest=False):
        if isTest:
            self.branchsearch.search_neary_branch(q, isTest=True)
            self.Reserve.append(numpy.array([q]))
        else:
            self.branchsearch.branches = []
            self.branchsearch.search_neary_branch(q, isTest=False)
        self.BranchDraw()
        self.msetplot.draw()

    def BranchDraw(self, isDrawMset=True):
        if isDrawMset: self.msetplot.plot(self.mset_data[0], self.mset_data[1],'k,')
        for i in range(len(self.branchsearch.branches)):
            data = self.branchsearch.branches[i]
            self.msetplot.axes.annotate('%d' % (i) , xy=(data[len(data)/2].real, data[len(data)/2].imag),  xycoords='data',
                                         xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
            self.msetplot.replot(data.real, data.imag,'.', markersize=10)
    def Initialization(self):
        self.branchsearch = maps.CompPathIntegration.BranchSearch(self.map, self.initial_p, self.iteration)            
        self.q1 = None
        self.Reserve = []
        self.InitializationCheckList()
        wx.xrc.XRCCTRL(self.panel,'StaticTextPreference').SetLabel('Preference: iteration=%d, p_0 = %.2f' % (self.iteration,self.initial_p))
    def DeleteCheckedBranches(self):
        count = 0
        self.checkedindex.sort()
        for i in self.checkedindex:
            self.Reserve.pop(i - count)
            self.branchsearch.branches.pop(i-count)
            count +=1
        self.InitializationCheckList()
        self.UpdataCheckList()
    def InitializationCheckList(self):
        for i in range(len(self.checklistindex)):
            self.checklistbranch.Delete(0)
        self.checklistindex = []
        self.checklistlabel = []
        self.checkedindex = []
    def UpdataCheckList(self):
        for i in range(len(self.Reserve)):
            self.checklistindex.append(i)
            self.checklistlabel.append('Branch%d' % i)
            self.checklistbranch.Append('Branch%d' % i)
        self.BranchDraw(True)
        self.msetplot.draw()

