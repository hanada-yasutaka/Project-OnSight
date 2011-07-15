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
        self.Psetting = self.map.Psetting
        self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
        self.initial_p = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlInitial_p').GetValue())
        self.branchsearch = maps.CompPathIntegration.BranchSearch(self.map, self.initial_p, self.iteration)            
        wx.xrc.XRCCTRL(self.panel,'StaticTextPreference').SetLabel('Preference: iteration=%d, p_0 = %.2f' % (self.iteration,self.initial_p))

        self.Reserve = []
        self.mapdata = [] 
        self.checkedbranchonly = False
        self.checkedlsetonly = True
        ### Creating PlotPanel,
        # move plot panel to under other plot panel after last modified 
        self.msetplot = parent.GetParent().MakePlotPanel('set M')
        self.msetplot.OnPress=self.OnPress         
        self.lsetplot = parent.GetParent().MakePlotPanel('set L')

        ### Event methods
# general notebook
        def OnApply(event):
            # to do dialogue
            self.Initialization()
            self.GetMset()
            self.DrawMset()      
        def OnSpinCtrlIteration(event):
            self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
        def OnTextCtrlInitial_p(event):
            self.initial_p = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlInitial_p').GetValue())
        def OnDrawMset(event):
            self.msetplot.clear()
            self.DrawBranch(isDrawMset=not self.checkedbranchonly)
        def OnCheckBoxBranchOnly(event):
            self.checkedbranchonly = event.IsChecked()
            self.msetplot.clear()
            self.DrawBranch(isDrawMset=not event.IsChecked())
        def OnDrawLset(event):
            self.GetLset()
            self.DrawLset()
        def OnCheckBoxLsetOnly(event):
            self.checkedlsetonly = event.IsChecked()
            self.lsetplot.clear()
            self.DrawLset(isDrawMap=not event.IsChecked())
        def OnCheckListBranch(event):
            index = event.GetSelection()
            if self.checklistbranch1.IsChecked(index):
                self.checkedindex.append(index)
            else:
                self.checkedindex.remove(index)
            self.checkedindex.sort()
        def OnDeleteBranch(event):
            if 0 in self.checkedindex: raise TypeError, "Branch0 can't delete"
            if len(self.checkedindex) != 0:
                self.DeleteCheckedBranches()
        def OnSearch(event):
            # to do dialogue
            try: self.actionplot
            except AttributeError: self.actionplot = parent.GetParent().MakePlotPanel('Im Action vs Re p_n')
            self.SearchBranch()
            for branch in self.branchsearch.branches:
                print len(branch)
            self.DrawBranch(isDrawMset=False)
            self.DrawLset()
            self.DrawAction()
            print 'End Searching'
        ## Branch pruning
        def OnCheckList2Branch(event):
            index = event.GetSelection()
            if self.checklistbranch2.IsChecked(index):
                self.checkedindex2.append(index)
            else:
                self.checkedindex2.remove(index)
            self.checkedindex2.sort()
            print self.checkedindex2
        def OnDrawAction(event):
            try: self.actionplot
            except AttributeError: self.actionplot = parent.GetParent().MakePlotPanel('Im Action vs Re p_n')
            self.GetAction()
            self.DrawAction()
        def OnDrawAll(event):
            try: self.actionplot
            except AttributeError: self.actionplot = parent.GetParent().MakePlotPanel('Im Action vs Re p_n')
            self.DrawBranch(isDrawMset=not self.checkedbranchonly)
            self.DrawLset(isDrawMap = not self.checkedlsetonly)
            self.GetAction()
            self.DrawAction()
            
        if wx.Platform != '__WXMAC__':
            self.Bind(wx.EVT_SPINCTRL,OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        else:
            self.Bind(wx.EVT_TEXT, OnSpinCtrlIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        self.Bind(wx.EVT_TEXT_ENTER, OnTextCtrlInitial_p,  wx.xrc.XRCCTRL(self.panel, 'TextCtrlInitial_p'))
        self.Bind(wx.EVT_BUTTON, OnApply, wx.xrc.XRCCTRL(self.panel, 'ButtonApply')) 
        self.Bind(wx.EVT_BUTTON, OnDrawMset, wx.xrc.XRCCTRL(self.panel,'ButtonDrawMset'))
        self.Bind(wx.EVT_CHECKBOX, OnCheckBoxBranchOnly, wx.xrc.XRCCTRL(self.panel, 'CheckBoxBranchOnly'))
        self.Bind(wx.EVT_BUTTON, OnDrawLset, wx.xrc.XRCCTRL(self.panel,'ButtonDrawLset'))
        self.Bind(wx.EVT_CHECKBOX, OnCheckBoxLsetOnly,   wx.xrc.XRCCTRL(self.panel, 'CheckBoxLsetOnly'))
        ###
        self.checklistindex = []
        self.checkedindex = []
        self.checklistlabel = []
        self.checklistbranch1 = wx.xrc.XRCCTRL(self.panel, 'CheckListBranch1')
        self.Bind(wx.EVT_CHECKLISTBOX, OnCheckListBranch, self.checklistbranch1)
        self.Bind(wx.EVT_BUTTON, OnDeleteBranch, wx.xrc.XRCCTRL(self.panel, 'ButtonDeleteBranch'))
        self.Bind(wx.EVT_BUTTON, OnDrawAll, wx.xrc.XRCCTRL(self.panel, 'ButtonDrawAll'))
        self.Bind(wx.EVT_BUTTON, OnSearch, wx.xrc.XRCCTRL(self.panel, 'ButtonSearch'))
        ###
        #
        self.Bind(wx.EVT_BUTTON, OnDrawAction, wx.xrc.XRCCTRL(self.panel, 'ButtonDrawAction'))
        ### Branch Pruning
        self.checkedindex2 = []
        self.checklistbranch2 = wx.xrc.XRCCTRL(self.panel, 'CheckListBranch2')
        self.Bind(wx.EVT_CHECKLISTBOX, OnCheckList2Branch, self.checklistbranch2)
        
        
        self.GetMset()
        self.DrawMset()
        self.msetplot.draw()
        self.lsetplot.draw()

    def OnPress(self,xy):
        if 'Branch0' not in self.checklistlabel: self.GetRealBranch()
        q = complex(xy[0] + 1.j*xy[1])
        self.GetBranch(q, isTest=True)
        self.DrawBranch()
        self.checklistbranch1.Append('Branch%d' % (len(self.Reserve)-1))
        self.checklistbranch2.Append('Branch%d' % (len(self.Reserve)-1))
        self.checklistlabel.append('Branch%d' % (len(self.Reserve)-1))
        self.checklistindex.append((len(self.Reserve)-1))
        self.GetLset()
        self.DrawLset()
    def SearchBranch(self):
        branch_sampling = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlBranchSample').GetValue())
        branches = self.branchsearch.branches
        self.branchsearch.branches = []
        i = 1
        for q in self.branchsearch.worm_start_point:
            a = len(branches[i])/branch_sampling
            self.GetBranch(q, a=a, isTest=False)
            i+=1
        self.branchsearch.get_realbranch(branch_sampling)            
        self.branchsearch.worm_start_point = []
    def GetBranch(self, q, wr=0.005, a=0, isTest=False):
        if isTest:
            self.branchsearch.search_neary_branch(q,wr=wr, isTest=True)
            self.Reserve.append(numpy.array([q]))
        else:
            self.branchsearch.get_branch(q, r=a*wr,isTest=False)
    def GetMset(self):
        range = self.get_mset_range()
        self.mset_data = self.branchsearch.get_mset(range[0],range[1],range[2],range[3],range[4])
    def GetLset(self, isPeriodic=True):
        range = self.get_lset_range()
        self.branchsearch.get_lset(isPeriodic)
    def GetClMap(self):
        range = self.get_lset_range()
        self.mapdata = self.branchsearch.get_map(range[0],range[1],range[2],range[3],sample=50, iter=100)
    def GetAction(self):
#        self.branchsearch.action=[]
        self.branchsearch.get_action()
    def GetRealBranch(self):
        self.branchsearch.get_realbranch()
        self.checklistbranch1.Append('Branch0')
        self.checklistbranch2.Append('Branch0')
        self.checklistlabel.append('Branch0')
        self.checklistindex.append(0)
        self.Reserve.append(numpy.array([]))
    def DrawBranch(self, isDrawMset=True):
        if len(self.checkedindex) == 0: br_list= range(len(self.branchsearch.branches))
        else: br_list = self.checkedindex
        self.msetplot.plot()
        #for i in range(len(self.branchsearch.branches)):
        for i in br_list:
            data = self.branchsearch.branches[i]
            self.msetplot.replot(data.real, data.imag,'.')
            self.msetplot.axes.annotate('%d' % (i) , xy=(data[len(data)/2].real, data[len(data)/2].imag),  xycoords='data',
                                         xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
        if isDrawMset: self.msetplot.replot(self.mset_data[0], self.mset_data[1],'k,')
        self.msetplot.draw()
    def DrawMset(self):
        self.msetplot.plot(self.mset_data[0],self.mset_data[1],',k')
        if len(self.branchsearch.branches) != 0:
            self.DrawBranch()
        self.msetplot.draw()
    def DrawLset(self, isDrawMap=False):
        self.lsetplot.plot()
        if len(self.checkedindex) == 0: index = range(len(self.branchsearch.lset))
        else: index = self.checkedindex
        for i in index:
            data = self.branchsearch.lset[i]
            self.lsetplot.replot(data[0].real, data[1].real,'.')
            self.lsetplot.axes.annotate('%d' % (i) , xy=(data[0][len(data)/2].real, data[1][len(data)/2].real),  xycoords='data',
                                            xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
        if isDrawMap:
            self.GetClMap()
            self.lsetplot.replot(self.mapdata[0],self.mapdata[1],color='#AFAFAF',linestyle='',marker=',')
        self.get_lset_range()
        self.lsetplot.draw()
    def DrawAction(self):
        self.actionplot.plot()
        if len(self.checkedindex) == 0: index = range(len(self.branchsearch.action))
        else: index = self.checkedindex
        for i in index:
            action = self.branchsearch.action[i]
            lset = self.branchsearch.lset[i]
            self.actionplot.replot(lset[1].real, action.imag, '.')
            self.actionplot.axes.annotate('%d' % (i) , xy=(lset[1][len(lset[1])/2].real, action[len(action)/2].imag),  xycoords='data',
                                          xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
        self.get_action_range()
        self.actionplot.draw()
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
        self.lsetplot.setlim()
        return xmin, xmax, ymin, ymax
    def get_action_range(self):
        xmin = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlActxmin').GetValue())
        xmax = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlActxmax').GetValue())
        ymin = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlActymin').GetValue())
        ymax = float(wx.xrc.XRCCTRL(self.panel,'TextCtrlActymax').GetValue())
        self.actionplot.xlim = (xmin, xmax)
        self.actionplot.ylim = (ymin, ymax)
        self.actionplot.setlim()
        return xmin, xmax, ymin, ymax
    def Initialization(self):
        self.branchsearch = maps.CompPathIntegration.BranchSearch(self.map, self.initial_p, self.iteration)
        self.branchsearch.Psetting = self.Psetting
        self.Reserve = []
        self.InitializationCheckList()
        wx.xrc.XRCCTRL(self.panel,'StaticTextPreference').SetLabel('Preference: iteration=%d, p_0 = %.2f' % (self.iteration,self.initial_p))
    def DeleteCheckedBranches(self):
        count = 0
        self.checkedindex.sort()
        for i in self.checkedindex:
            self.Reserve.pop(i - count)
            self.branchsearch.worm_start_point.pop(i-count - 1)
            self.branchsearch.lset.pop(i-count)
            self.branchsearch.branches.pop(i-count)
            # to do after implimentation of Get Action
            # self.branchsearch.action.pop(i-count)
            count +=1
        self.InitializationCheckList()
        self.UpdataCheckList()
    def InitializationCheckList(self):
        for i in range(len(self.checklistindex)):
            self.checklistbranch1.Delete(0)
            self.checklistbranch2.Delete(0)
        self.lsetplot.clear()
        self.checklistindex = []
        self.checklistlabel = []
        self.checkedindex = []
    def UpdataCheckList(self):
        for i in range(len(self.Reserve)):
            self.checklistindex.append(i)
            self.checklistlabel.append('Branch%d' % i)
            self.checklistbranch1.Append('Branch%d' % i)
            self.checklistbranch2.Append('Branch%d' % i)
        self.DrawBranch(True)
        
        self.DrawLset()
        self.lsetplot.draw()

