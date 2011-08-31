import wx
import wx.xrc
import numpy
import Utils
import maps.MapSystem, maps.QuantumMap

from MainPanel import _SubPanel

class QmapEigenPanel(_SubPanel):
    def __init__(self, parent, mapsystem, title):
        _SubPanel.__init__(self, parent, mapsystem, title)

        xmlresource=wx.xrc.XmlResource("OnSight/data/xrc/qmapeigen.xrc")
        self.panel=xmlresource.LoadPanel(self,"qmapeigen")

        sizer=wx.BoxSizer()
        sizer.Add(self.panel,proportion=1,flag= wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)
        
        self.map = self.mapsystem.map
        self.qmap = maps.QuantumMap.QMap(self.map)
        
        self.cmap_data = []


        ### 
        self.state_num = 0
        exp_part = int(wx.xrc.XRCCTRL(self.panel, 'TextCtrlexp_part').GetValue())
        self.vmin = 10**(-exp_part)
        self.draw = self.DrawHsm
        self.rep = 'hsm'
        self.logplot = False
        
        ###
        self.Initialization()
        
        
        def OnButtonGet(event):
            range=self.get_range()
            self.N = range[4]
            self.qmap.setRange(range[0], range[1], range[2], range[3], range[4])
            self.qmap.getEigen()
            self.qmap.get_pvecs()
            
            wx.xrc.XRCCTRL(self.panel, 'SpinCtrlState').Enable(True)
            wx.xrc.XRCCTRL(self.panel, 'SpinCtrlState').SetRange(0,self.N-1)
            wx.xrc.XRCCTRL(self.panel, 'SpinCtrlState').SetValue(0)
            wx.xrc.XRCCTRL(self.panel, 'ButtonDraw').Enable(True)
            wx.xrc.XRCCTRL(self.panel, 'ButtonNext').Enable(True)
            wx.xrc.XRCCTRL(self.panel, 'ButtonEigenValueDraw').Enable(True)
        
        def OnSpinState(event):
            self.state_num = wx.xrc.XRCCTRL(self.panel, 'SpinCtrlState').GetValue()
            if self.state_num == self.N - 1:
                wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(False)
            elif self.state_num == 0:
                wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(False)
            else:
                wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(True)
                wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(True)

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

        def OnButtonDraw(event):
            self.plotpanel.clear()
            self.draw(self.state_num, self.rep)
            
        def OnButtonNext(event):
            self.state_num += 1
            wx.xrc.XRCCTRL(self.panel,'SpinCtrlState').SetValue(self.state_num)
            if self.state_num == self.N:
                wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(False)
            else:
                wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(True)
                wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(True)
            self.draw(self.state_num, self.rep)

        def OnButtonPrev(event):
            self.state_num -= 1
            wx.xrc.XRCCTRL(self.panel,'SpinCtrlState').SetValue(self.state_num)
            if self.state_num == 0:
                wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(False)
            else:
                wx.xrc.XRCCTRL(self.panel,'ButtonPrev').Enable(True)
                wx.xrc.XRCCTRL(self.panel,'ButtonNext').Enable(True)
            self.draw(self.state_num, self.rep)

        def OnCheckBoxLog(event):
            self.logplot = event.IsChecked()

        def OnTextLogMin(event):
            exp_part = wx.xrc.XRCCTRL(self.panel, 'TextCtrlLogMin').GetValue()
            if exp_part != '':
                self.vmin = 10**(-int(exp_part))
                
        def OnButtonEvalsDraw(event):
            try: self.evalplot.clear()
            except: self.evalplot=parent.GetParent().MakePlotPanel('eigen values')
            self.DrawEigenValues()
        
        def OnButtonClear(event):
            self.cmap_data = []
            self.plotpanel.clear()
            self.draw(self.state_num, self.rep)
                        
        self.Bind(wx.EVT_BUTTON, OnButtonGet, wx.xrc.XRCCTRL(self.panel, 'ButtonGet'))
        if wx.Platform != '__WXMAC__':
            self.Bind(wx.EVT_SPINCTRL,OnSpinState, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlState'))
        else:
            self.Bind(wx.EVT_TEXT, OnSpinState, wx.xrc.XRCCTRL(self.panel, 'SpinCtrlState'))
        self.Bind(wx.EVT_RADIOBOX, OnRadioBoxRep, wx.xrc.XRCCTRL(self.panel, 'RadioBoxRep'))
        self.Bind(wx.EVT_BUTTON, OnButtonDraw, wx.xrc.XRCCTRL(self.panel, 'ButtonDraw'))
        self.Bind(wx.EVT_BUTTON, OnButtonNext, wx.xrc.XRCCTRL(self.panel, 'ButtonNext'))
        self.Bind(wx.EVT_BUTTON, OnButtonPrev, wx.xrc.XRCCTRL(self.panel, 'ButtonPrev'))
        self.Bind(wx.EVT_CHECKBOX, OnCheckBoxLog, wx.xrc.XRCCTRL(self.panel, 'CheckBoxLog'))
        self.Bind(wx.EVT_TEXT, OnTextLogMin, wx.xrc.XRCCTRL(self.panel, 'TextCtrlexp_part'))
        self.Bind(wx.EVT_BUTTON, OnButtonEvalsDraw, wx.xrc.XRCCTRL(self.panel, 'ButtonEigenValueDraw'))
        self.Bind(wx.EVT_BUTTON, OnButtonClear, wx.xrc.XRCCTRL(self.panel, 'ButtonClear'))
        
        self.plotpanel=parent.GetParent().MakePlotPanel(self.title)
        self.plotpanel.OnPress = self.OnPress
        self.plotpanel.plot()
        self.set_lim()
        self.plotpanel.draw()
    
    def Initialization(self):
        range = self.qmap.get_range()
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlqmin').SetValue(str(range[0]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlqmax').SetValue(str(range[1]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlpmin').SetValue(str(range[2]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlpmax').SetValue(str(range[3]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlhdim').SetValue(str(range[4]))
        vrange= self.qmap.get_vrange()
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlvqmin').SetValue(str(vrange[0]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlvqmax').SetValue(str(vrange[1]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlvpmin').SetValue(str(vrange[2]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlvpmax').SetValue(str(vrange[3]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlqgrid').SetValue(str(vrange[4]))
        wx.xrc.XRCCTRL(self.panel, 'TextCtrlpgrid').SetValue(str(vrange[5]))      
        
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
        
    def set_lim(self):
        range = self.get_vrange()
        self.plotpanel.xlim = (range[0], range[1])
        self.plotpanel.ylim = (range[2], range[3])
        self.plotpanel.setlim() 
        
    def get_range(self):
        qmin = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlqmin").GetValue())
        qmax = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlqmax").GetValue())
        pmin = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlpmin").GetValue())
        pmax = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlpmax").GetValue())
        hdim = int(wx.xrc.XRCCTRL(self.panel, "TextCtrlhdim").GetValue())
        return (qmin, qmax, pmin, pmax, hdim)
    
    def get_vrange(self):
        vqmin = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlvqmin").GetValue())
        vqmax = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlvqmax").GetValue())
        vpmin = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlvpmin").GetValue())
        vpmax = float(wx.xrc.XRCCTRL(self.panel, "TextCtrlvpmax").GetValue())
        col = int(wx.xrc.XRCCTRL(self.panel, "TextCtrlqgrid").GetValue())
        row = int(wx.xrc.XRCCTRL(self.panel, "TextCtrlpgrid").GetValue())
        return (vqmin, vqmax, vpmin, vpmax,col, row)
    
    def Draw(self, num, rep):
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
            data = self.qmap.evecs[num]
            
            self.plotpanel.plot(q, numpy.abs(data)**2,'-')
            
        elif rep == 'p':
            self.plotpanel.xlim = (vrange[2],vrange[3])
            self.plotpanel.setlim()
            data = self.qmap.pvecs[num]
            
            self.plotpanel.plot(p, numpy.abs(data)**2,'-')
        if self.logplot: self.plotpanel.axes.set_yscale('log')
        else : self.plotpanel.axes.set_yscale('linear')
        self.plotpanel.draw()
        
        
    def DrawHsm(self, num, rep='hsm'):
        range = self.get_vrange()
        xmin, xmax = range[0],range[1]
        ymin, ymax = range[2],range[3]
        col, row = range[4], range[5]
        self.qmap.setVRange(xmin, xmax, ymin, ymax, col, row)
        self.set_lim()

        x = numpy.arange(xmin, xmax, (xmax - xmin)/col)
        y = numpy.arange(ymin, ymax, (ymax - ymin)/row)
        X,Y = numpy.meshgrid(x,y)
        
        data =  self.qmap.get_hsmdata(self.qmap.evecs[num])

        self.plotpanel.clear()
        self.plotpanel.axes.set_yscale('linear')
        import pylab
        #if self.logplot:
        if self.logplot:
            data = self.qmap.rounding_hsmdata(data, 1.0/self.vmin)
            index = numpy.where(data == 0.0)
            data[index] = numpy.nan
            self.plotpanel.axes.contourf(X,Y,numpy.log(data),color='k')
            self.plotpanel.axes.contourf(X,Y,numpy.log(data), cmap=pylab.cm.Oranges)
        else:
            self.plotpanel.axes.contour(X,Y,data,color='k')
            self.plotpanel.axes.contourf(X,Y,data,cmap=pylab.cm.Oranges)
        if True:
            for xy in self.cmap_data:
                self.plotpanel.replot(xy[0],xy[1],',k')
        try:
            self.evalplot.clear()
            self.DrawEigenValues(num)
        except:
            pass
        self.plotpanel.setlim()
        self.plotpanel.draw()
        
    def DrawEigenValues(self, num=None):
        data = self.qmap.evals
        
        theta = numpy.arange(0,2.0*numpy.pi,0.01)
        z = numpy.cos(theta) + 1.j*numpy.sin(theta) 
        
        self.evalplot.plot(data.real, data.imag,'.')
        self.evalplot.replot(z.real, z.imag,'-')
        if num != None:
            self.evalplot.replot(data[num].real, data[num].imag, 'o')
        self.evalplot.xlim=(-1.1, 1.1)
        self.evalplot.ylim=(-1.1, 1.1)
        self.evalplot.setlim()
        self.evalplot.draw()    