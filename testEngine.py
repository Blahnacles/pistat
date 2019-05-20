from pyqtgraph.Qt import QtCore, QtGui
import deviceConfig as dc
import time
import threading

# Initialise the piStat object
piStat = dc.ToolBox(dc.UsbStat(),dc.GraphData(), debugFlag=True)
devLock = threading.Lock()

def actionThread():
    while 1:
        time.sleep(0.1)
        with devLock:
            piStat.action()

def dToggle():
    if piStat.state == dc.States.Demo1:
        piStat.state = dc.States.Demo2
    elif piStat.state == dc.States.Demo2:
        piStat.state = dc.States.Demo1

# Create the daemon thread (exits when main thread exits)
deviceThread = threading.Thread(target=actionThread,name='deviceThread', daemon=True)
# Start the daemon thread
deviceThread.start()