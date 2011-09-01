import wx
import wx.xrc
import numpy
import Utils
import maps.MapSystem, maps.QuantumMap

from MainPanel import _SubPanel

class QmapEvolvePanel(_SubPanel):
    def __init__(self, parent, mapsystem, title):
        _SubPanel.__init__(self, parent, mapsystem, title)

        xmlresource=wx.xrc.XmlResource("OnSight/data/xrc/qmapevolvepanel.xrc")
        self.panel=xmlresource.LoadPanel(self,"qmapevolvepanel")

        sizer=wx.BoxSizer()
        sizer.Add(self.panel,proportion=1,flag= wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)
        
        self.map = self.mapsystem.map
        self.qmap = maps.QuantumMap.QMap(self.map)
        
        self.Initialization()
        
        self.range = self.get_range()
        self.vrange = self.get_vrange()
        self.ini_c = self.get_initial()
        self.rb_initial = 0
        self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()
        self.state = 'p'
        self.step = wx.xrc.XRCCTRL(self.panel, 'SpinCtrlDrawStep').GetValue()
        self.logplot = False
        self.cmap_data = []
        exp_part = int(wx.xrc.XRCCTRL(self.panel, 'TextCtrlLogMin').GetValue())
        self.vmin = 10**(-exp_part)
        self.draw = self.DrawHsm
        self.rep = 'hsm'

        def OnClear(event):
            self.cmap_data = []
            self.plotpanel.clear()
            try: self.draw(self.step, self.rep)
            except :pass

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
            self.plotpanel.clear()
            self.range = self.get_range()
            self.ini_c = self.get_initial()
            self.qmap.setRange(self.range[0], self.range[1], self.range[2],self.range[3], self.range[4])
            
            if self.state in ('p','plt'):
                self.qmap.setState(self.state,self.ini_c[1])
            elif self.state in ('q'):
                self.qmap.setState(self.state, self.ini_c[0])
            else:
                self.qmap.setState(self.state, self.ini_c[0],self.ini_c[1])
            self.DrawHsm(0, 'hsm')
            wx.xrc.XRCCTRL(self.panel, 'ButtonIter').Enable(True)
            wx.xrc.XRCCTRL(self.panel, 'ButtonDraw').Enable(False)
            wx.xrc.XRCCTRL(self.panel, 'ButtonNext').Enable(False)
            wx.xrc.XRCCTRL(self.panel, 'ButtonPrev').Enable(False)

        def OnSpinIteration(event):
            self.iteration = wx.xrc.XRCCTRL(self.panel,'SpinCtrlIteration').GetValue()

        def OnButtonIteration(event):
            wx.xrc.XRCCTRL(self.panel, 'ButtonDraw').Enable(True)
            wx.xrc.XRCCTRL(self.panel, 'ButtonNext').Enable(True)
            self.step = 0
            wx.xrc.XRCCTRL(self.panel, 'SpinCtrlDrawStep').SetValue(self.step)
            self.qmap.evolve(self.iteration)
            self.qmap.get_pvecs()

        def OnRadioBoxRep(event):
            radio = event.GetSelection()
            if radio == 0:
                self.rep = 'hsm'
                self.draw = self.DrawHsm
            elif radio == 1:
                self.rep = 'p'
                self.draw = self.Draw
            else:
                self.rep = 'q'
                self.draw = self.Draw

        def OnSpinDrawStep(event):
            self.step = wx.xrc.XRCCTRL(self.panel, 'SpinCtrlDrawStep').GetValue()
            if self.step == self.iteration:
                wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(False)
            elif self.step == 0:
                wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(False)
            else:
                wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(True)
                wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(True)
            wx.xrc.XRCCTRL(self.panel,'SpinCtrlDrawStep').SetRange(0,self.iteration)

        def OnButtonDraw(event):
            self.plotpanel.clear()
            self.draw(self.step, self.rep)

        def OnButtonNext(event):
            self.step += 1
            wx.xrc.XRCCTRL(self.panel,'SpinCtrlDrawStep').SetValue(self.step)
            if self.step == self.iteration:
                wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(False)
            else:
                wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(True)
                wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(True)
            self.draw(self.step, self.rep)

        def OnButtonPrev(event):
            self.step -= 1
            wx.xrc.XRCCTRL(self.panel,'SpinCtrlDrawStep').SetValue(self.step)
            if self.step == 0:
                wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(False)
            else:
                wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(True)
                wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(True)

            self.draw(self.step, self.rep)

        def OnCheckBoxLog(event):
            self.logplot = event.IsChecked()
 
        def OnTextLogMin(event):
            exp_part = wx.xrc.XRCCTRL(self.panel, 'TextCtrlLogMin').GetValue()
            if exp_part != '':
                self.vmin = 10**(-int(exp_part))




        self.Bind(wx.EVT_BUTTON, OnClear, wx.xrc.XRCCTRL(self.panel, 'ButtonClear'))
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
        self.Bind(wx.EVT_TEXT, OnTextLogMin, wx.xrc.XRCCTRL(self.panel, 'TextCtrlLogMin'))
        ## make plotpanel
        self.plotpanel=parent.GetParent().MakePlotPanel(self.title)
        self.plotpanel.OnPress = self.OnPress
        self.plotpanel.plot()
        self.set_lim()
        self.plotpanel.draw()

    def Initialization(self):
        range = self.qmap.get_range()
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlQmin').SetValue(str(range[0]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlQmax').SetValue(str(range[1]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlPmin').SetValue(str(range[2]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlPmax').SetValue(str(range[3]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlHdim').SetValue(str(range[4]))
        vrange= self.qmap.get_vrange()
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlVQmin').SetValue(str(vrange[0]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlVQmax').SetValue(str(vrange[1]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlVPmin').SetValue(str(vrange[2]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlVPmax').SetValue(str(vrange[3]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlQgrid').SetValue(str(vrange[4]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlPgrid').SetValue(str(vrange[5]))    
        
        
    def set_lim(self):
        range = self.get_vrange()
        self.plotpanel.xlim = (range[0], range[1])
        self.plotpanel.ylim = (range[2], range[3])
        self.plotpanel.setlim() 
         
    def OnPress(self, xy):
        iter = 200
        trajectory=True
        #self.mapsystem.Psetting = [(True,1.0), (False, 1.0)]
        self.mapsystem.setTrajectory(trajectory)
        self.mapsystem.setInit(maps.MapSystem.Point(self.mapsystem.dim,data=[xy[0],xy[1]]))
        self.mapsystem.evolves(iter)
        xy=numpy.array(self.mapsystem.Trajectory[0]).transpose()
        self.cmap_data.append(xy)
        self.plotpanel.replot(xy[0],xy[1],',k')
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

    def DrawHsm(self, iter, rep='hsm'):
        range = self.get_vrange()
        xmin, xmax = range[0],range[1]
        ymin, ymax = range[2],range[3]
        col, row = range[4], range[5]
        self.qmap.setVRange(xmin, xmax, ymin, ymax, col, row)
        self.set_lim()

        x = numpy.arange(xmin, xmax, (xmax - xmin)/col)
        y = numpy.arange(ymin, ymax, (ymax - ymin)/row)
        X,Y = numpy.meshgrid(x,y)
        if iter == 0:
            data = self.qmap.get_hsmdata(self.qmap.ivec)
        else:
            data = self.qmap.get_hsmdata(self.qmap.qvecs[iter])
        
        self.plotpanel.clear()
        import pylab
        if self.logplot:
            data = self.qmap.rounding_hsmdata(data, 1.0/self.vmin)
            index = numpy.where(data == 0.0)
            data[index] = numpy.nan
            self.plotpanel.axes.contourf(X,Y,numpy.log(data),color='k')
            self.plotpanel.axes.contourf(X,Y,numpy.log(data), cmap=pylab.cm.Oranges)
        else:
            #index = numpy.where(data < 1e-4)
            #data[index] = numpy.nan
            self.plotpanel.axes.contour(X,Y,data,color='k')
            self.plotpanel.axes.contourf(X,Y,data,cmap=pylab.cm.Oranges)
        if True:
            for xy in self.cmap_data:
                self.plotpanel.replot(xy[0],xy[1],',k')
        self.plotpanel.setlim()
        self.plotpanel.draw()
        
    def Draw(self, iter, rep):
        if rep in ('hsm'): raise TypeError
        range = self.get_range()
        vrange = self.get_vrange()
        qmin, qmax = range[0], range[1]
        pmin, pmax = range[2], range[3]
        hdim = range[4]
        self.plotpanel.plot()
        
        q = numpy.arange(qmin, qmax, (qmax - qmin)/hdim)
        p = numpy.arange(pmin, pmax, (pmax - pmin)/hdim)

        
        if self.logplot: self.plotpanel.ylim = (self.vmin, None)
        else: self.plotpanel.ylim = (0, None)

        if rep == 'q':
            self.plotpanel.xlim = (vrange[0], vrange[1])
            self.plotpanel.setlim()
            data = self.qmap.qvecs[iter]
            
            self.plotpanel.plot(q, numpy.abs(data)**2,'-')
            
        elif rep == 'p':
            self.plotpanel.xlim = (vrange[2],vrange[3])
            self.plotpanel.setlim()
            data = self.qmap.pvecs[iter]
            
            self.plotpanel.plot(p, numpy.abs(data)**2,'-')
        if self.logplot: self.plotpanel.axes.set_yscale('log')
        else : self.plotpanel.axes.set_yscale('linear')
        #else self.logplot:
        self.plotpanel.draw()
        

        