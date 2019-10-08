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
global selX, selY
selX = []
selY = []


#p = 1e3*0.09 # read every 90 ms
p = 1e3*1 # read every second
psec = 1
firstRead = timeit.default_timer()
lastRead = firstRead
tSum = lastRead
ani = None


def testAnimate(i):
    global croppedListXFinal, croppedListYFinal, linearRegFlag, xList, yList, pSelect
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
    a.set_xlabel("Potential")
    a.set_ylabel("Current")
    

def test2Animate():
    pList, cList = testEngine.piStat.getData()

    a.clear()
    a.plot(pList)

def modeToggle():
    testEngine.dToggle()


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

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        
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


        # Connect & calibrate button
        conButton = ttk.Button(self, text="Initialise CV")
        conButton.place(x=510, y=240)
        
        # Button and UI interaction functions
        def onclick(event):
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
        
            global xList, yList, xCoords, yCoords
            xL = xList[:]
            yL = yList[:]
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
        
        # Assigning commands to buttons
        voltButton.configure(command=lambda: getVoltage())
        buttonExpertMode.configure(command=lambda: controller.show_frame(ExpertMode))
        conButton.configure(command=lambda: testEngine.cv())
        setLinearRegressionButton.configure(command=lambda: getLineParameters())
        calibrateButton.configure(command=lambda: testEngine.dummy())
        sLRBcancel.configure(command=lambda:lineCancel())

        


        
        
        
        
        
        


class ExpertMode(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        #label = tk.Label(self, text="Potentio Stat", font=LARGE_FONT)
        #label.grid
        
        colourLabelY = tk.Label(self, background="#326ada", width=3, height=18)
        colourLabelY.grid(column=0, rowspan=6)

        colourLabelX = tk.Label(self, background="#326ada", width=57, height=2)
        colourLabelX.grid(column=1, row=6, columnspan=5)

        label1 = tk.Label(self, text = "DAC Offset")
        label1.grid(column=1, row = 0, padx=3, pady=3 )

        label1 = tk.Label(self, text = "DAC Gain")
        label1.grid(column=1, row = 1, padx=3, pady=3  )

        label1 = tk.Label(self, text = "Pot. Offset")
        label1.grid(column=1, row = 2, padx=3, pady=3  )

        label1 = tk.Label(self, text = "Curr. Offset")
        label1.grid(column=1, row = 3, padx=3, pady=3  )

        label1 = tk.Label(self, text = "R1")
        label1.grid(column=1, row = 4, padx=3, pady=3 )

        label1 = tk.Label(self, text = "R2")
        label1.grid(column=3, row = 0, padx=3, pady=3  )

        label1 = tk.Label(self, text = "R3")
        label1.grid(column=3, row = 1, padx=3, pady=3 )

        label1 = tk.Label(self, text = "Current Range")
        label1.grid(column=3, row = 2, padx=3, pady=3  )

        label1 = tk.Label(self, text = "Potential(V)")
        label1.grid(column=3, row = 3, padx=3, pady=3  )

        label1 = tk.Label(self, text = "PID")
        label1.grid(column=3, row = 4, padx=3, pady=3  )

        entry1 = tk.Entry(self)
        entry1.grid(column=2, row = 0)

        entry2 = tk.Entry(self)
        entry2.grid(column=2, row = 1)

        entry3 = tk.Entry(self)
        entry3.grid(column=2, row = 2)

        entry4 = tk.Entry(self)
        entry4.grid(column=2, row = 3)

        entry5 = tk.Entry(self)
        entry5.grid(column=2, row = 4)

        entry6 = tk.Entry(self)
        entry6.grid(column=4, row = 0)

        entry7 = tk.Entry(self)
        entry7.grid(column=4, row = 1)

        entry8 = tk.Entry(self)
        entry8.grid(column=4, row = 2)

        entry9 = tk.Entry(self)
        entry9.grid(column=4, row = 3)

        entry10 = tk.Entry(self)
        entry10.grid(column=4, row = 4)

        buttonSimpleMode = ttk.Button(self, text="Simple", command=lambda: controller.show_frame(SimpleMode))
        buttonSimpleMode.grid(column=6, row=0)

        applyVariables= ttk.Button(self, text="Apply")
        applyVariables.grid(column=6, row =6)
        
        def get_parameters():
            entry1Data = entry1.get()
            entry2Data = entry2.get()
            entry3Data = entry3.get()
            entry4Data = entry4.get()
            entry5Data = entry5.get()
            entry6Data = entry6.get()
            entry7Data = entry7.get()
            entry8Data = entry8.get()
            entry9Data = entry9.get()
            entry10Data = entry10.get()





app = Deploy()
ani = animation.FuncAnimation(f, testAnimate, interval=200)
app.geometry("800x480")
#app.attributes("-zoomed", True)
app.mainloop()



