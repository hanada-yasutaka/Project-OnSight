import wx
import wx.xrc
import numpy
import Utils
import maps.MapSystem, maps.QuantumMap

from MainPanel import _SubPanel

class QuantumPanel(_SubPanel):
    def __init__(self, parent, mapsystem, title):
        _SubPanel.__init__(self, parent, mapsystem, title)

        xmlresource=wx.xrc.XmlResource("OnSight/data/xrc/quantumpanel.xrc")
        self.panel=xmlresource.LoadPanel(self,"quantumpanel")

        sizer=wx.BoxSizer()
        sizer.Add(self.panel,proportion=1,flag= wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)
        
        self.map = self.mapsystem.map
        self.qmap = maps.QuantumMap.QMap(self.map)
        
        self.range = self.get_range()
        self.vrange = self.get_vrange()
        self.ini_c = self.get_initial()
        self.rb_initial = 0
        self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
        self.state = 'p'
        self.step = wx.xrc.XRCCTRL(self.panel, 'SpinCtrlDrawStep').GetValue()
        self.logplot = False
        
        print self.map.Para.para
        def OnApply(event):
            self.Initialization()
        def OnRadioBoxInitial(event):
            radio = event.GetSelection()
            if radio == 0 or radio == 3:
                if radio == 0: self.state = 'p'
                else: self.state = 'qlt'
                wx.xrc.XRCCTRL(self.panel, 'TextCtrlq_c').Enable(False)
                wx.xrc.XRCCTRL(self.panel, 'TextCtrlp_c').Enable(True)
            elif radio == 1:
                self.state = 'q'
                wx.xrc.XRCCTRL(self.panel, 'TextCtrlq_c').Enable(True)
                wx.xrc.XRCCTRL(self.panel, 'TextCtrlp_c').Enable(False)
            else:
                self.state = 'cs'
                wx.xrc.XRCCTRL(self.panel, 'TextCtrlq_c').Enable(True)
                wx.xrc.XRCCTRL(self.panel, 'TextCtrlp_c').Enable(True)
        def OnSetInitialState(event):
            self.range = self.get_range()
            self.ini_c = self.get_initial()
            self.qmap.setRange(self.range[0], self.range[1], self.range[2],self.range[3], self.range[4])
            if self.state in ('p','plt'):
                self.qmap.setState(self.state,self.ini_c[1])
            elif self.state in ('q'):
                self.qmap.setState(self.state, self.ini_c[0])
            else:
                self.qmap.setState(self.state, self.ini_c[0],self.ini_c[1])
            self.Draw(iter=0)
        def OnSpinIteration(event):
            self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
        def OnButtonIteration(event):
            self.qmap.evolve(self.iteration)
        def OnRadioBoxRep(event):
            radio = event.GetSelection()
            print radio
        def OnSpinDrawStep(event):
            self.step = wx.xrc.XRCCTRL(self.panel, 'SpinCtrlDrawStep').GetValue()
        def OnButtonDraw(event):
            self.Draw(self.step)
        def OnButtonNext(event):
            self.step += 1
            wx.xrc.XRCCTRL(self.panel,'SpinCtrlDrawStep').SetValue(self.step)
            self.Draw(self.step)
        def OnButtonPrev(event):
            self.step -= 1
            wx.xrc.XRCCTRL(self.panel,'SpinCtrlDrawStep').SetValue(self.step)
            self.Draw(self.step)
        def OnCheckBoxLog(event):
            self.logplot = event.IsChecked()


        self.Bind(wx.EVT_BUTTON, OnApply, wx.xrc.XRCCTRL(self.panel, 'ButtonApply'))
        self.Bind(wx.EVT_RADIOBOX, OnRadioBoxInitial, wx.xrc.XRCCTRL(self.panel,'RadioBoxIniState'))
        self.Bind(wx.EVT_BUTTON, OnSetInitialState, wx.xrc.XRCCTRL(self.panel, 'ButtonSet'))  
        if wx.Platform != '__WXMAC__':
            self.Bind(wx.EVT_SPINCTRL,OnSpinIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        else:
            self.Bind(wx.EVT_TEXT, OnSpinIteration, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlIteration'))
        self.Bind(wx.EVT_BUTTON, OnButtonIteration, wx.xrc.XRCCTRL(self.panel, 'ButtonIter'))
        self.Bind(wx.EVT_RADIOBOX, OnRadioBoxRep, wx.xrc.XRCCTRL(self.panel, 'RadioBoxRep'))
        if wx.Platform != '__WXMAC__':
            self.Bind(wx.EVT_SPINCTRL,OnSpinDrawStep, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlDrawStep'))
        else:
            self.Bind(wx.EVT_TEXT, OnSpinDrawStep, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlDrawStep'))
        self.Bind(wx.EVT_BUTTON, OnButtonDraw, wx.xrc.XRCCTRL(self.panel, 'ButtonDraw'))
        self.Bind(wx.EVT_BUTTON, OnButtonNext, wx.xrc.XRCCTRL(self.panel, 'ButtonNext'))
        self.Bind(wx.EVT_BUTTON, OnButtonPrev, wx.xrc.XRCCTRL(self.panel, 'ButtonPrev'))
        self.Bind(wx.EVT_CHECKBOX, OnCheckBoxLog, wx.xrc.XRCCTRL(self.panel, 'CheckBoxLog'))
            
        ## make plotpanel
        self.plotpanel=parent.GetParent().MakePlotPanel(self.title)
        self.plotpanel.OnPress = self.OnPress
    def Initialization(self):
        self.map = self.mapsystem.map
        self.qmap = maps.QuantumMap.QMap(self.map)
        
        self.range = self.get_range()
        self.vrange = self.get_vrange()
        self.ini_c = self.get_initial()
        self.rb_initial = 0
        self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
        self.state = 'p'
        self.step = wx.xrc.XRCCTRL(self.panel, 'SpinCtrlDrawStep').GetValue()
        self.logplot = False
        
        print self.map.Para.para
    def OnPress(self, xy):
        print xy
        iter = 200
        trajectory=True
        self.mapsystem.setTrajectory(trajectory)
        self.mapsystem.setInit(maps.MapSystem.Point(self.mapsystem.dim,data=[xy[0],xy[1]]))
        self.mapsystem.evolves(iter)
        xy=numpy.array(self.mapsystem.Trajectory[0]).transpose() if self.trajectory else numpy.array(self.mapsystem.P.data).transpose()[0]
        self.plotpanel.replot(xy[0],xy[1],',')
        self.plotpanel.draw()
    def get_range(self):
        qmin = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlQmin").GetValue())
        qmax = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlQmax").GetValue())
        pmin = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlPmin").GetValue())
        pmax = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlPmax").GetValue())
        hdim = int(wx.xrc.XRCCTRL(self.panel, "TextCtrlHdim").GetValue())
        return (qmin, qmax, pmin, pmax, hdim)
    def get_vrange(self):
        vqmin = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlVQmin").GetValue())
        vqmax = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlVQmax").GetValue())
        vpmin = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlVPmin").GetValue())
        vpmax = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlVPmax").GetValue())
        col = int(wx.xrc.XRCCTRL(self.panel, "TextCtrlQgrid").GetValue())
        row = int(wx.xrc.XRCCTRL(self.panel, "TextCtrlPgrid").GetValue())
        return (vqmin, vqmax, vpmin, vpmax,col, row)
    def get_initial(self):
        q_c = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlq_c").GetValue())
        p_c = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlp_c").GetValue())
        return (q_c, p_c)
    def Draw(self, iter):
        range = self.get_vrange()
        xmin, xmax = range[0],range[1]
        ymin, ymax = range[2],range[3]
        col, row = range[4], range[5]
        self.qmap.setVRange(xmin, xmax, ymin, ymax, col, row)
        if iter == 0:
            data = self.qmap.get_hsmdata(self.qmap.ivec)
        else:
            data = self.qmap.get_hsmdata(self.qmap.qvecs[iter])
        x = numpy.arange(xmin, xmax, (xmax - xmin)/col)
        y = numpy.arange(ymin, ymax, (ymax - ymin)/row)
        X,Y = numpy.meshgrid(x,y)
        #todo
        # I want to use imshow (for view), but ... 
        #extent = (xmin, xmax, ymin, ymax)
        self.plotpanel.plot()
        if self.logplot:
            self.plotpanel.axes.contourf(X,Y,numpy.log(data), hold='on', color='k')
        else:
            self.plotpanel.axes.contourf(X,Y,data, hold='on', color='k')
        #self.plotpanel.axes.imshow(data,cmap=pylab.cm.Oranges,extent=extent)
        self.plotpanel.draw()

        