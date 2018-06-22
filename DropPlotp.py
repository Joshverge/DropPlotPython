import wx
import re
import tempfile
import numpy as np
import os.path
import brewer2mpl
import matplotlib as mpl
import matplotlib.pyplot as plt
from math import log10, floor

class PlottingManager():

    def plotData(self,filename, xcol, ycol):
        [tx,ty] = self.getData(filename,xcol,ycol)
        # plt.xlabel(xaxis, **self.fontax); plt.ylabel(yaxis, **self.fontax);
        # plt.title(titleIn,**self.font)
        plt.plot(tx, ty)
        print "Done Plotting"

    def getData(self,filename, xcol, ycol):
        print "Plotting : ", str(filename)
        fileIn = open(filename,'r')
        fileStr = fileIn.read()
        csvType = False
        if ',' in fileStr:
            csvType = True
        if csvType:
            #print "CSV all"
            data = np.genfromtxt(filename, unpack=True, delimiter=',')
        else:
            fileStr = re.sub('\s+', ' ', fileStr).strip()
            fp = tempfile.NamedTemporaryFile()
            fp.write(fileStr)
            data = np.genfromtxt(filename, unpack=True)

        tx = data[xcol]
        ty = data[ycol]
        return [tx,ty]

    def showPlot(self):
        plt.grid(True);
        plt.legend();
        plt.show()

MENU_FILE_EXIT = wx.NewId()
DRAG_SOURCE    = wx.NewId()

class PlotFileDropTarget(wx.TextDropTarget):
    def __init__(self, PlottingManager, obj):
        wx.TextDropTarget.__init__(self)
        self.obj = obj
        self.xCol = 0; self.yCol = 1
        self.xTitle = "x"; self.yTitle = "y";
        self.plotTitle = "plot";
        self.plotManager = PlottingManager

    def OnDropText(self, x, y, data):
        self.obj.WriteText("Will plot | "+data[7:-2] + '\n\n')
        [self.xCol,self.yCol] = [0, 1]
        print "OnDropText called \n"

        self.plotManager.plotData(data[7:-2],self.xCol,self.yCol)
        self.plotManager.showPlot()

class MainWindow(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent, wx.ID_ANY, title, size = (750,600), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)

        self.SetBackgroundColour(wx.WHITE)
        # Setup plotting manager
        self.plotManager = PlottingManager()
        # setup dragdrop box
        self.text = wx.TextCtrl(self, DRAG_SOURCE, "", pos=(0,0), size=(750,200), style = wx.TE_MULTILINE|wx.HSCROLL)
        self.dt1 = PlotFileDropTarget(self.plotManager,self.text)
        self.text.SetDropTarget(self.dt1)

        wx.EVT_RIGHT_DOWN(self.text, self.OnDragInit)
        self.Show()

    def CloseWindow(self, event):
        self.Close()

    def OnDragInit(self, event):
        tdo = wx.PyTextDataObject(self.text.GetStringSelection())
        tds = wx.DropSource(self.text)
        tds.SetData(tdo)
        tds.DoDragDrop(True)

class DropPlot(wx.App):
    def OnInit(self):
        frame = MainWindow(None, -1, "DropPlot - Drag data to plot")
        self.SetTopWindow(frame)
        return True

# main loop
app = DropPlot(0)
app.MainLoop()
