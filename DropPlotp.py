import wx
import re
import tempfile
import numpy as np
import os.path
import matplotlib.pyplot as plt
import math

def dlatlon2xy(lat, lon, xoffset, yoffset):

    rlat1 = []
    rlat2 = []
    rlon1 = []
    rlon2 = []
    dlat = []
    dlon = []
    dx = []
    dy = []
    x = []
    y = []
    R = 6371000
    i=0

    for j in range(len(lat)):
        x.append(0) #  X AND Y offset are interchanged again
        y.append(0) #

    while i < len(lat)-1:
        rlat1.append(lat[i]*math.pi/180);
        rlat2.append(lat[i+1]*math.pi/180);
        rlon1.append(lon[i]*math.pi/180);
        rlon2.append(lon[i+1]*math.pi/180);

        dlat.append(rlat2[i] - rlat1[i])
        dlon.append(rlon2[i] - rlon1[i])

        dx.append(R*dlon[i]*math.cos((rlat1[i]+rlat2[i])/2))
        dy.append(R*dlat[i])
        # print dx[i]," ",dy[i],"\n"

        if i==0:
            print "xoffset yoffset",xoffset," ",yoffset,"\n"
            x[i] += dx[i] + yoffset #X & Y offset are interchanged
            y[i] += dy[i] + xoffset
            print "x[0] y[0] ",x[i]," ",y[i],"\n"

        else:
            x[i] = dx[i] + x[i-1]
            y[i] = dy[i] + y[i-1]
            # print x[i]," ",y[i],"\n"
        i+=1

    print " Reached the end \n"
    return (x, y)

class PlottingManager():

    def __init__(self):
        print "__init__(self) \n"

        # Change the default colors
        self.data_log = False;
        self.traj_log = False;
        self.TimeYaw  = False;
        self.latlon = False;
        self.clearMode = False;
        self.gps = False
        self.mhe = False

    def SetClearMode(self,cs):
        plt.clf()
        plt.draw()
        self.clearMode=cs


    def setHistMode(self,hs):
        self.histMode = hs


    def setdatalogMode(self,ds):
        self.data_log = ds

    def setFitData(self,fs):
        self.fitData = fs

    def setlatlonMode(self,ss):
        print " setlatlonMode gets called \n"
        self.latlon = ss

    def setTimeYawMode(self,ys):
        self.TimeYaw = ys

    def setGPSMode(self,gs):
        self.gps = gs

    def setMHEMode(self,ms):
        self.mhe = ms

    def plotData(self,filename, xcol, ycol, flip_data=True):
        abstract = self.getData(filename,xcol,ycol)
        # plt.plot(abstract[0], abstract[1])


        do_else = True  # This allows for a default plot when none of the
                        #buttons are set
        if self.data_log:
                            #plt.figure(1)
                            #plt.title('GPS & MHE')
                            #plt.subplot(211)
            pri_llx, pri_lly = dlatlon2xy(self.datalogVals[22],self.datalogVals[23]*-1, self.datalogVals[11][0], self.datalogVals[10][0])
            sec_llx, sec_lly = dlatlon2xy(self.datalogVals[24],self.datalogVals[25]*-1, self.datalogVals[11][0], self.datalogVals[10][0])
            plt.plot(self.datalogVals[15], self.datalogVals[14],color='r',label='MHE Trajectory')
            plt.plot(self.datalogVals[11], self.datalogVals[10], marker='+',color='k',label='GPS Trajectory')
            plt.plot(self.datalogVals[51], self.datalogVals[50]*-1,color='g',label='GPS-INS Trajectory')
            plt.plot(pri_lly,pri_llx, color='b',label='primary LatLon Trajectory')
            plt.plot(sec_lly,sec_llx, color='y',label='secondary LatLon Trajectory')

            do_else = False

        if self.latlon:
            plt.plot(self.datalogVals[22], self.datalogVals[23], marker='o',color='g',label='Latitude vs Longitube')
            do_else = False

        if self.TimeYaw:
            plt.plot(self.datalogVals[32],self.datalogVals[1], marker='o',color='y',label='Yaw vs Time ')
            do_else = False

        if self.gps:
            plt.plot(self.datalogVals[11], self.datalogVals[10], marker='o',color='b',label='GPS Trajectory')
            do_else = False

        if self.mhe:
            plt.plot(self.datalogVals[15], self.datalogVals[14], marker='o', color = 'r', label = 'MHE Trajectory')
            do_else = False

        if do_else:

            if flip_data == True:

                plt.plot(abstract[ycol], abstract[xcol], marker='o')
            else:
                 plt.plot(abstract[xcol], abstract[ycol], marker='o')


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
            data = np.genfromtxt(filename, unpack=True, delimiter=',',skip_header=2)
            self.datalogVals = data

        else:
            fileStr = re.sub('\s+', ' ', fileStr).strip()
            fp = tempfile.NamedTemporaryFile()
            fp.write(fileStr)
            data = np.genfromtxt(filename, unpack=True)
            self.datalogVals = data




        return data

    def showPlot(self):
        plt.grid(True);
        plt.legend();
        # plt.ion()
        plt.show()

MENU_FILE_EXIT = wx.NewId()
DRAG_SOURCE    = wx.NewId()

class PlotFileDropTarget(wx.TextDropTarget):
    def __init__(self, PlottingManager, obj):
        wx.TextDropTarget.__init__(self)
        self.obj = obj
        self.plotManager = PlottingManager

    def OnDropText(self, x, y, data):
        self.obj.WriteText("Will plot | "+ data[7:-2] + '\n\n')
        self.plotManager.plotData(data[7:-2],0,1)
        self.plotManager.showPlot()

class MainWindow(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent, wx.ID_ANY, title, size = (750,600), style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour(wx.WHITE)
        # Setup plotting manager
        self.plotManager = PlottingManager()
        plt.pause(0.01)

        # setup menu bar
        menuBar = wx.MenuBar()
        menu1 = wx.Menu()
        menu1.Append(MENU_FILE_EXIT, "Exit", "Quit DropPlot")
        menuBar.Append(menu1, "&File")
        self.SetMenuBar(menuBar)
        wx.EVT_MENU(self, MENU_FILE_EXIT, self.CloseWindow)

        # setup dragdrop box
        self.text = wx.TextCtrl(self, DRAG_SOURCE, "", pos=(0,0), size=(750,200), style = wx.TE_MULTILINE|wx.HSCROLL)
        self.dt1 = PlotFileDropTarget(self.plotManager,self.text)
        self.text.SetDropTarget(self.dt1)
        wx.EVT_RIGHT_DOWN(self.text, self.OnDragInit)

        # add buttons
        self.dt1.xCol = 0; self.dt1.yCol = 1;
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL); self.buttons = []
        self.sizer3 = wx.BoxSizer(wx.HORIZONTAL);
        self.sizer4 = wx.BoxSizer(wx.HORIZONTAL);


        # first row of buttons
        self.buttons.append(wx.Button(self, -1, "X Column &"))
        self.sizer2.Add(self.buttons[0], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.ChangeXaxis,self.buttons[0])

        self.buttons.append(wx.Button(self, -1, "Y Column &"))
        self.sizer2.Add(self.buttons[1], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.ChangeYaxis,self.buttons[1])

        self.buttons.append(wx.Button(self, -1, "X Title &"))
        self.sizer2.Add(self.buttons[2], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.ChangeXtitle,self.buttons[2])

        self.buttons.append(wx.Button(self, -1, "Y Title  &"))
        self.sizer2.Add(self.buttons[3], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.ChangeYtitle,self.buttons[3])

        self.buttons.append(wx.Button(self, -1, "Plot Title  &"))
        self.sizer2.Add(self.buttons[4], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.ChangeTitle,self.buttons[4])

        # second row of buttons
        self.buttons.append(wx.Button(self, -1, "Hold For Multi Plots  &"))
        self.sizer3.Add(self.buttons[5], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.ShowPlots,self.buttons[5])

        # third row of buttons

        self.buttons.append(wx.Button(self, -1, "Set datalog &"))
        self.sizer4.Add(self.buttons[6], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.Setdatalog,self.buttons[6])

        self.buttons.append(wx.Button(self, -1, "Set LatLon &"))
        self.sizer4.Add(self.buttons[7], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.Setlatlon,self.buttons[7])

        self.buttons.append(wx.Button(self, -1, "Set TimeYaw &"))
        self.sizer4.Add(self.buttons[8], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.SetTimeYaw,self.buttons[8])

        self.buttons.append(wx.Button(self, -1, "Set GPS &"))
        self.sizer4.Add(self.buttons[9], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.SetGPS,self.buttons[9])

        self.buttons.append(wx.Button(self, -1, "Set MHE &"))
        self.sizer4.Add(self.buttons[10], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.SetMHE, self.buttons[10])

        self.buttons.append(wx.Button(self, -1, "clear &"))
        self.sizer4.Add(self.buttons[11], 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.SetClearButton, self.buttons[11])

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.text, 1, wx.EXPAND)
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)
        self.sizer.Add(self.sizer3, 0, wx.EXPAND)
        self.sizer.Add(self.sizer4, 0, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()

    def ChangeXaxis(self,event):
        self.boxCol1 = wx.TextEntryDialog(None,"X- Axis Column? ","X-axis","0")
        if self.boxCol1.ShowModal() == wx.ID_OK :
            self.dt1.xCol = int(self.boxCol1.GetValue())

    def ChangeYaxis(self,event):
        self.boxCol1 = wx.TextEntryDialog(None,"Y- Axis Column? ","Y-axis","1")
        if self.boxCol1.ShowModal() == wx.ID_OK :
            self.dt1.yCol = int(self.boxCol1.GetValue())

    def ChangeXtitle(self,event):
        self.boxCol1 = wx.TextEntryDialog(None,"X- Axis Title? ","X-axis","x")
        if self.boxCol1.ShowModal() == wx.ID_OK :
            self.dt1.xTitle = self.boxCol1.GetValue()

    def ChangeYtitle(self,event):
        self.boxCol1 = wx.TextEntryDialog(None,"Y- Axis Title? ","Y-axis","y")
        if self.boxCol1.ShowModal() == wx.ID_OK :
            self.dt1.yTitle = self.boxCol1.GetValue()

    def ChangeTitle(self,event):
        self.boxCol1 = wx.TextEntryDialog(None,"Plot Title? ","X-axis","0")
        if self.boxCol1.ShowModal() == wx.ID_OK :
            self.dt1.plotTitle = self.boxCol1.GetValue()

    #functions that plot

    def ShowPlots(self,event):
        if self.dt1.plotNow:
            self.dt1.plotNow = False
            self.buttons[5].SetLabel('Show Multi Plots')
        else:
            self.dt1.plotNow = True
            self.plotManager.showPlot()
            self.buttons[5].SetLabel('Hold For Multi Plots')

    def Setdatalog(self,event):
        if self.plotManager.data_log:
            self.plotManager.setdatalogMode(False)
            self.buttons[6].SetLabel('Set GPS&MHE')

        else:
            self.plotManager.setdatalogMode(True)
            self.buttons[6].SetLabel('GPS&MHE set')

    def SetGPS(self,event):
        if self.plotManager.gps:
            self.plotManager.setGPSMode(False)
            self.buttons[9].SetLabel('Set GPS')

        else:
            self.plotManager.setGPSMode(True)
            self.buttons[9].SetLabel('GPS set')

    def SetMHE(self,event):
        if self.plotManager.mhe:
            self.plotManager.setMHEMode(False)
            self.buttons[10].SetLabel('Set MHE')

        else:
            self.plotManager.setMHEMode(True)
            self.buttons[10].SetLabel('MHE set')

    def Setlatlon(self,event):
        if self.plotManager.latlon:
            self.plotManager.setlatlonMode(False)
            self.buttons[7].SetLabel('Set Lat&Lon')

        else:
            self.plotManager.setlatlonMode(True)
            self.buttons[7].SetLabel('Lat&Lon set')

    def SetTimeYaw(self,event):
        if self.plotManager.TimeYaw:
            self.plotManager.setTimeYawMode(False)
            self.buttons[8].SetLabel('Set Time&Yaw')

        else:
            self.plotManager.setTimeYawMode(True)
            self.buttons[8].SetLabel('Time&Yaw Set')


    def SetClearButton(self,event):
        print "Entering clear buttons \n"
        self.plotManager.SetClearMode(True)
        self.buttons[11].SetLabel('clear')



    def CloseWindow(self, event):
        self.Close()

    def OnDragInit(self, event):
        tdo = wx.PyTextDataObject(self.text.GetStringSelection())
        tds = wx.DropSource(self.text)
        tds.SetData(tdo)
        tds.DoDragDrop(True)

class DropPlot(wx.App):
    def OnInit(self):
        frame = MainWindow(None, -1, "Drag data upto this window to plot")
        self.SetTopWindow(frame)
        return True

# main loop
app = DropPlot(0)
app.MainLoop()
