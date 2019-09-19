import usb.core, usb.util
import numpy as np
import collections
import random
from pyqtgraph.Qt import QtCore, QtGui
from time import sleep
from datetime import datetime
import pandas
# comment here

class States:
    """
    Named list of states to be used as a simple state machine.
    NotConnected
    IdleInit - state for graph initiation
    Idle - continuous update for graph

    """
    NotConnected, IdleInit, Idle, PDInit, Stationary_Graph, Measuring_CV, CVInit, Measuring_CD, Measuring_Rate, Measuring_PD, Demo1, Demo2, zOffset = range(13)





class GraphData:
    """ Holds data read from the potentiostat """
    def __init__(self):
        self.potentialOffset = 0
        self.currentOffset = 0
        self.rawPotentialData = collections.deque(maxlen=200)
        self.potentialData = collections.deque(maxlen=200)
        self.rawCurrentData = collections.deque(maxlen=200)
        self.currentData = collections.deque(maxlen=200)
        self.rawPotentialData.append(0)
        self.rawCurrentData.append(0.5)
        self.currentRange = b'RANGE 1'
        self.timeStamp = None # to hold start time for sweep data
        self.lastTime = None
    def zeroOffset(self):
        """ Set offset values for pot&current, based on the last few values
        To be ran after 30 seconds calibration; see SOP for more information
        Used to be called zero_offset, offset_changed_callback omitted as it
        is a GUI related function."""
        # Screw these two lines, has to be a better way - SBL
        self.potentialOffset = int(round(-np.average(list(self.rawPotentialData))))
        self.currentOffset = int(round(-np.average(list(self.rawCurrentData))))

    def sweepCalc(self, dT, uV, vV, uBound, lBound,rate,cycles):
        """Return the potential after a given time differential along a cv ramp
        dT (s): elapsed time differential, from beginning of scan to current data point
        uV (V): initial voltage
        vV (V): final voltage
        uBound (V): voltage ceiling
        lBound (V): voltage floor
        scanrate (V/s): rate by which the voltage should vary with respect to time
        """
        phase1 = uBound - uV # Potential to traverse in first stage
        phase2 = (uBound-lBound)*2.*cycles
        phase3 = abs(vV-uBound)
        sweepVal = rate*dT
        if sweepVal < phase1: # Have not passed first ramp
            print("phase1, sweepval = ",sweepVal)
            return uV + sweepVal # Therefore simply add the differential to the initial potential
        elif sweepVal < phase1+phase2: # Mid Cycle
            print("phase2, sweepval = ",sweepVal)
            sweepVal -= phase1
            return lBound + abs((sweepVal)%(2*(uBound-lBound))-(uBound-lBound))
        elif sweepVal < phase1+phase2+phase3:
            print("phase3, sweepval = ",sweepVal)
            sweepVal -= phase1 + phase2
            if vV > uBound:
                return uBound + sweepVal
            else:
                return uBound - sweepVal
        else:
            return None
    def clearData(self):
        self.rawPotentialData.clear()
        self.rawCurrentData.clear()
        self.currentData.clear()
        self.potentialData.clear()
        print("data reset!")
    def loadData(self,filename):
        # loads potential/current data from a given .csv file
        try:
            data = pandas.read_csv(filename)
            self.potentialData = data.values[:,0]
            self.currentData = data.values[:,1]
            print("data in "+filename+" successfully loaded, first sample: "+str(data.values[1,1]))
        except Exception as e:
            print(e)

    #def idleInit(self):
    #    """
    #    Prep the graph, initialisation goes here
    #    ends by changing to continous update state.
    #    """
    #    self.state = States.Idle
    
    


    
class ToolBox:
    """Holds generic potentioStat mgmt functionality & data"""
    ### Toolbox - a compilation of PiStat generic functions
    ### Ported SBL 08/05/2019

    def __init__(self, potStat, potData, debugFlag=False):
        self.potStat = potStat
        self.potData = potData
        self.debugFlag = debugFlag
        if(debugFlag):
            self.state = States.Idle
        else:
            self.state = States.NotConnected
        #timer = QtCore.QTimer()
        #timer.timeout.connect(self.action) # call this function
        #timer.start(p) # every p ms
        self.offsetBin = False
        self.params = [-0.2, 0.2, 0.2, -0.2, 0.1, 1]
    def connect_disconnect_usb(self):
        """Toggle device between connected & disconnected
        """
        # Refactored SBL 08/05/2019
        # Returns False if disconnect successful, and True if connect succesful
        # Returns None if connect/disconnect failed
        # DISCONNECT:
        if self.potStat.dev is not None:
            usb.util.dispose_resources(self.potStat.dev)
            self.potStat.dev = None
            self.state = States.NotConnected
            # TODO Device disconnected msg
            return False
        # CONNECT:
        else:
            # Create the device object using the vid & pid
            self.potStat.dev = usb.core.find(idVendor=int(self.potStat.vid, 0), idProduct=int(self.potStat.pid, 0))
            if self.potStat.dev is not None:
                # If connection successful, get info & setup
                # TODO Usb interface connected msg
                try:
                    self.potStat.dac_calibrate()
                    self.potStat.get_dac_settings()
                    print("Settings obtained")
                    self.potStat.setCellStatus(False)
                    print("Cell Set")
                    self.potStat.send_command(b'POTENTIOSTATIC', b'OK')
                    print("Potentiostatic mode")
                    return True
                except ValueError:
                    print("value error")
                    pass # In case device is not yet calibrated

    def dataRead(self):
        potential, current = self.potStat.readPotentialCurrent()
        shuntSel = self.potStat.shuntSelector
        sc = self.potStat.shunt_calibration[shuntSel]
        potential = (potential - self.potData.potentialOffset)/2097152.*8.
        current = (current -self.potData.currentOffset)/2097152.*25./(sc*100.**shuntSel)
        # TODO DELETE THIS
        # THIS IS BAD PRACTICE
        # COMPENSATING FOR TEAMS-219, REMOVE THIS LINE IF THE BUG HAS BEEN FIXED
        # LIKELY CAUSE IS MISCALCULATION OF UNDERFLOW IN twoCompDec
        if potential<-8:
            potential+=16
        # YEAH THAT BLOCK ABOVE. SHOULD NOT BE THERE - Simon Laffan 2019/09/15
        print("v =",potential)
        print("i =",current)
        self.potData.rawPotentialData.append(potential)
        self.potData.potentialData.append(potential)
        self.potData.rawCurrentData.append(current)
        if self.potData.currentRange == b'RANGE 3':
            current *= 1e3
        self.potData.currentData.append(current)
        

    def demo1Init(self):
        """Initialises the system for non-device demo data"""
        self.state = States.Demo1

    def action(self,lock):
        """State machine for regular cyclic voltammetry operation. Added 06/08/2019 SBL"""
        s = self.state
        print(s)
        if s == States.IdleInit:
            # IdleInit means a connection to the device has not been made
            if not self.connect_disconnect_usb():
                # If connection fails, try every 5 seconds
                print("error: failed to connect")
                lock.acquire()
                self.state = States.Idle
                lock.release()
            else:
                print("successfully connected - stabilising")
                sleep(5)
                self.potStat.dac_calibrate()
                # debug
                print("entering zero offset state")
                lock.acquire()
                self.state = States.zOffset
                lock.release()
        elif s == States.zOffset:
            # Clear the data sets
            self.potData.clearData()
            # read 20 times for reliable offset values
            # TODO confirm 20 is enough for reliability
            for i in range(20):
                lock.acquire()
                self.dataRead()
                lock.release()
                sleep(0.1)
            self.potData.zeroOffset()
            print("zoffset returned a poffset of ",self.potData.potentialOffset,"and a coffset of",self.potData.currentOffset)
            self.potStat.potential_offset = self.potData.potentialOffset
            # sanitise data once again, to prepare for current ranging
            self.potData.clearData()
            for i in range(20):
                # read 20 times for reliable current ranging
                lock.acquire()
                self.dataRead()
                lock.release()
                sleep(0.1)
            # set current range, & finally sanitise data
            self.autoRange()
            self.potData.clearData()
            # enter idle data reading stage
            # debug
            print("Entering CV initialisation state")
            lock.acquire()
            self.state = States.CVInit
            lock.release()
        elif s == States.Idle:
            pass
        elif s == States.CVInit:
            self.potStat.vOutput(value=-0.4) # setting the starting potential
            self.potStat.send_command(b'POTENTIOSTATIC', b'OK') # potentiostatic mode set
            self.potData.currentRange = b'RANGE 1' # set highest current range - should be 1 by default anyway
            self.potStat.setCellStatus(True) # Cell on
            for j in range(3):
                for i in range(20):
                    lock.acquire()
                    self.dataRead() # 20 reads
                    lock.release()
                    sleep(0.1)
                self.autoRange() # autorange after 20 reads
                self.potData.clearData() # clear data, complete 3 times
            # debug
            print("Entering CV measurement phase - ramp, two cycles")
            lock.acquire()
            self.state = States.Measuring_CV
            lock.release()
            self.potData.timeStamp = datetime.now()
            self.potData.lastTime= datetime.now()
            print(self.potData.currentRange)
            print(self.potData.potentialOffset)
            print(self.potData.currentOffset)
        elif s == States.Measuring_CV:
            dT = datetime.now() - self.potData.lastTime # time differential as datetime obj
            dT = dT.seconds + dT.microseconds * 1e-6 # seconds elapsed, as float
            lock.acquire() # avoid collisions with gui
            uV = self.params[0] # get params for sweepCalc
            vV = self.params[1]
            uBound = self.params[2]
            lBound = self.params[3]
            rate = self.params[4]
            cycles = self.params[5]
            lock.release()
            voltage = self.potData.sweepCalc(dT, uV, vV, uBound, lBound, rate, cycles)
            print("Current voltage input:",voltage)
            if voltage == None:
                print("Commencing Deposition")
                self.potData.clearData()
                self.potData.timeStamp = datetime.now()
                self.potData.lastTime= datetime.now()
                lock.acquire()
                self.state = States.Measuring_CD
                lock.release()
            else:
                self.potStat.vOutput(value=voltage)
                lock.acquire()
                self.dataRead()
                lock.release()
        elif s == States.Measuring_CD:
            lock.acquire() # avoid collisions with gui
            uV = self.params[0] # get params for sweepCalc
            vV = self.params[1]
            uBound = self.params[2]
            lBound = self.params[3]
            rate = self.params[4]
            cycles = self.params[5]
            lock.release()
            dT = datetime.now() - self.potData.lastTime # time differential as datetime obj
            dT = dT.seconds + dT.microseconds * 1e-6 # seconds elapsed, as float
            voltage = self.potData.sweepCalc(dT, uV, vV, uBound, lBound, rate, cycles)
            print("Current voltage input:",voltage)
            if voltage == None:
                print("Device now idle")
                lock.acquire()
                self.state = States.Idle
                lock.release()
            else:
                self.potStat.vOutput(value=voltage)
                lock.acquire()
                self.dataRead()
                lock.release()
        elif s == States.PDInit:
            # initialise device for pulse/deposition
            self.potStat.vOutput()
            self.potData.currentRange = b'RANGE 1' # set highest current range - should be 1 by default anyway
            self.potStat.setCellStatus(True) # cell on
            self.potStat.send_command(b'POTENTIOSTATIC', b'OK') # potentiostatic mode set
            for j in range(2):
                for i in range(20):
                    lock.acquire()
                    self.dataRead() # 20 reads
                    lock.release()
                    sleep(0.1)
                self.autoRange() # autorange based on 20 reads, then clear data
                self.potData.clearData()
            lock.acquire()
            self.state = States.Measuring_PD # enter measurement state
            lock.release()
        elif s == States.Demo1:
            lock.acquire()
            self.potData.loadData("dummyData.csv")
            print("data read from .csv")
            self.state = States.Idle
            lock.release()
        return 0.1
        
        












    def testAction(self,lock):
        """demo action function, changed from action to testAction 06/08/2019
        defunct in future release, new demo to be made for completed UI
        returns time to sleep for"""
        # Why doesnt this language implement switch-case????    
        s = self.state
        if s == States.Demo1:
            self.demo1DataRead()
            return 0.2
        elif s == States.IdleInit:
            self.connect_disconnect_usb()
            print("idleinit")
            self.state = States.zOffset    
        elif s == States.zOffset:
            # do 50 reads, then offset data
            if len(self.potData.rawCurrentData) < 150:
                self.dataRead()
            else:
                self.potData.zeroOffset()
                print("------------------------------------------")
                print("Offset Buffer - Voltage",self.potData.potentialOffset,"Current",self.potData.currentOffset)
                print("------------------------------------------")
                self.state = States.Demo2
                self.offsetBin = True
                # Turn cell on after offset created
                self.potStat.setCellStatus(True)
                # Reset data sets
                self.potData.rawCurrentData.clear()
                self.potData.rawPotentialData.clear()
        elif s == States.Demo2:
            self.dataRead()
        elif s == States.Idle:
            self.dataRead()
        elif s == States.NotConnected:
            return 0
        return 0.1


    def demo1DataRead(self):
        """Adds 1 pseudo-random datapoint when called"""
        #potential = 1e-100*random.randint(0,100)
        if self.potData.rawPotentialData[-1] <=200:
            current = self.potData.rawCurrentData[-1] + 1e-2*random.randint(-10,10)
            if current <0 or current > 1:
                current = self.potData.rawCurrentData[-1]
            potential = self.potData.rawPotentialData[-1] + 1
            self.potData.rawPotentialData.append(potential)
            self.potData.rawCurrentData.append(current)
        else:
            self.state = States.NotConnected

    def getData(self):
        """Returns plottable data"""
        return self.potData.rawPotentialData, self.potData.rawCurrentData
    
    def autoRange(self):
        """Uses a selected sample of data to determine an appropriate current range
        from the values: 2uA, 200uA & 20mA.
        Then uses this value to set the desired shunt resistor,
        and format the data."""
        size = len(self.potData.rawCurrentData)
        iVals = list(self.potData.rawCurrentData)[size-20:size]
        iMean = abs(sum(iVals)/size)
        if iMean <= 0.002:
            # 2uA range - RANGE 1
            cRange = b'RANGE 1'
        elif iMean <= 0.2:
            # 200uA range - RANGE 2
            cRange = b'RANGE 2'
        else:
            # 20mA range - RANGE 3
            cRange = b'RANGE 3'
        # The more I type range, the less it seems like a word
        # range range range range range
        # set range within data object
        self.potData.currentRange = cRange
        # change current range setting on hardware
        self.potStat.send_command(cRange, b'OK')

        
        



class UsbStat:
    """Contains PotentioStat configuration settings"""
    def __init__(self):
        """Initialise the system variables"""
        self.dev = None # usb device object for the pStat
        self.vid = "0xa0a0"
        self.pid = "0x0002"
        # The following are set by get_dac_settings from dev flash memory
        #TODO set defaults
        self.dac_offset = None
        self.dac_gain = None
        self.potential_offset = 0
        self.current_offset = 0
        # Fine adjustment for shunt resistors - R1/10ohm, R2/1kohm, R3/100kohm
        self.shunt_calibration = [1.,1.,1.]
        self.timeStamp = None
        self.shuntSelector = 0
        self.fwdPotential = 1 # in volts
        self.startPot = -0.4

    #######################################
    ######## Calibration functions ########
    #######################################
    def get_dac_settings(self):
        """Retrieve DAC calibration values from the device's flash memory.
        Then, retrieve dac offset values from the device's flash memory.
        
        Adapted and combined from get_dac_calibration(), get_offset() and 
        get_shunt_calibration()"""

        # Reading settings from device
        if self.dev is not None:
            ##### Getting dac offset & gain
            self.flashRead(b'DACCALGET')
            #### Getting potential & current offset
            self.flashRead(b'OFFSETREAD')
            #### Getting shunt calibration
            self.flashRead(b'SHUNTCALREAD')
    
    def dac_calibrate(self):
        """Activate the automatic DAC1220 calibration function and retrieve the results."""
        self.send_command(b'DACCAL', b'OK')
        self.get_dac_settings()
        # realistically only need dac_offset & dac_gain from the above
        # Not worth optimising for in alpha, as it increases cyc complexity by a lot

    ########################################
    ######## Input/Output functions ########
    ########################################
    def send_command(self, command_string, expected_response):
        """Send a command string to the USB device and check the response
            Returns True if command was properly received, returns False
            if not connected or command rejected by device."""
        if self.dev is not None:
            ######## BEGIN DEVICE ACCESS
            self.dev.write(0x01, command_string) # 0x01 = write address of EP1
            response = bytes(self.dev.read(0x81,64)) # 0x81 = read address of EP1
            ######## END DEVICE ACCESS
            if response == expected_response:
                return True
        return False

    def flashRead(self, designator):
        output = []
        self.dev.write(0x01, designator)
        response = bytes(self.dev.read(0x81,64))
        if response == bytes([255,255,255,255,255,255]):
            print("No response for ",designator)
        elif designator == b'SHUNTCALREAD':
            for i in range(0,3):
                temp = response[2*i:2*i+2]
                r = float(2**8*temp[0]+temp[1] -2**15)
                self.shunt_calibration[i] = 1.+r/1e6
        else:
            res = response[0:3]
            a = (2**12*res[0]+2**4*res[1]+res[2]/2**4) - 2**19
            res = response[3:6]
            b = (2**12*res[0]+2**4*res[1]+res[2]/2**4) - 2**19
            if designator == b'DACCALGET':
                self.dac_offset = a
                self.dac_gain = b
            elif designator == b'OFFSETREAD':
                self.potential_offset = a
                self.current_offset = b
                print("poffset:",a,"coffset",b)

    def setCellStatus(self, cell_on_boolean):
        """Switch the cell connection (True = cell on, False = cell off)."""
        if cell_on_boolean:
            self.send_command(b'CELL ON', b'OK')
        else:
            self.send_command(b'CELL OFF', b'OK')

    def readPotentialCurrent(self):
        """
        Collect data from the potentiostat.
        wait_for_adc_read() omitted, as it is explicitly for windows system timing
        Returns raw potential, and raw current.
        """
        def twoCompDec(msb, midb, lsb):
            """Converts 2s complement to decimal. Now with vastly improved logic"""
            combined_value = (msb%64)*2**16+midb*2**8+lsb # Get rid of overflow bits
            ovh = (msb > 63) and (msb < 128) # Check for Theoverflow high (B22 set)
            ovl = (msb > 127) # Check for overflow low (B23 set)
            print("----new read: ovh =",ovh,"ovl =",ovl,"combined value =",combined_value)
            if ovl or not ovh:
                return (combined_value - 2**22)
            else:
                return combined_value

        ######## BEGIN DEVICE ACCESS
        self.dev.write(0x01,b'ADCREAD') # 0x01 = write address of EP1
        msg = bytes(self.dev.read(0x81,64)) # 0x81 = read address of EP1
        ######## END DEVICE ACCESS
        if msg != b'WAIT': # 'WAIT' is received if a conversion has not yet finished
            p = twoCompDec(msg[0], msg[1], msg[2]) # raw potential
            i = twoCompDec(msg[3], msg[4], msg[5]) # raw current
            return p,i
        return None, None
    def vOutput(self, value=1):
        print("poffset:",self.potential_offset)
        self.send_command(b'DACSET '+self.ddb(value/8.*2.**19+int(round(self.potential_offset/4.))),b'OK')

    def ddb(self,v):
        # TODO make it pretty
        code = 2**19 + int(round(v)) # Convert the (signed) input value to an unsigned 20-bit integer with zero at midway
        code = np.clip(code, 0, 2**20 - 1) # If the input exceeds the boundaries of the 20-bit integer, clip it
        byte1 = code // 2**12
        byte2 = (code % 2**12) // 2**4
        byte3 = (code - byte1*2**12 - byte2*2**4)*2**4
        return bytes([byte1,byte2,byte3])