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
        self.checkedlsetdraw = False
        self.checkedactiondraw = False
        self.load_branch_num = 0
        ### Creating PlotPanel,
        # move plot panel to under other plot panel after last modified 
        self.msetplot = parent.GetParent().MakePlotPanel('set M')
        self.msetplot.OnPress=self.OnPress         

        ### Event methods

        def OnApply(event):
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
            try: self.lsetplot
            except AttributeError: self.lsetplot = parent.GetParent().MakePlotPanel('set L')
            self.lsetplot.clear()
            self.GetLset()
            self.DrawLset(isDrawMap=not self.checkedlsetonly)
        def OnCheckBoxLsetOnly(event):
            self.checkedlsetonly = event.IsChecked()
            self.lsetplot.clear()
            self.DrawLset(isDrawMap=not event.IsChecked())
        def OnCheckBoxQmapDraw(event):
            # todo draw wave function
            pass
        def OnQmapSet(event):
            self.get_qmap_range()
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
        def OnCheckBoxLsetDraw(event):
            self.checkedlsetdraw = event.IsChecked()
        def OnCheckBoxActionDraw(event):
            self.checkedactiondraw = event.IsChecked()
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
            print 'End Searching'
            #path = os.environ['HOME'] + '/.onsight/%s/Mset/project' % (self.mapsystem.MapName)
            #self.loadBranch(path)
        def OnLoad(event):
            if len(self.checklistindex2) != 0: self.InitializationCheckList2()
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
                file.close()
                self.LoadBranch(proj)
            dlg.Destroy()
            wx.xrc.XRCCTRL(self.panel, 'ButtonPruning').Enable(True)
        def OnCheckList2Branch(event):
            index = event.GetSelection()
            if self.checklistbranch2.IsChecked(index):
                self.checkedindex2.append(index)
            else:
                self.checkedindex2.remove(index)
            self.checkedindex2.sort()

        def OnDrawAction(event):
            try: self.actionplot
            except AttributeError: self.actionplot = parent.GetParent().MakePlotPanel('Im Action vs Re p_n') 
            self.GetAction()
            self.DrawAction()
        def OnDrawAll(event):
            self.DrawBranch(isDrawMset=not self.checkedbranchonly,marker='--', isDrawCutBranch=True)

            if self.checkedlsetdraw:
                try: self.lsetplot
                except AttributeError: self.lsetplot = parent.GetParent().MakePlotPanel('set L')
                self.GetLset()
                self.DrawLset(isDrawMap=not self.checkedlsetonly,marker=',',isDrawCutBranch=True)
            if self.checkedactiondraw:
                try: self.actionplot
                except AttributeError: self.actionplot = parent.GetParent().MakePlotPanel('Im Action vs Re p_n')
                self.GetLset()
                self.GetAction() 
                self.DrawAction(marker=':', isDrawCutBranch=True)

        def OnBranchPruning(event):
            if len(self.checklistindex1) == 0: raise ValueError
            if len(self.branchsearch.cut_branches_data) != 0: self.branchsearch.cut_branches_data =[] 
            index = range(len(self.checklistindex1))
            count = 0
            for i in index:
                if i in self.checkedindex1:
                    isChain=True
                else:
                    isChain=False
                branch = self.branchsearch.branch_data[i]
                self.branchsearch.get_pruning_branch(branch,cut_pmin=-7.0, cut_pmax=7.0, isChain=isChain)
            self.DrawBranch(isDrawMset=False,marker='--', isDrawCutBranch='ALL')
            self.InitializationCheckList2()
            self.UpdataCheckList2()
            wx.xrc.XRCCTRL(self.panel, 'ButtonDrawAll').Enable(True)
            # todo reset checkedindex1
        def OnDrawCheckedContribution(event):
            try: self.wavepanel
            except AttributeError: self.wavepanel=parent.GetParent().MakePlotPanel('Momentam Rep. of Wave Function')
            self.DrawCheckedWaveFunction()
        def OnDrawSemiclassicalWave(event):
            try: self.wavepanel
            except AttributeError: self.wavepanel=parent.GetParent().MakePlotPanel('Momentam Rep. of Wave Function')
            self.GetSemiclassicalWaveFunction()
        
        def OnSliderPruning(event):
            index_min = int(wx.xrc.XRCCTRL(self.panel, 'SliderBranchPruning_min').GetValue())
            index_max = int(wx.xrc.XRCCTRL(self.panel, 'SliderBranchPruning_max').GetValue())
            if index_max > index_min:
                self.branchsearch.hand_branch_pruning(index_min ,index_max, self.slider_pruning_index)
            else:
                self.branchsearch.hand_branch_pruning(index_max, index_min, self.slider_pruning_index)
            self.DrawBranch(isDrawMset=not self.checkedbranchonly, isDrawCutBranch='ALL')
        def OnBranchChoice(event):
            self.slider_pruning_index = self.checklistlabel2.index(str(event.GetString()))
            branch = self.branchsearch.branch_data[self.slider_pruning_index]
            cut_index = self.branchsearch.cut_index[self.slider_pruning_index]
            wx.xrc.XRCCTRL(self.panel,'SliderBranchPruning_min').SetMax(int( len(branch[0]) -1 ))
            wx.xrc.XRCCTRL(self.panel,'SliderBranchPruning_max').SetMax(int( len(branch[0]) - 1 ))
            wx.xrc.XRCCTRL(self.panel,'SliderBranchPruning_min').SetValue(cut_index.min())
            wx.xrc.XRCCTRL(self.panel,'SliderBranchPruning_max').SetValue(cut_index.max())
            self.DrawBranch(isDrawMset=not self.checkedbranchonly, isDrawCutBranch='ALL')

 
        
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
        wx.xrc.XRCCTRL(self.panel, 'ButtonDrawAll').Enable(False)
        self.Bind(wx.EVT_BUTTON, OnSearch, wx.xrc.XRCCTRL(self.panel, 'ButtonSearch'))
        self.Bind(wx.EVT_BUTTON, OnLoad , wx.xrc.XRCCTRL(self.panel, 'ButtonLoad'))
        ###
        #
        self.Bind(wx.EVT_BUTTON, OnDrawAction, wx.xrc.XRCCTRL(self.panel, 'ButtonDrawAction'))
        
        self.Bind(wx.EVT_CHECKBOX, OnCheckBoxQmapDraw, wx.xrc.XRCCTRL(self.panel, 'CheckBoxQmapDraw'))
        self.Bind(wx.EVT_BUTTON, OnQmapSet, wx.xrc.XRCCTRL(self.panel, 'ButtonQmapSet'))
        ### Branch Pruning
        self.checkedindex2 = []
        self.checklistindex2 = []
        self.checklistlabel2 = []
        self.checklistbranch2 = wx.xrc.XRCCTRL(self.panel, 'CheckListBranch2')
        self.Bind(wx.EVT_CHECKLISTBOX, OnCheckList2Branch, self.checklistbranch2)
        self.Bind(wx.EVT_BUTTON, OnBranchPruning, wx.xrc.XRCCTRL(self.panel, 'ButtonPruning'))
        wx.xrc.XRCCTRL(self.panel, 'ButtonPruning').Enable(False)
        
        ###
        self.Bind(wx.EVT_CHECKBOX, OnCheckBoxLsetDraw, wx.xrc.XRCCTRL(self.panel, 'CheckBoxLsetDraw'))
        self.Bind(wx.EVT_CHECKBOX, OnCheckBoxActionDraw, wx.xrc.XRCCTRL(self.panel, 'CheckBoxActionDraw'))
        self.Bind(wx.EVT_BUTTON, OnDrawCheckedContribution, wx.xrc.XRCCTRL(self.panel,'ButtonDrawCheckedContribution'))
        self.Bind(wx.EVT_BUTTON, OnDrawSemiclassicalWave, wx.xrc.XRCCTRL(self.panel, 'ButtonDrawSemiclassicalWave'))
        
        #
        self.Bind(wx.EVT_CHOICE, OnBranchChoice, wx.xrc.XRCCTRL(self.panel, 'ChoiceBranch'))
        self.Bind(wx.EVT_SLIDER, OnSliderPruning, wx.xrc.XRCCTRL(self.panel, 'SliderBranchPruning_min'))
        self.Bind(wx.EVT_SLIDER, OnSliderPruning, wx.xrc.XRCCTRL(self.panel, 'SliderBranchPruning_max'))
        self.branch_or_chain = 0
        self.GetMset()
        self.DrawMset()

    def OnPress(self,xy):
        if 'Branch0' not in self.checklistlabel1:
             self.GetRealBranch()
             self.branchsearch.worm_start_point.insert(0,None)
        q = complex(xy[0] + 1.j*xy[1])
        print 'Start Branch Search'
        self.GetBranch(q, isTest=True)
        print 'End Branch Search'             
        self.DrawBranch()
        
    def SearchBranch(self):
        branch_sampling = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlBranchSample').GetValue())
        branches = self.branchsearch.branches
        self.branchsearch.branches = []
        i = 0
        for q in self.branchsearch.worm_start_point:
            if q is not None:
                a = len(branches[i])/branch_sampling
                self.GetBranch(q, a=a, isTest=False)
            i+=1
        self.branchsearch.get_realbranch(branch_sampling)            
        self.branchsearch.worm_start_point = []
        # todo after branch searching 
        
    def GetBranch(self, q, wr=0.001, a=0, isTest=False):
        if isTest:
            err = self.branchsearch.search_neary_branch(q,wr=wr, isTest=True)
            if err:
                self.branchsearch.branches.pop()
                self.branchsearch.worm_start_point.pop()
            else:
                self.checklistbranch1.Append('Branch%3d' % (len(self.branchsearch.worm_start_point) - 1) )
                self.checklistlabel1.append('Branch%d' % (len(self.branchsearch.worm_start_point)-1) )
                self.checklistindex1.append((len(self.branchsearch.worm_start_point)-1))
        else:
            r = wr*a
            if r <1e-8: r = 1-e7
            self.branchsearch.get_branch(q, r=r,isTest=False)
    def GetMset(self):
        range = self.get_mset_range()
        self.mset_data = self.branchsearch.get_mset(range[0],range[1],range[2],range[3],range[4])
    def GetLset(self, isPeriodic=True):
        self.branchsearch.get_lset(isPeriodic)
    def GetClMap(self):
        range = self.get_lset_range()

        self.mapdata = self.branchsearch.get_map(self.map,range[0],range[1],range[2],range[3],sample=50, iter=100)
    def GetAction(self):
        self.branchsearch.get_action()
    def GetRealBranch(self):
        self.branchsearch.get_realbranch()
        self.checklistbranch1.Append('Branch  0')
        self.checklistlabel1.append('Branch0')
        self.checklistindex1.append(0)
    def DrawBranch(self, isDrawMset=True,marker='.',isDrawCutBranch=False):
        if isDrawCutBranch=='ALL': br_list = range(len(self.checklistindex1))
        elif isDrawCutBranch=='EACH': br_list = [self.slider_pruning_index]
        elif len(self.checkedindex1) == 0: br_list = range(len(self.branchsearch.branches))
        else: br_list = self.checkedindex1
        self.msetplot.plot()
        for i in br_list:
            data = self.branchsearch.branches[i]
            if isDrawCutBranch:
                cut_branch = self.branchsearch.cut_branches_data[i][0]
                self.msetplot.replot(cut_branch.real, cut_branch.imag, '.')
                self.msetplot.axes.annotate('%d' % (i) , xy=(cut_branch[len(cut_branch)/2].real, cut_branch[len(cut_branch)/2].imag),  xycoords='data',
                                         xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
                self.msetplot.replot(data.real, data.imag,linestyle=':',color='#AFAFAF')
            else:
                self.msetplot.replot(data.real, data.imag,marker)
                self.msetplot.axes.annotate('%d' % (i) , xy=(data[len(data)/2].real, data[len(data)/2].imag),  xycoords='data',
                                         xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
        if isDrawMset: self.msetplot.replot(self.mset_data[0], self.mset_data[1],'k,')
        self.msetplot.draw()
    def DrawMset(self):
        self.msetplot.plot(self.mset_data[0],self.mset_data[1],',k')
        if len(self.branchsearch.branches) != 0:
            self.DrawBranch()
        self.msetplot.draw()
    def DrawLset(self, isDrawMap=False,marker='.',isDrawCutBranch=False):
        self.lsetplot.plot()
        if len(self.checkedindex1) == 0: index = range(len(self.branchsearch.lset))
        else: index = self.checkedindex1
        for i in index:
            data = self.branchsearch.lset[i]
            if isDrawCutBranch:
                cut_branch = self.branchsearch.cut_branches_data[i][1]
                self.lsetplot.replot(cut_branch[0].real, cut_branch[1].real, '.')
                self.lsetplot.axes.annotate('%d' % (i) , xy=(cut_branch[0][len(cut_branch[0])/2].real, cut_branch[1][len(cut_branch[1])/2].real),  xycoords='data',
                                            xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
                self.lsetplot.replot(data[0].real, data[1].real,color='#AFAFAF',linestyle='',marker=',')
            else:
                self.lsetplot.replot(data[0].real, data[1].real,marker)
                self.lsetplot.axes.annotate('%d' % (i) , xy=(data[0][len(data[0])/2].real, data[1][len(data[1])/2].real),  xycoords='data',
                                            xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
        if isDrawMap:
            self.GetClMap()
            self.lsetplot.replot(self.mapdata[0],self.mapdata[1],color='#AFAFAF',linestyle='',marker=',')
        self.get_lset_range()
        self.lsetplot.draw()
    def DrawAction(self, marker='.',isDrawCutBranch=False):
        self.actionplot.plot()
        if len(self.checkedindex1) == 0: index = range(len(self.branchsearch.action))
        else: index = self.checkedindex1
        for i in index:
            action = self.branchsearch.action[i]
            lset = self.branchsearch.lset[i]
            if isDrawCutBranch:
                cut_action = self.branchsearch.cut_branches_data[i][2]
                cut_lsetp = self.branchsearch.cut_branches_data[i][1][1]
                self.actionplot.replot(cut_lsetp.real, cut_action.imag, '.')
                self.actionplot.axes.annotate('%d' % (i) , xy=(cut_lsetp[len(cut_lsetp)/2].real, cut_action[len(cut_action)/2].imag),  xycoords='data',
                                            xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
                self.actionplot.replot(lset[1].real, action.imag, color='#AFAFAF', linestyle='--')
            else:
                self.actionplot.replot(lset[1].real, action.imag, marker)
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
    def get_qmap_range(self):
        qmin = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlQmapQmin').GetValue())
        qmax = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlQmapQmax').GetValue())
        pmin = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlQmapPmin').GetValue())
        pmax = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlQmapPmax').GetValue())
        hdim = int(wx.xrc.XRCCTRL(self.panel, 'TextCtrlQmapHdim').GetValue())
        wx.xrc.XRCCTRL(self.panel,'StaticTextQmapSet').SetLabel('Qmap:pmin=%.2f, pmax=%.2f, hdim=%d' % (pmin, pmax, hdim))
        return qmin, qmax, pmin, pmax, hdim
    def set_semiwave_range(self):
        range = self.get_qmap_range()
        ymin = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlYlimMin').GetValue())
        ymax = float(wx.xrc.XRCCTRL(self.panel, 'TextCtrlYlimMax').GetValue())
        self.wavepanel.axes.semilogy()
        self.wavepanel.ylim = (ymin, ymax)    
        self.wavepanel.xlim = (range[2], range[3])
        self.wavepanel.setlim()
    def Initialization(self):
        self.branchsearch = maps.CompPathIntegration.BranchSearch(self.map, self.initial_p, self.iteration)
        self.branchsearch.Psetting = self.Psetting
        self.InitializationCheckList()
        self.InitializationCheckList2()
        self.GetMset()
        self.DrawMset()
        wx.xrc.XRCCTRL(self.panel,'StaticTextPreference').SetLabel('Preference: iteration=%d, p_0 = %.2f' % (self.iteration,self.initial_p))
    def DeleteCheckedBranches(self):
        count = 0
        self.checkedindex1.sort()
        self.GetLset()
        self.GetAction()
        print len(self.branchsearch.worm_start_point), len(self.branchsearch.lset), len(self.branchsearch.action)
        for i in self.checkedindex1:
            self.branchsearch.worm_start_point.pop(i-count)
            self.branchsearch.lset.pop(i-count)
            self.branchsearch.action.pop(i-count)
            self.branchsearch.branches.pop(i-count)
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
    def InitializationCheckList2(self):
        for i in range(len(self.checklistindex2)):
            self.checklistbranch2.Delete(0)
            wx.xrc.XRCCTRL(self.panel, 'ChoiceBranch').Delete(0)
        self.checklistindex2 = []
        self.checklistlabel2 = []
        self.checkedindex2   = []
    def UpdataCheckList(self):
        for i in range(len(self.branchsearch.worm_start_point)):
            self.checklistindex1.append(i)
            self.checklistlabel1.append('Branch%d' % i)
            self.checklistbranch1.Append('Branch%3d' % i)
        self.DrawBranch(True)

    def UpdataCheckList2(self):
        for i in range(len(self.branchsearch.cut_branches_data)):
            self.checklistindex2.append(i)
            self.checklistlabel2.append('Branch%d' % i)
            self.checklistbranch2.Append('Branch%3d' % i)
            wx.xrc.XRCCTRL(self.panel, 'ChoiceBranch').Append('Branch%d' % i)

    def SaveBranch(self):
        import os
        home = os.environ['HOME']
        name = self.mapsystem.MapName
        datapath = home + '/.onsight/%s/Mset/data/p0_%.1f/step%d' % (self.mapsystem.MapName, self.initial_p, self.iteration)
        if os.path.exists(datapath) == False:
            os.makedirs(datapath)
        self.branchsearch.save_branch(self.load_branch_num, datapath)
        
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
        self.load_branch_num = len(branch_list) 
        sort_nicely(branch_list)
        for branch in branch_list:
            data = numpy.loadtxt('%s' % branch ).transpose()
            self.branchsearch.branches.append(data[1] + 1.j*data[2])
            self.branchsearch.lset.append([ data[3] + 1.j*data[5], data[4] + 1.j*data[6] ] )
            self.branchsearch.action.append(data[7] + 1.j*data[8])
            branch = [ data[1]+1.j*data[2], [ data[3]+1.j*data[5], data[4]+1.j*data[6] ], data[7]+1.j*data[8] ]
            self.branchsearch.branch_data.append(branch)
            self.branchsearch.worm_start_point.append(None)

        self.UpdataCheckList()
        self.DrawBranch(not self.checkedbranchonly)
    def DrawCheckedWaveFunction(self):
        range = self.get_qmap_range()
        self.wavepanel.plot()
        p = numpy.arange(range[2], range[3], (range[3]- range[2])/range[4])
        for index in self.checkedindex2:
            branch_data = self.branchsearch.cut_branches_data[index]
            semiwave = self.branchsearch.get_semiwave(branch_data, range[0],range[1], range[2],range[3], range[4])
            abs_swave = numpy.abs(semiwave)**2/numpy.sum(numpy.abs(semiwave)**2)
            self.wavepanel.replot(p, abs_swave)
            # to do indexing of each wave fuctioin
#            ann_index1 = set(numpy.where(abs_swave < 1e-8)[0])
#            ann_index2 = set(numpy.where(abs_swave > 1e-16)[0])
#            ann_index3 = list(ann_index1.intersection(ann_index2))
#            ann_index3.sort()
#            if len(ann_index3) == 0 : ann_index = int(range[4]/2)
#            else: ann_index = int((ann_index3[len(ann_index3)-1] - ann_index3[0])/2)
#            self.wavepanel.axes.annotate('%d' % (index) , xy=(branch_data[1][1][range[4]/2].real, abs_swave[range[4]/2]),  xycoords='data',
#                                                          xytext=(-20, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->"))
        self.set_semiwave_range()
        self.wavepanel.draw()
    def GetSemiclassicalWaveFunction(self):
        branch_data = []
        branch = numpy.array([],dtype=numpy.complex128)
        lsetq  = numpy.array([],dtype=numpy.complex128)
        lsetp  = numpy.array([],dtype=numpy.complex128)
        action = numpy.array([],dtype=numpy.complex128)
        for index in self.checkedindex2:
            branch = numpy.append(branch, self.branchsearch.cut_branches_data[index][0])
            lsetq  = numpy.append(lsetq, self.branchsearch.cut_branches_data[index][1][0])
            lsetp  = numpy.append(lsetp, self.branchsearch.cut_branches_data[index][1][1])
            action = numpy.append(action, self.branchsearch.cut_branches_data[index][2])
        branch_data.append(branch)
        branch_data.append([lsetq, lsetp])
        branch_data.append(action)
        range = self.get_qmap_range()
        semiwave = self.branchsearch.get_semiwave(branch_data, range[0], range[1], range[2], range[3], range[4])
        p = numpy.arange(range[2], range[3], (range[3] - range[2])/range[4])
        abs_swave = numpy.abs(semiwave)**2/numpy.sum(numpy.abs(semiwave)**2)
        self.wavepanel.plot(p, abs_swave)
        self.set_semiwave_range()
        self.wavepanel.draw()
            

