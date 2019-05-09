import usb.core, usb.util

class States:
    """Expose a named list of states to be used as a simple state machine."""
    NotConnected, Idle_Init, Idle, Measuring_Offset, Stationary_Graph, Measuring_CV, Measuring_CD, Measuring_Rate, Measuring_PD = range(9)

class ToolBox:
    """Holds generic potentioStat mgmt functionality & data"""
    ### Toolbox - a compilation of PiStat generic functions
    ### Ported SBL 08/05/2019

    def connect_disconnect_usb(self, potStat):
        """Toggle device between connected & disconnected
        """
        # Refactored SBL 08/05/2019
        # Returns False if disconnect successful, and True if connect succesful
        # Returns None if connect/disconnect failed
        # DISCONNECT:
        if potStat.dev is not None:
            usb.util.dispose_resources(potStat.dev)
            potStat.dev = None
            potStat.state = States.NotConnected
            # TODO Device disconnected msg
            return False
        # CONNECT:
        else:
            # Create the device object using the vid & pid
            potStat.dev = usb.core.find(idVendor=int(potStat.vid, 0), idProduct=int(potStat.pid, 0))
            if potStat.dev is not None:
                # If connection successful, get info & setup
                # TODO Usb interface connected msg
                try:
                    potStat.get_dac_settings()
                    potStat.set_cell_status(False)
                    return True
                except ValueError:
                    pass # In case device is not yet calibrated


class UsbStat:
    """Contains PotentioStat configuration settings"""
    dev = None # usb device object for the pStat
    vid = "0xa0a0"
    pid = "0x0002"
    dev = None
    state = States.NotConnected
    # The following are set by get_dac_settings from dev flash memory
    #TODO set defaults
    dac_offset = None
    dac_gain = None
    potential_offset = None
    current_offset = None
    # Fine adjustment for shunt resistors - R1/10ohm, R2/1kohm, R3/100kohm
    shunt_calibration = [1.,1.,1.]
    

    def __init__(self):
        """Initialise the system variables"""
        self.dev = None
        self.state = States.NotConnected

    #######################################
    ######## Calibration functions ########
    #######################################
    def get_dac_settings(self):
        """Retrieve DAC calibration values from the device's flash memory.
        Then, retrieve dac offset values from the device's flash memory.
        
        Adapted and combined from get_dac_calibration(), get_offset() and 
        get_shunt_calibration()"""

        ################################
        # Reading settings from device #
        ################################
        if self.dev is not None:
            ##### Getting dac offset & gain
            dOffset, dGain = self.flashRead(b'DACCALGET')
            #### Getting potential & current offset
            self.dev.write(0x01,b'OFFSETREAD') # 0x01 = write address of EP1
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
            self.dev.write(0x01, command_string) # 0x01 = write address of EP1
            response = bytes(self.dev.read(0x81,64)) # 0x81 = read address of EP1
            if response == expected_response:
                return True
        return False

    def flashRead(self, designator):
        shunt_calibration = [1.,1.,1.]
        output = []
        if designator == b'SHUNTCALREAD':
            # shunt calibration read has a different return type
            self.dev.write(0x01, designator)
            response = bytes(self.dev.read(0x81,64)) # 0x81 = read address of EP1
            if response != bytes([255,255,255,255,255,255]): # If no calibration value has been stored, all bits are set
                for i in range(0,3):
                    temp = response[2*i:2*i+2]
                    r = float(2**8*temp[0]+temp[1] - 2**15)
                    shunt_calibration[i] = 1.+r/1e6 # Yields an adjustment range from 0.967 to 1.033 in steps of 1 ppm
            return shunt_calibration
        output[0] = None
        output[1] = None
        self.dev.write(0x01,designator) # 0x01 = write address of EP1
        response = bytes(self.dev.read(0x81,64)) # 0x81 = write address of EP1
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
