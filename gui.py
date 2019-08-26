import testEngine
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import timeit
import time
LARGE_FONT= ("Verdana", 12)

style.use("ggplot")

f = Figure(figsize=(3,2.25), dpi = 100)
a = f.add_subplot(111)
xList = []
yList = []


#p = 1e3*0.09 # read every 90 ms
p = 1e3*1 # read every second
psec = 1
firstRead = timeit.default_timer()
lastRead = firstRead
tSum = lastRead
ani = None
stop = False


def testAnimate(i):
    global stop
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
        stop = True
    elif testEngine.piStat.state==testEngine.dc.States.Idle:
        a.plot(xList, yList)
    else:
        a.plot(xList)
        a.plot(yList)
    if stop:
        time.sleep(5)

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

def getLinearParameters():
    #Get data from entry boxes
    setPointxy1 = entryXY1.get()
    setPointxy2 = entryXY2.get()
        
    #Split point data into X and Y
    x1,y1 = setPointxy1.split(',')
    x2,y2 = setPointxy2.split(',')

    #create array points from data and put into array
    x = [int(x1), int(x2)]
    y = [int(y1), int(y2)]
    #find index of user data points
    # for x, y in zip(xList, yList):
    #     if(x == int(x1) and y == int(y1)
    #         x1Index = xList[x]
    #         y1Index = yList[y]

            # for x, y in zip(xList, yList):
            #     if(x == int(x2) and y == int(y2)
            #         x2Index = xList.index(x)
            #         y2Index = yList.index(y)
                   
    #crop list of data to remove peak for X
    croppedListX1 = xList[0:x1Index]
    croppedListX2 = xList[x2Index:]
    #Append lists for X
    croppedListXfinal = croppedListX1 + croppedListX2
    #crop list of data to remove peak for Y
    croppedListY1 = yList[0:y1Index]
    croppedListY2 = yList[y2Index:]
    #Append data for Y
    croppedListYFinal = croppedListY1 + croppedListY2
    #Calculate linear regression
    fit = np.polyfit(x, y, 1)
    #fit_fn = np.poly1d(fit)
    #Plot the linear Regression
    a.plot(x, polyval(fit,x), 'r-')
        
class SimpleMode(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="PotentioStat", font=LARGE_FONT)
        label.grid(column=1, row=1)
        
        colourLabelY = tk.Label(self, background="#326ada", width=5, height=16)
        colourLabelY.grid(column=0)

        colourLabelX = tk.Label(self, background="#326ada", width=54, height=2)
        colourLabelX.grid(column=1, row=4)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=1)

        #toolbar = NavigationToolbar2Tk(canvas, self)
        #toolbar.update()
        #canvas._tkcanvas.grid(row=2, column=1)
        #canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        buttonExpertMode = ttk.Button(self, text="Expert Mode", command=lambda: controller.show_frame(ExpertMode))
        buttonExpertMode.grid(column=3, row=1)
        calibrateButton = ttk.Button(self, text="Toggle Demo", command=lambda: testEngine.dummy())
        calibrateButton.grid(column=3, row=4)


        # lukes new regression stuff here
        setLinearRegressionButton = ttk.Button(self, text="Apply Linear Regression", command=getLinearParameters)
        setLinearRegressionButton.grid(column=2, row=4)
        
        entryXY1 = ttk.Entry(self)
        entryXY1.grid(column=3, row = 2)
          
        entryXY2 = ttk.Entry(self)
        entryXY2.grid(column=3, row = 3)
        
        
        
        
        


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
ani = animation.FuncAnimation(f, testAnimate, interval=1)
app.geometry("500x300")
app.mainloop()



