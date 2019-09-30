import deviceConfig as dc
import time
import threading

# Initialise the piStat object
piStat = dc.ToolBox(dc.UsbStat(),dc.GraphData(), debugFlag=True)
devLock = threading.Lock()

def actionThread():
    while 1:
        time.sleep(piStat.action(devLock))

def dToggle():
    if piStat.state == dc.States.Demo1:
        lock.acquire()
        piStat.state = dc.States.IdleInit
        lock.release()
    elif piStat.state == dc.States.Demo2:
        lock.acquire()
        piStat.state = dc.States.Demo1
        lock.release()

def dummy():
    piStat.state = dc.States.Demo1
    print(piStat.state)

def cv():
    # Must lock when changing state
    devLock.acquire()
    piStat.state = dc.States.IdleInit
    devLock.release()

def depositionData():
	"""return the deposition data, or to return an
	appropriate error/exception
	if the data is not yet available."""
	
	devLock.acquire()
	params, v, i = dc.saveArrays()
	devLock.release()
	
	return v, i

def getData():
    devLock.acquire()
    potentialData = piStat.potData.potentialData
    currentData = piStat.potData.currentData
    devLock.release()
    return potentialData, currentData

def setVoltage(vLow, vHigh):
    piStat.params[2] = vHigh
    piStat.params[3] = vLow
# Create the daemon thread (exits when main thread exits)
deviceThread = threading.Thread(target=actionThread,name='deviceThread', daemon=True)
# Start the daemon thread
deviceThread.start()