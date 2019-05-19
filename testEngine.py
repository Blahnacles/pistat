from pyqtgraph.Qt import QtCore, QtGui
import deviceConfig as dc
import timeit
import time

#p = 1e3*0.09 # read every 90 ms
p = 1e3*1 # read every second
psec = 1
firstRead = timeit.default_timer()
lastRead = firstRead
tSum = lastRead

# Initialise the piStat object
piStat = dc.ToolBox(dc.UsbStat(),dc.GraphData(), debugFlag=True)

# For the non-hardware test, no connection or reading from the dac is required.
piStat.demo1Init()

#timer = QtCore.QTimer()
#timer.timeout.connect(printDemo, piStat) # call this function
#timer.start(10000) # every p ms


