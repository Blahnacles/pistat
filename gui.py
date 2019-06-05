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


def testAnimate(i):
    xList, yList = testEngine.piStat.getData()
    a.clear()
    if testEngine.piStat.offsetBin:
        # Set the axes once offset has changed
        # set lower limit to 110% of the offset
        #h = 1.1*max(testEngine.piStat.potData.potentialOffset,testEngine.piStat.potData.currentOffset)
        a.axes.set_ylim(-20,2)
        # Reset the offsetBin once it has been checked
        #testEngine.piStat.offsetBin = False
    if testEngine.piStat.state==testEngine.dc.States.Demo1:
        a.plot(xList, yList)
    else:
        SimpleMode
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

        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.frames = {}

        frame = SimpleMode(container, self)

        self.frames[SimpleMode] = frame

        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SimpleMode)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

    @staticmethod
    def testFunction():
        print("Testing!")
        
class SimpleMode(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="PotentioStat", font=LARGE_FONT)
        #label.pack(pady=10,padx=10)
        
        #values of the potential and current

        self.potentialLabel = tk.Label(self, text="0.000", font=LARGE_FONT)
        #potentialLabel.pack(side=LEFT, pady=10, padx=10)
        self.potentialLabel.grid(row=0, column=0)

        currentLabel = tk.Label(self, text="0.000", font=LARGE_FONT)
        #currentLabel.pack(side=LEFT, pady=10, padx=10)
        currentLabel.grid(row=0, column=1)

        #Plotting the Graph

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        #canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        canvas.get_tk_widget().grid(row=2, column=1, columnspan=3, rowspan=6, sticky='ewns')#sticky=E+W+S+N
        #Adding Toolbar to Graph

        #toolbar = NavigationToolbar2Tk(canvas, self)
        #toolbar.update()
        #canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        canvas._tkcanvas.grid(row=5, column=1)
        #Adding Buttons to start functionality

        button2 = ttk.Button(self, text="Toggle Demo", command=testEngine.dToggle)
        #button2.pack(side=RIGHT, padx=5, pady=5)
        button2.grid(row=5, column=4)
        button1 = ttk.Button(self, text="Calibrate and go")
        #button1.pack(side=RIGHT, padx=5, pady=5)
        button1.grid(row=5, column=5)
    
    def labelChange(self,p,i):
        self.potentialLabel.configure(text=p)
        
        
        
        

class ExpertMode(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Potentio Stat", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        f = Figure(figsize=(5,5), dpi = 100)
        a = f.add_subplot(111)
        a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        button1 = ttk.Button(self, text="Calibrate and go")
        button1.pack()
        


class UploadData(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Potentio Stat", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        f = Figure(figsize=(5,5), dpi = 100)
        a = f.add_subplot(111)
        a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        button1 = ttk.Button(self, text="Calibrate and go")
        button1.pack()

class Test1Mode(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Potentio Stat", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        button1 = ttk.Button(self, text="Calibrate and go")
        button1.pack()



app = Deploy()
ani = animation.FuncAnimation(f, testAnimate, interval=1)
app.geometry("500x300")
app.mainloop()



