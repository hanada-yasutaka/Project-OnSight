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



        self.state_num = 0
        exp_part = int(wx.xrc.XRCCTRL(self.panel, 'TextCtrlexp_part').GetValue())
        self.vmin = 10**(-exp_part)
        self.draw = self.DrawHsm
        self.rep = 'hsm'
        self.logplot = False
        
        def OnButtonGet(event):
            range=self.get_range()
            self.N = range[4]
            self.qmap.setRange(range[0], range[1], range[2], range[3], range[4])
            self.qmap.getEigen()
            wx.xrc.XRCCTRL(self.panel, 'SpinCtrlState').Enable(True)
            wx.xrc.XRCCTRL(self.panel, 'SpinCtrlState').SetRange(0,self.N-1)
            wx.xrc.XRCCTRL(self.panel, 'SpinCtrlState').SetValue(0)
            wx.xrc.XRCCTRL(self.panel, 'ButtonDraw').Enable(True)
            wx.xrc.XRCCTRL(self.panel, 'ButtonNext').Enable(True)
        
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
            wx.xrc.XRCCTRL(self.panel,'SpinCtrlDrawStep').SetValue(self.state_num)
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
        
        self.plotpanel=parent.GetParent().MakePlotPanel(self.title)
        self.plotpanel.OnPress = self.OnPress
        self.plotpanel.plot()
        self.set_lim()
        self.plotpanel.draw()
        
        
    def OnPress(self, xy):
        iter = 200
        trajectory=True
        print xy
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
        import pylab
        #if self.logplot:
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
        
        