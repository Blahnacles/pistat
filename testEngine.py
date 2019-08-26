import deviceConfig as dc
import time
import threading

# Initialise the piStat object
piStat = dc.ToolBox(dc.UsbStat(),dc.GraphData(), debugFlag=True)
devLock = threading.Lock()

def actionThread():
    while 1:
        time.sleep(piStat.testAction(devLock))

def dToggle():
    if piStat.state == dc.States.Demo1:
        piStat.state = dc.States.IdleInit
    elif piStat.state == dc.States.Demo2:
        piStat.state = dc.States.Demo1

def dummy():
    piStat.state == dc.States.Idle
    devLock.acquire()
    piStat.potData.loadData("dummyData.csv")
    devLock.release()

def getData():
    devLock.acquire()
    potentialData = piStat.potData.potentialData
    currentData = piStat.potData.currentData
    devLock.release()
    return potentialData, currentData

# Create the daemon thread (exits when main thread exits)
deviceThread = threading.Thread(target=actionThread,name='deviceThread', daemon=True)
# Start the daemon thread
deviceThread.start()