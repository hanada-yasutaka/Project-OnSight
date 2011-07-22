import wx
import wx.xrc
import numpy
import Utils
import maps.MapSystem, maps.CompPathIntegration

from MainPanel import _SubPanel

def sort_nicely( l ): 
    import re 
    """ Sort the given list in the way that humans expect. 
    """ 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    l.sort( key=alphanum_key ) 


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

        self.mapdata = [] 
        self.checkedbranchonly = False
        self.checkedlsetonly = True
        ### Creating PlotPanel,
        # move plot panel to under other plot panel after last modified 
        self.msetplot = parent.GetParent().MakePlotPanel('set M')
        self.msetplot.OnPress=self.OnPress         
        self.lsetplot = parent.GetParent().MakePlotPanel('set L')
        self.actionplot = parent.GetParent().MakePlotPanel('Im Action vs Re p_n')
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
            self.GetMset()
            self.DrawBranch(isDrawMset=not self.checkedbranchonly)
        def OnCheckBoxBranchOnly(event):
            self.checkedbranchonly = event.IsChecked()
            self.msetplot.clear()
            self.DrawBranch(isDrawMset=not event.IsChecked())
        def OnDrawLset(event):
            self.lsetplot.clear()
            self.DrawLset(isDrawMap=not self.checkedlsetonly)
        def OnCheckBoxLsetOnly(event):
            self.checkedlsetonly = event.IsChecked()
            self.lsetplot.clear()
            self.DrawLset(isDrawMap=not event.IsChecked())
        def OnCheckListBranch(event):
            index = event.GetSelection()
            if self.checklistbranch1.IsChecked(index):
                self.checkedindex1.append(index)
            else:
                self.checkedindex1.remove(index)
            self.checkedindex1.sort()
        def OnDeleteBranch(event):
            if 0 in self.checkedindex1: raise TypeError, "Branch0 can't delete"

            if len(self.checkedindex1) != 0:
                self.DeleteCheckedBranches()
        # branch data
        def OnSearch(event):
            if len(self.checklistindex1) == 0: raise ValueError, 'Branch was not searched'
            dlg = wx.MessageDialog(self, 'Branch Search tasks a long time.\nSo, Each Branch data are saved in your home directory.\nAre you OK?',
                                   'Warning',
                                   wx.OK | wx.CANCEL | wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.SearchBranch()
                self.SaveBranch()

        def OnLoad(event):
            import os
            home = os.environ['HOME']
            projpath = home + '/.onsight/%s/Mset/project' % (self.mapsystem.MapName)
            dlg = wx.FileDialog(self, message='Choose a .mset file',
                                    defaultDir=projpath, defaultFile="",
                                    wildcard='.mset',
                                    style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
            if dlg.ShowModal() == wx.ID_OK:
                path=str(dlg.GetPaths()[0])
                file = open('%s' % path, 'r')
                proj = []
                for line in file:
                    proj.append(line)
                self.LoadBranch(proj)
            dlg.Destroy()
        def OnCheckList2Branch(event):
            index = event.GetSelection()
            if self.checklistbranch2.IsChecked(index):
                self.checkedindex2.append(index)
            else:
                self.checkedindex2.remove(index)
            self.checkedindex2.sort()
            print self.checkedindex2
        def OnDrawAction(event):
            self.GetAction()
            self.DrawAction()
        def OnDrawAll(event):
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
        self.checklistindex1 = []
        self.checkedindex1 = []
        self.checklistlabel1 = []
        self.checklistbranch1 = wx.xrc.XRCCTRL(self.panel, 'CheckListBranch1')
        self.Bind(wx.EVT_CHECKLISTBOX, OnCheckListBranch, self.checklistbranch1)
        self.Bind(wx.EVT_BUTTON, OnDeleteBranch, wx.xrc.XRCCTRL(self.panel, 'ButtonDeleteBranch'))
        self.Bind(wx.EVT_BUTTON, OnDrawAll, wx.xrc.XRCCTRL(self.panel, 'ButtonDrawAll'))
        self.Bind(wx.EVT_BUTTON, OnSearch, wx.xrc.XRCCTRL(self.panel, 'ButtonSearch'))
        self.Bind(wx.EVT_BUTTON, OnLoad , wx.xrc.XRCCTRL(self.panel, 'ButtonLoad'))
        ###
        #
        self.Bind(wx.EVT_BUTTON, OnDrawAction, wx.xrc.XRCCTRL(self.panel, 'ButtonDrawAction'))
        ### Branch Pruning
        self.checkedindex2 = []
        self.checklistindex2 = []
        self.checklistlabel2 = []
        self.checklistbranch2 = wx.xrc.XRCCTRL(self.panel, 'CheckListBranch2')
        self.Bind(wx.EVT_CHECKLISTBOX, OnCheckList2Branch, self.checklistbranch2)
        
        
        self.GetMset()
        self.DrawMset()
        self.msetplot.draw()
        self.lsetplot.draw()
        self.actionplot.draw()

    def OnPress(self,xy):
        if 'Branch0' not in self.checklistlabel1: self.GetRealBranch()
        q = complex(xy[0] + 1.j*xy[1])
        self.GetBranch(q, isTest=True)
        self.DrawBranch()
        self.checklistbranch1.Append('Branch%3d' % (len(self.branchsearch.branches)-1))
        self.checklistlabel1.append('Branch%d' % (len(self.branchsearch.branches)-1))
        self.checklistindex1.append((len(self.branchsearch.branches)-1))
        self.GetLset()
        self.DrawLset()
        self.GetAction()
        self.DrawAction()
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
        self.branchsearch.get_action()
    def GetRealBranch(self):
        self.branchsearch.get_realbranch()
        self.checklistbranch1.Append('Branch  0')
       # self.checklistbranch2.Append('Branch0')
        self.checklistlabel1.append('Branch0')
        self.checklistindex1.append(0)
    def DrawBranch(self, isDrawMset=True):
        if len(self.checkedindex1) == 0: br_list = range(len(self.branchsearch.branches))
        else: br_list = self.checkedindex1
        self.msetplot.plot()
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
        if len(self.checkedindex1) == 0: index = range(len(self.branchsearch.lset))
        else: index = self.checkedindex1
        for i in index:
            data = self.branchsearch.lset[i]
            self.lsetplot.replot(data[0].real, data[1].real,'.')
            self.lsetplot.axes.annotate('%d' % (i) , xy=(data[0][len(data[0])/2].real, data[1][len(data[1])/2].real),  xycoords='data',
                                            xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
        if isDrawMap:
            self.GetClMap()
            self.lsetplot.replot(self.mapdata[0],self.mapdata[1],color='#AFAFAF',linestyle='',marker=',')
        self.get_lset_range()
        self.lsetplot.draw()
    def DrawAction(self):
        self.actionplot.plot()
        if len(self.checkedindex1) == 0: index = range(len(self.branchsearch.action))
        else: index = self.checkedindex1
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
        self.InitializationCheckList()
        self.lsetplot.clear()
        self.msetplot.clear()
        self.GetMset()
        self.DrawMset()
        wx.xrc.XRCCTRL(self.panel,'StaticTextPreference').SetLabel('Preference: iteration=%d, p_0 = %.2f' % (self.iteration,self.initial_p))
    def DeleteCheckedBranches(self):
        count = 0
        self.checkedindex1.sort()
        for i in self.checkedindex1:
            self.branchsearch.worm_start_point.pop(i-count - 1)
            self.branchsearch.lset.pop(i-count)
            self.branchsearch.action.pop(i-count)
            self.branchsearch.branches.pop(i-count)
            # to do after implimentation of Get Action
            # self.branchsearch.action.pop(i-count)
            count +=1
        self.checkedindex1 = []
        self.InitializationCheckList()
        self.UpdataCheckList()
    def InitializationCheckList(self):
        for i in range(len(self.checklistindex1)):
            self.checklistbranch1.Delete(0)
        self.checklistindex1 = []
        self.checklistlabel1 = []
        self.checkedindex1 = []
    def UpdataCheckList(self):
        for i in range(len(self.branchsearch.branches)):
            self.checklistindex1.append(i)
            self.checklistlabel1.append('Branch%d' % i)
            self.checklistbranch1.Append('Branch%3d' % i)
            #self.checklistbranch2.Append('Branch%d' % i)
        self.DrawBranch(True)
        self.DrawLset()
        self.DrawAction()

    def UpdataCheckList2(self):
        for i in range(len(self.branchsearch.branches)):
            self.checklistindex2.append(i)
            self.checklistlable1.append('Branch%d' % i)
            self.checklistbranch2.Append('Branch%3d', i)
 
    def SaveBranch(self):
        import os
        home = os.environ['HOME']
        name = self.mapsystem.MapName
        datapath = home + '/.onsight/%s/Mset/data/p0_%.1f/step%d' % (self.mapsystem.MapName, self.initial_p, self.iteration)
        if os.path.exists(datapath) == False:
            os.makedirs(datapath)
        self.branchsearch.save_branch(datapath)
        
        projpath = home + '/.onsight/%s/Mset/project' % (self.mapsystem.MapName)
        if os.path.exists(projpath) == False:
            os.makedirs(projpath)
        name = 'iter%dp0_%.1f.mset' % (self.iteration, self.initial_p)
        file = open("%s/%s" % (projpath, name), 'w')
        file.write('%d\n%.1f\n' % (self.iteration,self.initial_p))
        file.write('%s' % datapath)
        file.close()
    def LoadBranch(self, proj):
        import glob
        self.iteration = int(proj[0])
        self.initial_p = float(proj[1])        
        wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').SetValue(self.iteration)
        wx.xrc.XRCCTRL(self.panel,'TextCtrlInitial_p').SetValue(proj[1])
        datapath = proj[2] + '/Branch*.dat'
        
        self.Initialization()
        branch_list = glob.glob(datapath)
        sort_nicely(branch_list)
        for branch in branch_list:
            data = numpy.loadtxt('%s' % branch ).transpose()
            self.branchsearch.branches.append(data[1] + 1.j*data[2])
            self.branchsearch.lset.append([ data[3] + 1.j*data[5], data[4] + 1.j*data[6] ] )
            self.branchsearch.action.append(data[7] + 1.j*data[8])
        self.UpdataCheckList()
        
        self.DrawBranch(not self.checkedbranchonly)
        self.DrawLset(not self.checkedlsetonly)
        self.DrawAction()

