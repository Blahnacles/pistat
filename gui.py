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
#from PIL import Image, ImageTk
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


#p = 1e3*0.09 # read every 90 ms
p = 1e3*1 # read every second
psec = 1
firstRead = timeit.default_timer()
lastRead = firstRead
tSum = lastRead
ani = None
def onclick(event):
    print(event.xdata, event.ydata)
    global ix, iy
    ix, iy = event.xdata, event.ydata
    global xCoords
    xCoords.append(ix)
    global yCoords
    yCoords.append(iy)
    global len
    len +=1
    print(len)
    if(len==3):
        xCoords = []
        xCoords.append(ix)
        yCoords = []
        yCoords.append(iy)
        len = 1

def testAnimate(i):
    global croppedListXFinal, croppedListYFinal, linearRegFlag, xList, yList
    xList, yList = testEngine.getData()
    a.clear()
    if testEngine.piStat.offsetBin:
        # Set the axes once offset has changed
        # set lower limit to 110% of the offset
        #h = 1.1*max(testEngine.piStat.potData.potentialOffset,testEngine.piStat.potData.currentOffset)
        #a.axes.set_ylim(-h,h)
        a.axes.set_ylim(-20,2)
        # Reset the offsetBin once it has been checked
        #testEngine.piStat.offsetBin = False
    if testEngine.piStat.state==testEngine.dc.States.Demo1:
        a.plot(xList, yList)
        a.axes.set_yscale("symlog")
        a.set_xlabel("Potential")
        a.set_ylabel("Current")
    elif linearRegFlag and croppedListXFinal is not None:
        fit = np.polyfit(croppedListXFinal, croppedListYFinal, 1)
        a.plot(xList, yList)
        a.plot(croppedListXFinal, np.polyval(fit,croppedListXFinal), 'r-')
        a.axes.set_yscale("symlog")
        a.set_xlabel("Potential")
        a.set_ylabel("Current")
        a.set_title("Sample data & regression line")
    elif testEngine.piStat.state==testEngine.dc.States.Idle:
        a.plot(xList, yList)
        a.axes.set_yscale("symlog")
        a.set_xlabel("Potential")
        a.set_ylabel("Current")
        a.set_title("Sample data")
    #elif testEngine.piStat.state==testEngine.dc.States.Measuring_PD:
        #a.axes.set_yscale()
    else:
        a.plot(xList)
        a.plot(yList)

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

    @staticmethod
    def testFunction():
        print("Testing!")

def getLinearParameters(entryX1,entryX2):
    """Takes two points, and performs a linear regression for all points except the range between x1 & x2"""
    global croppedListXFinal, croppedListYFinal, linearRegFlag, xList, yList
    #Split point data into X and Y
    #x1,y1 = setPointxy1.split(',')
    #x2,y2 = setPointxy2.split(',')

    #create array points from data and put into array
    #find index of user data points
    #for x, y in zip(xList, yList):
     #   if(x == int(setPointx1))
    #        x1Index = xList[x]
     #       y1Index = yList[y]
    
    #indexX1 = xList.index(setPointx1)
    #indexX2 = xList.index(setPointx2)

    xxList = xList[:]
    yyList = yList[:]
    xxList = xxList[::-1]
    yyList = yyList[::-1]
    # for i in xList:
    #     if i>entryX1:
    #         indexX1 = i
    #         print(indexX1)
    #         print("one")
    #     if i>entryX2:
    #         indexX2 = i
    #         print(indexX2)
    #         print("two")
    #         break
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
    #Calculate linear regression
    #fit = np.polyfit(croppedListXFinal, croppedListYFinal, 1)
    #fit_fn = np.poly1d(fit)
    #Plot the linear Regression
    #a.plot(croppedListXFinal, np.polyval(fit,croppedListXFinal), 'r-')
    linearRegFlag=True
        
class SimpleMode(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        
        #tk.frame.config(bg="white")
        
        #latrobeIcon = Image.open("latrobeicon.jpg")
        #latrobeShowImage = ImageTk.PhotoImage(latrobeIcon)

        #latrobeLabel = tk.label(self, image=latrobeShowImage)
        #latrobeLabel.place(x=0, y=0)

        def updatePlot():
            a.plot(xCoords, yCoords)
            canvas.draw()

        def getVoltage():
            upVolt = upperScale.get()
            lowVolt = lowerScale.get()
        
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
        #canvas.get_tk_widget().grid(column=1, row=2)
        canvas.get_tk_widget().place(y=40, x=60)
        #toolbar = NavigationToolbar2Tk(canvas, self)
        #toolbar.update()
        #canvas._tkcanvas.grid(row=2, column=1)
        #canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        seperationLabel = tk.Label(self, background="black")
        seperationLabel.place(x=500, y=0, height=480, width=5)
        x1Label = tk.Label(self, text="X1 Value")
        x1Label.place(x=515, y=60)
        x2Label = tk.Label(self, text="X2 Value")
        x2Label.place(x=515, y=100)
        entryX1 = ttk.Entry(self)
        #entryX1.grid(column=3, row = 2)
        entryX1.place(x=510, y=80)
        entryX2 = ttk.Entry(self)
        #entryX2.grid(column=2, row = 2, pady=5)
        entryX2.place(x=510, y=120)
        setLinearRegressionButton = ttk.Button(self, text="Line Reg", command=lambda: getLinearParameters(float(entryX1.get()),float(entryX2.get())))
        # ^ holy brackets batman!
        #setLinearRegressionButton.grid(column=3, row=5)
        setLinearRegressionButton.place(x=510, y=160)
        buttonExpertMode = ttk.Button(self, text="Expert", command=lambda: controller.show_frame(ExpertMode))
        #buttonExpertMode.grid(column=3, row=1)
        buttonExpertMode.place(x=50, y=445, width = 60)
        calibrateButton = ttk.Button(self, text="Load Data", command=lambda: testEngine.dummy())
        #calibrateButton.grid(column=3, row=6)
        calibrateButton.place(x=510, y=200)

        #Sliders for Upper/Lower voltage bounds
        scaleLabelUpper = tk.Label(self, text="Upper Voltage")
        scaleLabelUpper.place(x=640, y=60)
        scaleLabelLower = tk.Label(self, text="Lower Voltage")
        scaleLabelLower.place(x=640, y=110)

        upperScale = Scale(self, from_=-2, to=2, orient=HORIZONTAL, resolution=0.1)
        upperScale.place(x=600, y=90)
        lowerScale = Scale(self, from_=-20, to=20, orient=HORIZONTAL, resolution=0.1)
        lowerScale.place(x=600, y=140)

        voltButton = ttk.Button(self, text="get Voltages", command=getVoltage)
        voltButton.place(x=600, y=170)

        # Connect & calibrate button
        conButton = ttk.Button(self, text="Initialise CV", command=lambda: testEngine.cv())
        conButton.place(x=510, y=240)

        cid = f.canvas.mpl_connect('button_press_event', onclick)
        # lukes new regression stuff here

        
        
        
        
        
        


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

class UploadData(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        #label = tk.Label(self, text="Potentio Stat", font=LARGE_FONT)
        #label.pack(pady=10,padx=10)
        
        #f = Figure(figsize=(5,5), dpi = 100)
        #a = f.add_subplot(111)
        #a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

        #canvas = FigureCanvasTkAgg(f, self)
        #canvas.draw()
        #canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        #button1 = ttk.Button(self, text="Calibrate and go")
        #button1.pack()

class Test1Mode(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Potentio Stat", font=LARGE_FONT)
        label.grid(column=1, row=1)
        
        

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=2, row=2)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.grid(column=2, row=2)

        button1 = ttk.Button(self, text="Calibrate and go")
        button1.grid(column=3, row=3)



app = Deploy()
ani = animation.FuncAnimation(f, testAnimate, interval=200)
app.geometry("800x480")
#app.attributes("-zoomed", True)
app.mainloop()



