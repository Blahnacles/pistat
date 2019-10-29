"""
TEAMS CSE3PRB
PiStat - Minituarised PotentioStat
Team members:
    Luke Gidley - 18089236; Simon Laffan 18774937; Keenan Saleh - 19529401;
    Kush Shah - 19548278; Rihtvik Sharma - 18851514
deviceConfig.py manages connection with the potentiostat through usb. 
takes commands from the testEngine to manage this connection, run cyclic voltammetry,
and set parameters on the device. Also manages data storage and access.

The methods provided are executed by the gui, through user interaction
Instantiates a piStat object, and executes a daemon thread to contain it.
Daemon thread exits when gui exits.
devLock provides syncronisation with gui and engine
"""
import deviceConfig as dc
import time
import threading

# Initialise the piStat object
piStat = dc.ToolBox(dc.UsbStat(),dc.GraphData(), debugFlag=True)
devLock = threading.Lock() # Lock to sync access to low level config data, and measurement data

def actionThread():
    """Simple function to begin the action loop/state machine
    Should be run within a thread object"""
    while 1:
        time.sleep(piStat.action(devLock))

def connectDisconnect():
    """Establish or destroy connection with the device"""
    devLock.acquire()
    piStat.state = dc.States.IdleInit
    devLock.release()
    time.sleep(1)
    return piStat.potStat.dev is not None

def saveCsv(filename):
    """Helper function for potData
    Saves the data in a given file
    Author: Simon Laffan"""
    piStat.potData.saveData(filename,piStat.params)
    
def getState():
    """Return state enum value
    Synchronised with device thread
    can therefore be run concurrently with actionThread"""
    devLock.acquire()
    s = piStat.state
    devLock.release()
    return s

def dummy():
    """Populate graph with dummy data from .csv"""
    devLock.acquire()
    piStat.state = dc.States.Demo1
    devLock.release()

def cv():
    """If device connected, begin cyclic voltammetry
    Author: Simon Laffan"""
    # Must lock when changing state
    devLock.acquire()
    if piStat.potStat.dev is not None:
        piStat.state = dc.States.CVInit
    devLock.release()
    return piStat.potStat.dev is not None

def cvCancel():
    """Immediately cancels the piStat, sends it into idle mode
    Author: Simon Laffan"""
    devLock.acquire()
    piStat.state = dc.States.Idle
    devLock.release()


def depositionData():
	"""return the deposition data, or to return an
	appropriate error/exception
	if the data is not yet available.
    Author: Simon Laffan"""
	
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
    """Author - Simon Laffan"""
    devLock.acquire()
    piStat.params[2] = vHigh
    piStat.params[3] = vLow
    # Unit test
    b=piStat.params[2]
    a=piStat.params[3]
    devLock.release()
    return a,b

def setPeak(height):
    """Assigns a value to be saved for the peak height
    Author: Simon Laffan"""
    piStat.potData.peakHeight = height
# Create the daemon thread (exits when main thread exits)
deviceThread = threading.Thread(target=actionThread,name='deviceThread', daemon=True)
# Start the daemon thread
deviceThread.start()