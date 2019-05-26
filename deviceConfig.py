import usb.core, usb.util
import numpy as np
import collections
import random
from pyqtgraph.Qt import QtCore, QtGui
from time import sleep

class States:
    """
    Named list of states to be used as a simple state machine.
    NotConnected
    IdleInit - state for graph initiation
    Idle - continuous update for graph

    """
    NotConnected, IdleInit, Idle, Measuring_Offset, Stationary_Graph, Measuring_CV, Measuring_CD, Measuring_Rate, Measuring_PD, Demo1, Demo2, zOffset = range(12)





class GraphData:
    """ Holds data read from the potentiostat """
    def __init__(self):
        self.potentialOffset = 0
        self.currentOffset = 0
        self.rawPotentialData = collections.deque(maxlen=200)
        self.rawCurrentData = collections.deque(maxlen=200)
        self.rawPotentialData.append(0)
        self.rawCurrentData.append(0.5)
    def zeroOffset(self):
        """ Set offset values for pot&current, based on the last few values
        To be ran after 30 seconds calibration; see SOP for more information
        Used to be called zero_offset, offset_changed_callback omitted as it
        is a GUI related function."""
        # Fuck these two lines, has to be a better way - SBL
        self.potentialOffset = int(round(np.average(list(self.rawPotentialData))))
        self.currentOffset = int(round(np.average(list(self.rawCurrentData))))

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
            self.demo1Init()
        else:
            self.state = States.NotConnected
        #timer = QtCore.QTimer()
        #timer.timeout.connect(self.action) # call this function
        #timer.start(p) # every p ms
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
                    self.potStat.get_dac_settings()
                    print("Settings obtained")
                    self.potStat.set_cell_status(False)
                    print("Cell Set")
                    return True
                except ValueError:
                    print("value error")
                    pass # In case device is not yet calibrated

    def dataRead(self):
        potential, current = self.potStat.readPotentialCurrent()
        potential -= self.potData.potentialOffset
        current -= self.potData.currentOffset
        print(potential)
        print(current)
        self.potData.rawPotentialData.append(potential)
        self.potData.rawCurrentData.append(current)

    def demo1Init(self):
        """Initialises the system for non-device demo data"""
        self.state = States.Demo1

    def action(self,lock):
        """returns time to sleep for"""
        # Why doesnt this language implement switch-case????    
        s = self.state
        if s == States.Demo1:
            self.demo1DataRead()
            print("Demo1")
            return 0.2
        elif s == States.IdleInit:
            self.connect_disconnect_usb()
            print("idleinit")
            self.state = States.zOffset       
        elif s == States.zOffset:
            # do 50 reads, then offset data
            if len(self.potData.rawCurrentData) < 30:
                self.dataRead()
            else:
                self.potData.zeroOffset()
                print("Offset Buffer - Voltage",self.potData.potentialOffset,"Current",self.potData.currentOffset)
                self.state = States.Demo2
        elif s == States.Demo2:
            # Reset data sets
            self.potData.rawCurrentData = collections.deque(maxlen=200)
            self.potData.rawPotentialData = collections.deque(maxlen=200)
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
        self.potential_offset = None
        self.current_offset = None
        # Fine adjustment for shunt resistors - R1/10ohm, R2/1kohm, R3/100kohm
        self.shunt_calibration = [1.,1.,1.]
        self.timeStamp = None

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
            dOffset, dGain = self.flashRead(b'DACCALGET')
            #### Getting potential & current offset
            pOffset, cOffest = self.flashRead(b'OFFSETREAD')
            #### Getting shunt calibration
            shunt_calibration = self.flashRead(b'SHUNTCALREAD')
            # now set the collected values
            self.dac_offset = dOffset
            self.dac_gain = dGain
            self.potential_offset = pOffset
            self.current_offset = cOffest
            self.shunt_calibration = shunt_calibration
    
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
        shunt_calibration = [1.,1.,1.]
        output = []
        if designator == b'SHUNTCALREAD':
            # shunt calibration read has a different return type
            ######## BEGIN DEVICE ACCESS
            self.dev.write(0x01, designator)
            response = bytes(self.dev.read(0x81,64)) # 0x81 = read address of EP1
            ######## END DEVICE ACCESS
            if response != bytes([255,255,255,255,255,255]): # If no calibration value has been stored, all bits are set
                for i in range(0,3):
                    temp = response[2*i:2*i+2]
                    r = float(2**8*temp[0]+temp[1] - 2**15)
                    shunt_calibration[i] = 1.+r/1e6 # Yields an adjustment range from 0.967 to 1.033 in steps of 1 ppm
            return shunt_calibration
        output.append(None)
        output.append(None)
        ######## BEGIN DEVICE ACCESS
        self.dev.write(0x01,designator) # 0x01 = write address of EP1
        response = bytes(self.dev.read(0x81,64)) # 0x81 = write address of EP1
        ######## END DEVICE ACCESS
        # Check for a stored response within the stat's flash memory
        if response != bytes([255,255,255,255,255,255]):
                res = response[0:3]
                # Just a bytes to decimal conversion
                output[0] = (2**12*res[0]+2**4*res[1]+res[2]/2**4) - 2**19
                res = response[3:6]
                # Just a bytes to decimal conversion
                output[1] = (2**12*res[0]+2**4*res[1]+res[2]/2**4) - 2**19
                # TODO read from flash msg
        else:
            # TODO set defaults when no data is stored
            output
        return output[0], output[1]

    def set_cell_status(self, cell_on_boolean):
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
