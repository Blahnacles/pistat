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

f = Figure(figsize=(5,5), dpi = 100)
a = f.add_subplot(111)
xList = []
yList = []


#p = 1e3*0.09 # read every 90 ms
p = 1e3*1 # read every second
psec = 1
firstRead = timeit.default_timer()
lastRead = firstRead
tSum = lastRead


def testAnimate(i):
    xList, yList = testEngine.piStat.getData()
    a.clear()
    a.plot(xList, yList)
    a.axes.set_ylim(0,1)
    a.axes.set_xlim(0,200)


class Deploy(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

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

app.mainloop()



