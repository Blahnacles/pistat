"""
TEAMS CSE3PRB
PiStat - Minituarised PotentioStat
Team members:
    Luke Gidley - 18089236; Simon Laffan 18774937; Keenan Saleh - 19529401;
    Kush Shah - 19548278; Rihtvik Sharma - 18851514
deviceConfig.py manages connection with the potentiostat through usb. 
takes commands from the testEngine to manage this connection, run cyclic voltammetry,
and set parameters on the device. Also manages data storage and access.
"""
import testEngine
import tkinter as tk
from tkinter import ttk
from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import timeit
import time
import numpy as np
LARGE_FONT= ("Verdana", 12)

style.use("ggplot")
f = Figure(figsize=(4.3,4), dpi = 100, tight_layout=True)
a = f.add_subplot(111)
global xList
global yList
global linearRegFlag
linearRegFlag=False
global croppedListXFinal
croppedListXFinal = None
global croppedListYFinal
croppedListYFinal = None
global xList, yList
global upVolt, lowVolt
global xCoords, yCoords
global pSelect
xCoords = []
yCoords = []
pSelect = 0
global selX, selY, win
selX = []
selY = []


#p = 1e3*0.09 # read every 90 ms
p = 1e3*1 # read every second
psec = 1
firstRead = timeit.default_timer()
lastRead = firstRead
tSum = lastRead
ani = None

win = None

def testAnimate(i):
    """Animation function for graph. Run by an animation in root
    Graphs relevant data depending on device state and user inputs
    Author: Luke Gidley"""
    global croppedListXFinal, croppedListYFinal, linearRegFlag, xList, yList, pSelect, win
    xList, yList = testEngine.getData()
    a.clear()
    a.autoscale(False)
    if len(xList):
        a.plot(xList,yList)
        if len(xCoords):
            if pSelect == 2:
                a.plot(xCoords,yCoords)
            else:
                a.scatter(xCoords,yCoords)
        miny = min(yList)
        maxy = max(yList)

        a.axes.set_ylim(miny-(maxy-miny)*0.1, maxy)
        a.axes.set_xlim(min(xList)*1.1,max(xList)*1.1)
        #a.axes.set_yscale("symlog") # why though?
    s = testEngine.getState()
    #if s == testEngine.dc.States.IdleInit:
    #elif s == testEngine.dc.States.zOffset and win is not None:
    #elif s == testEngine.dc.States.Idle and win is not None:

    a.set_xlabel("Potential")
    a.set_ylabel("Current")
    



class Deploy(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        for F in (SimpleMode, ExpertMode):
        
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SimpleMode)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()



    

def getLinearParameters(entryX1,entryX2):
    """Takes two points, and performs a linear regression for all points except the range between x1 & x2"""
    global croppedListXFinal, croppedListYFinal, linearRegFlag, xList, yList


    xxList = xList[:]
    yyList = yList[:]
    xxList = xxList[::-1]
    yyList = yyList[::-1]

    indexX1 = np.abs([xx-entryX1 for xx in xxList]).argmin()
    indexX2 = np.abs([xx-entryX2 for xx in xxList]).argmin()
    xxList = xList[:]
    if indexX1>indexX2:
        indexX1,indexX2 = indexX2,indexX1
    #crop list of data to remove peak for X
    croppedListX1 = xxList[0:indexX1]
    croppedListX2 = xxList[indexX2:]
    #Append lists for X
    croppedListXFinal = np.concatenate((croppedListX1, croppedListX2))
    print(str(type(croppedListX1)))
    #crop list of data to remove peak for Y
    croppedListY1 = yyList[0:indexX1]
    croppedListY2 = yyList[indexX2:]
    #Append data for Y
    croppedListYFinal = np.concatenate((croppedListY1, croppedListY2))

    linearRegFlag=True
        
class SimpleMode(tk.Frame):
    """Main screen, handles basic device interactions and simple user settings & params
    Created by Luke Gidley"""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        global f
        #tk.frame.config(bg="white")

        def updatePlot():
            a.plot(xCoords, yCoords)
            canvas.draw()

        colourLabelY = tk.Label(self, background="#326ada", width=5, height=16)
        #colourLabelY.grid(column=0, rowspan=4)
        colourLabelY.place(x=0, y=0, height=480, width=50 )

        #label = tk.Label(self, text="0000", font=LARGE_FONT)
        #label.grid(column=1, row=1)

        label = tk.Label(self, text="PiStat", font=LARGE_FONT)
        #label.grid(column=1, row=1)
        label.place(x = 60, y = 5)
        
        colourLabelX = tk.Label(self, background="#326ada", width=54, height=2)
        colourLabelX.place(x=0, y=440, height=40, width=800)
        
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().place(y=40, x=60)
        seperationLabel = tk.Label(self, background="black")
        seperationLabel.place(x=500, y=0, height=480, width=5)
        x1Label = tk.Label(self, text="X1 Value")
        x1Label.place(x=0, y=0)
        x2Label = tk.Label(self, text="X2 Value")
        x2Label.place(x=515, y=140)
        entryX1 = ttk.Entry(self, width=10)
        #entryX1.grid(column=3, row = 2)
        entryX1.place(x=510, y=80)
        entryX2 = ttk.Entry(self, width=10)
        #entryX2.grid(column=2, row = 2, pady=5)
        entryX2.place(x=510, y=160)
        x1Label.place_forget()
        x2Label.place_forget()
        entryX1.place_forget()
        entryX2.place_forget()
        setLinearRegressionButton = ttk.Button(self, text="Select Data Points")
        #setLinearRegressionButton.grid(column=3, row=5)
        setLinearRegressionButton.place(x=510, y=280)
        sLRBcancel = ttk.Button(self, text="Reset Point Selection")
        sLRBcancel.place(x=510,y=260)
        sLRBcancel.place_forget()
        buttonExpertMode = ttk.Button(self, text="Expert")
        #buttonExpertMode.grid(column=3, row=1)
        buttonExpertMode.place(x=50, y=445, width = 60)
        calibrateButton = ttk.Button(self, text="Load Data")
        #calibrateButton.grid(column=3, row=6)
        calibrateButton.place(x=510, y=200)

        #Sliders for Upper/Lower voltage bounds
        scaleLabelUpper = tk.Label(self, text="Upper Voltage")
        scaleLabelUpper.place(x=515, y=60)
        scaleLabelLower = tk.Label(self, text="Lower Voltage")
        scaleLabelLower.place(x=515, y=120)

        upperScale = Scale(self, from_=-2, to=2, orient=HORIZONTAL, resolution=0.1, length=100)
        upperScale.place(x=515, y=80)
        lowerScale = Scale(self, from_=-2, to=2, orient=HORIZONTAL, resolution=0.1)
        lowerScale.place(x=515, y=135)

        voltButton = ttk.Button(self, text="Set Voltages")
        voltButton.place(x=650, y=95)

        saveButton = ttk.Button(self, text="Save Data")
        saveButton.place(x=150, y=445)


        # Connect & calibrate button
        conButton = ttk.Button(self, text="Connect Potentiostat")
        conButton.place(x=510, y=240)

        cancelButton = ttk.Button(self, text="Reset & Cancel CV")
        cancelButton.place(x=510, y=340)        

        # Button and UI interaction functions
        def onclick(event):
            """Gathers data points from user interaction with graph
            Author: Luke Gidley"""
            global xCoords, yCoords, pSelect
            ix, iy = event.xdata, event.ydata
            if ix is not None and iy is not None and pSelect==1:
                print(ix,iy)
                xCoords.append(ix)
                yCoords.append(iy)
                setLinearRegressionButton.configure(text=str(len(xCoords))+" points - confirm?")
        cid = f.canvas.mpl_connect('button_press_event', onclick)
        def getLineParameters():
            global pSelect, xCoords, yCoords
            print(str(pSelect))
        #error message if points selected is 0, will reset array of values if true
            if pSelect == 0:
                setLinearRegressionButton.configure(text="0 points selected")
                xCoords = []
                yCoords = []
                sLRBcancel.configure(text="Reset Point Selection")
                sLRBcancel.place(x=650,y=280)
                pSelect = 1
        #enables line manipulation buttons if there are more than 0 points
            elif pSelect == 1:
                sLRBcancel.configure(text="Get Peak Height")
                setLinearRegressionButton.configure(text="Clear Line")
                pSelect = 2
            elif pSelect == 2:
                xCoords = []
                yCoords = []
                pSelect = 0
                setLinearRegressionButton.configure(text="Select Data Points")
        #function to reset the arrays with line data in it
        def lineCancel():
            global pSelect, xCoords, yCoords
            if pSelect == 2:
                h = calcHeight()
                tk.messagebox.showinfo("Peak height calculation","Peak height: "+format(1000*h[0],"f")+" mA")
                setLinearRegressionButton.configure(text="Select Data Points")
                xCoords = []
                yCoords = []
                pSelect = 0
            else:
                pSelect = 0
                sLRBcancel.place_forget()
                setLinearRegressionButton.configure(text="Select Data Points")
                xCoords = []
                yCoords = []
                pSelect = 0
        def getVoltage():
            upVolt = upperScale.get()
            lowVolt = lowerScale.get()
            if (lowVolt > upVolt) :
                # Error handling
                tk.messagebox.showerror("Floor/Ceiling Error", "The voltage floor should be less than the ceiling")
            else:
                # Do voltage setting stuff here
                a,b=testEngine.setVoltage(lowVolt,upVolt)
                tk.messagebox.showinfo("Voltage Set", "Voltage successfully set - floor: "+str(a)+"V, ceiling: "+str(b)+"V")
        
        def calcHeight():
            """Calulate the height between the peak and the line set by the user
            Authors - Simon Laffan & Luke Gidley"""
            global xList, yList, xCoords, yCoords
            xL = np.asarray(xList)
            yL = np.asarray(yList)
            #Gets max value from array
            maxHeightY = max(yL)
            #get the index of the max value for x
            maxIndex = np.where(maxHeightY==yL)
            #get value from the index of the max height value
            maxHeightX = xL[maxIndex]
            #sort the coordinates
            xCoords, yCoords = zip(*sorted(zip(xCoords,yCoords)))
            
            #finds the two closest points beneath the peak
            for i in range(len(xCoords)):
                if(xCoords[i] > maxHeightX):
                    x1 = xCoords[i]
                    y1 = yCoords[i]
                    x2 = xCoords[i-1]
                    y2 = yCoords[i-1]
                    break                
            try:
                m = (y2 - y1) / (x2 - x1)
                c = y1 - m * x1
                yD = maxHeightX * m + c
            except UnboundLocalError as error:
                tk.messagebox.showerror("Peak calculation error","The given line must pass under the peak current value")
                
            return maxHeightY - yD

        def cv():
            """Handle interaction for connection, as well as initiate cv sweep"""
            res = testEngine.cv()
            if res == 0:
                tk.messagebox.showerror("Connection Error", "Please ensure the device is connected properly. If so, try reseating the usb plug.")
            else:
                tk.messagebox.showinfo("Connection Successful", "Successfully connected to piStat - the piStat is initialising")
                conButton.configure(text="Run CV")
        
        def cvCancel():
            if testEngine.getState() != testEngine.dc.States.Idle:
                tmp = tk.messagebox.askokcancel(title="Are you sure?",message="Cancel the measurement in progress?")
                if tmp:
                    testEngine.cvCancel()
                return
            tk.messagebox.showinfo(title="Device Idle", message="The potentiostat device manager is already in Idle mode")

        def saveData():
            """Open a dialog to get a file name from the user
            Save the metadata and data in this file
            Author: Simon Laffan"""
            filePath = tk.filedialog.asksaveasfilename(defaultextension='.csv')
            testEngine.saveCsv(filePath)
            

        # Assigning commands to buttons
        voltButton.configure(command=lambda: getVoltage())
        buttonExpertMode.configure(command=lambda: controller.show_frame(ExpertMode))
        conButton.configure(command=lambda: cv())
        setLinearRegressionButton.configure(command=lambda: getLineParameters())
        calibrateButton.configure(command=lambda: testEngine.dummy())
        sLRBcancel.configure(command=lambda:lineCancel())
        cancelButton.configure(command=lambda:cvCancel())
        saveButton.configure(command=lambda:saveData())

        


        
        
        
        
        
        


class ExpertMode(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        #label = tk.Label(self, text="Potentio Stat", font=LARGE_FONT)
        #label.grid
        def paramGet(entryField, paramIndex):
            entryField.delete(0,tk.END)
            entryField.insert(0, testEngine.piStat.params[paramIndex])
        
        colourLabelY = tk.Label(self, background="#326ada", width=3, height=18)
        colourLabelY.grid(column=0, rowspan=6)

        colourLabelX = tk.Label(self, background="#326ada", width=57, height=2)
        colourLabelX.grid(column=1, row=6, columnspan=5)

        label1 = tk.Label(self, text = "Voltage Floor")
        label1.grid(column=1, row = 0, padx=3, pady=3 )

        label1 = tk.Label(self, text = "Initial Voltage")
        label1.grid(column=1, row = 1, padx=3, pady=3  )

        label1 = tk.Label(self, text = "Scan Rate (V/s)")
        label1.grid(column=1, row = 2, padx=3, pady=3  )

        label1 = tk.Label(self, text = "Voltage Ceiling")
        label1.grid(column=3, row = 0, padx=3, pady=3  )

        label1 = tk.Label(self, text = "Final Voltage")
        label1.grid(column=3, row = 1, padx=3, pady=3 )

        label1 = tk.Label(self, text = "Cycles (zero for ramp)")
        label1.grid(column=3, row = 2, padx=3, pady=3  )

        voltageFloorEntry = tk.Entry(self)
        voltageFloorEntry.grid(column=2, row = 0)
        paramGet(voltageFloorEntry, 3)

        voltageCeilingEntry = tk.Entry(self)
        voltageCeilingEntry.grid(column=4, row = 0)
        paramGet(voltageCeilingEntry, 2)

        initialVoltageEntry = tk.Entry(self)
        initialVoltageEntry.grid(column=2, row = 1)
        paramGet(initialVoltageEntry, 0)

        finalVoltageEntry = tk.Entry(self)
        finalVoltageEntry.grid(column=4, row = 1)
        paramGet(finalVoltageEntry, 1)

        scanRateEntry = tk.Entry(self)
        scanRateEntry.grid(column=2, row = 2)
        paramGet(scanRateEntry, 4)

        cycleEntry = tk.Entry(self)
        cycleEntry.grid(column=4, row = 2)
        paramGet(cycleEntry, 5)

        def refresh():
            """Sets the entry values to their backend values
            Author: Simon Laffan"""
            paramGet(initialVoltageEntry, 0)
            paramGet(finalVoltageEntry, 1)
            paramGet(voltageCeilingEntry, 2)
            paramGet(voltageFloorEntry, 3)
            paramGet(scanRateEntry, 4)
            paramGet(cycleEntry, 5)
        def setDefaults():
            """Resets the parameters to default values
            Gets and sets the entry field values
            Author: Simon Laffan"""
            tmp = tk.messagebox.askokcancel(title="Are you sure?",message="The piStat parameters will be reset to their default values, would you like to proceed?")
            if tmp:
                testEngine.piStat.params = [-0.2, 0.2, 0.2, -0.2, 0.1, 0]
                refresh()
        def paramSet():
            """Send the values to the device manager
            Sanitises and checks for validity, and sets parameters
            Author: Simon Laffan"""
            msgString = ""
            # get the values
            params = testEngine.piStat.params
            try:
                vmin = float(voltageFloorEntry.get())
                vmax = float(voltageCeilingEntry.get())
                vInitial = float(initialVoltageEntry.get())
                vFinal = float(finalVoltageEntry.get())
                scanRate = float(scanRateEntry.get())
            except:
                tk.messagebox.showerror("Number format error", "Voltage and scan rates must be numbers. No settings were altered")
                return
            try:
                nCycles = int(cycleEntry.get())
            except:
                tk.messagebox.showerror("Cycle input error", "Number of cycles must be a natural number (including 0). No settings were altered")
                return
            # Check for modifications
            if vmin>vmax:
                tk.messagebox.showerror("Voltage Floor/Ceiling Error,", "Voltage floor must be less than voltage ceiling. No settings were altered")
                return
            if vmin!=params[3]:
                if abs(vmin)>2:
                    tk.messagebox.showerror("Voltage Floor Error", "Voltage floor must be between -2 and 2 Volts. No settings were altered")
                    return
                params[3] = vmin
                msgString += "[V Floor]"
            if vmax!=params[2]:
                if abs(vmax)>2:
                    tk.messagebox.showerror("Voltage Floor Error", "Voltage floor must be between -2 and 2 Volts. No settings were altered")
                    return
                params[2] = vmax
                msgString+=" [V ceiling]"
            if vInitial!=params[0]:
                if abs(vInitial)>2:
                    tk.messagebox.showerror("Start Voltage Error", "Starting voltage must be between -2 and 2 Volts. No settings were altered")
                    return
                params[0] = vInitial
                msgString+=" [V initial]"
            if vFinal!=params[1]:
                if abs(vFinal)>2:
                    tk.messagebox.showerror("End Voltage Error", "Final voltage must be between -2 and 2 Volts. No settings were altered")
                    return
                params[1] = vFinal
                msgString+=" [V final]"
            if nCycles!=params[5]:
                if nCycles<0:
                    tk.messagebox.showerror("Cycles error", "Number of cycles must be a natural number (including 0). No settings were altered")
                    return
                params[5] = nCycles
                msgString+=" [Cycles]"
            if scanRate!=params[4]:
                if scanRate<0.1 or scanRate>1:
                    tk.messagebox.showerror("Scan rate error", "Scan rate must be between 0.1 and 1 V/s. No settings were altered")
                    return
                params[4] = scanRate
                msgString+=" [Scan rate]"
            if msgString:
                tk.messagebox.showinfo("Values successfully set", "The following settings were altered: "+msgString)
            else:
                tk.messagebox.showinfo("No modifications made", "No parameter settings were altered. Try changing some values!")



            
        ttk.Button(self, text="Simple", command=lambda: controller.show_frame(SimpleMode)).grid(column=6, row=0)
        ttk.Button(self, text="Apply", command=paramSet).grid(column=2, row =3)
        ttk.Button(self, text="Refresh", command=refresh).grid(column=3,row=3)
        ttk.Button(self, text="Reset parameters", command=setDefaults).grid(column=4,row=3)






app = Deploy()
ani = animation.FuncAnimation(f, testAnimate, interval=200)
# Set appropriate screen size for given hardware
app.geometry("800x480")
#app.attributes("-zoomed", True)
app.mainloop()



