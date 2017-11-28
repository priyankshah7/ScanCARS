import platform
from ctypes import *
from PIL import Image
import sys


ERROR_CODE = {
    20001: "DRV_ERROR_CODES",
    20002: "DRV_SUCCESS",
    20003: "DRV_VXNOTINSTALLED",
    20006: "DRV_ERROR_FILELOAD",
    20007: "DRV_ERROR_VXD_INIT",
    20010: "DRV_ERROR_PAGELOCK",
    20011: "DRV_ERROR_PAGE_UNLOCK",
    20013: "DRV_ERROR_ACK",
    20024: "DRV_NO_NEW_DATA",
    20026: "DRV_SPOOLERROR",
    20034: "DRV_TEMP_OFF",
    20035: "DRV_TEMP_NOT_STABILIZED",
    20036: "DRV_TEMP_STABILIZED",
    20037: "DRV_TEMP_NOT_REACHED",
    20038: "DRV_TEMP_OUT_RANGE",
    20039: "DRV_TEMP_NOT_SUPPORTED",
    20040: "DRV_TEMP_DRIFT",
    20050: "DRV_COF_NOTLOADED",
    20053: "DRV_FLEXERROR",
    20066: "DRV_P1INVALID",
    20067: "DRV_P2INVALID",
    20068: "DRV_P3INVALID",
    20069: "DRV_P4INVALID",
    20070: "DRV_INIERROR",
    20071: "DRV_COERROR",
    20072: "DRV_ACQUIRING",
    20073: "DRV_IDLE",
    20074: "DRV_TEMPCYCLE",
    20075: "DRV_NOT_INITIALIZED",
    20076: "DRV_P5INVALID",
    20077: "DRV_P6INVALID",
    20083: "P7_INVALID",
    20089: "DRV_USBERROR",
    20091: "DRV_NOT_SUPPORTED",
    20095: "DRV_INVALID_TRIGGER_MODE",
    20099: "DRV_BINNING_ERROR",
    20990: "DRV_NOCAMERA",
    20991: "DRV_NOT_SUPPORTED",
    20992: "DRV_NOT_AVAILABLE"
}

class Andor:
    def __init__(self):
        # Loading the Andor dll driver
        self.dll = cdll.LoadLibrary("C:\\Program Files\\Andor SOLIS\\Drivers\\atmcd64d")

        cw = c_int()
        ch = c_int()

        self.dll.GetDetector(byref(cw), byref(ch))

    def __del__(self):
        error = self.dll.ShutDown()

    def Initialize(self):
        tekst = c_char()
        error = self.dll.Initialize(byref(tekst))

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            return 'Andor: camera initialized.'

        elif ERROR_CODE[error] == 'DRV_INIERROR':
            return 'Andor: error. Unable to load DETECTOR.INI'

        elif ERROR_CODE[error] == 'DRV_ERROR_ACK':
            return 'Andor: error. Unable to communicate with card.'

        elif ERROR_CODE[error] == 'DRV_USBERROR':
            return 'Andor: error. Unable to detect USB device or not USB 2.0'

        elif ERROR_CODE[error] == 'DRV_ERROR_NOCAMERA':
            return 'Andor: error. No camera found.'

        elif ERROR_CODE[error] == 'DRV_ERROR_PAGELOCK':
            return 'Andor: error. Unable to acquire lock on requested memory.'

        else:
            return 'Andor: error. Unknown error.'

    def CoolerON(self):
        error = self.dll.CoolerON()

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            return 'Andor: Cooler on.'

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: CoolerOn error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: CoolerOn error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_ERROR_ACK':
            return 'Andor: CoolerOn error. Unable to communicate with card.'

    def CoolerOFF(self):
        error = self.dll.CoolerOFF()

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            return 'Andor: Temperature controller switched OFF.'

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: CoolerOFF error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: CoolerOFF error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_ERROR_ACK':
            return 'Andor: CoolerOFF error. Unable to communicate with card.'

        elif ERROR_CODE[error] == 'DRV_NOT_SUPPORTED':
            return 'Andor: CoolerOFF error. Camera does not support switching cooler off.'

    def SetTemperature(self, temp):
        """
        :param temp:
        :return: error message(string)

        This function will set the desired temperature of the detector. To turn
        cooling ON and OFF use the CoolerON and CoolerOFF functions
        """
        error = self.dll.SetTemperature(temp)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetTemperature error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetTemperature error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_ERROR_ACK':
            return 'Andor: SetTemperature error. Unable to communicate with card.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetTemperature error. Temperature invalid.'

        elif ERROR_CODE[error] == 'DRV_NOT_SUPPORTED':
            return 'Andor: SetTemperature error. The camera does not support setting the temperature.'

    def ShutDown(self):
        error = self.dll.ShutDown()

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            return 'Andor: camera successfully shutdown.'

    def SetReadMode(self, mode):
        # 0: Full vertical binning
        # 1: multi track
        # 2: random track
        # 3: single track
        # 4: image

        error = self.dll.SetReadMode(mode)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetReadMode error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetReadMode error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetReadMode error. Invalid readout mode passed.'

    def SetAcquisitionMode(self, mode):
        # 1: Single Scan
        # 2: Accumulate
        # 3: Kinetics
        # 4: Fast Kinetics
        # 5: Run till abort

        error = self.dll.SetAcquisitionMode(mode)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetAcquisitionMode error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetAcquisitionMode error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetAcquisitionMode error. Acquisition mode invalid.'

    def SetNumberKinetics(self, numKin):
        """
        :param numKin:
        :return error message(string):

        This function will set the number of scans to be taken during a single
        acquisition sequence. This will only take effect if the acquisition
        mode is Kinetic Series.
        """
        error = self.dll.SetNumberKinetics(numKin)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetNumberKinetics error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetNumberKinetics error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetNumberKinetics error. Number in series invalid.'

    def SetNumberAccumulations(self, number):
        """
        :param number:
        :return error message(string):

        This function will set the number of scans accumulated in memory.
        This will only take effect if the acquisition mode is either
        Accumulate or Kinetic Series.
        """
        error = self.dll.SetNumberKinetics(number)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetNumberAccumulations error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetNumberAccumulations error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetNumberAccumulations error. Number of accumulates.'

    def SetAccumulationCycleTime(self, time):
        """
        :param time:
        :return error message(string):

        This function will set the accumulation cycle time to the nearest
        valid value not less than the given value. The actual cycle time used is
        obtained by GetAcquisitionTimings.
        """
        error = self.dll.SetAccumulationCycleTime(time)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetAccumulationCycleTime error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetAccumulationCycleTime error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetAccumulationCycleTime error. Exposure time invalid.'

    def SetKineticCycleTime(self, time):
        """
        :param time:
        :return error message(string):

         This function will set the kinetic cycle time to the nearest valid value
         not less than the given value. The actual time used is obtained
         by GetAcquisitionTimings.
        """
        error = self.dll.SetKineticCycleTime(time)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetKineticCycleTime error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetKineticCycleTime error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetKineticCycleTime error. Time invalid.'

    def SetShutter(self, type, mode, closingtime, openingtime):
        """
        :param type:
        :param mode:
        :param closingtime:
        :param openingtime:
        :return: error message(string)

        This function controls the behaviour of the shutter.

        int type:
            0: Output TTL low signal to open shutter
            1: Output TTL high signal to open shutter

        int mode:
            0: Fully auto
            1: Permanently open
            2: Permanently closed
            3: Open for FVB series
            4: Open for any series

        int closingtime:
            Time shutter takes to close (ms)

        int openingtime
            Time shutter takes to open (ms)
        """
        error = self.dll.SetShutter(type, mode, closingtime, openingtime)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetShutter error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetShutter error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_ERROR_ACK':
            return 'Andor: SetShutter error. Unable to communicate with card.'

        elif ERROR_CODE[error] == 'DRV_NOT_SUPPORTED':
            return 'Andor: SetShutter error. Camera does not support shutter control'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetShutter error. Invalid TTL type.'

        elif ERROR_CODE[error] == 'DRV_P2INVALID':
            return 'Andor: SetShutter error. Invalid mode.'

        elif ERROR_CODE[error] == 'DRV_P3INVALID':
            return 'Andor: SetShutter error. Invalid time to open.'

        elif ERROR_CODE[error] == 'DRV_P4INVALID':
            return 'Andor: SetShutter error. Invalid time to close.'

    def StartAcquisition(self):
        """
        :return error message(string):

        This function starts an acquisition. The status of the acquisition can
        be monitored via GetStatus().
        """
        error = self.dll.StartAcquisition()

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: StartAcquisition error. System not initialized'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: StartAcquisition error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_VXDNOTINSTALLED':
            return 'Andor: StartAcquisition error. VxD not loaded.'

        elif ERROR_CODE[error] == 'DRV_ERROR_ACK':
            return 'Andor: StartAcquisition error. Unable to communicate with card.'

        elif ERROR_CODE[error] == 'DRV_INIERROR':
            return 'Andor: StartAcquisition error. Error reading DETECTOR.INI'

        elif ERROR_CODE[error] == 'DRV_ACQERROR':
            return 'Andor: StartAcquisition error. Acquisition settings invalid.'

        elif ERROR_CODE[error] == 'DRV_ERROR_PAGELOCK':
            return 'Andor: StartAcquisition error. Unable to allocate memory.'

        elif ERROR_CODE[error] == 'DRV_INVALID_FILTER':
            return 'Andor: StartAcquisition error. Filter not available for current acquisition'

        elif ERROR_CODE[error] == 'DRV_BINNING_ERROR':
            return 'Andor: StartAcquisition error. Range not multiple of horizontal binning.'

        elif ERROR_CODE[error] == 'DRV_SPOOLSETUPERROR':
            return 'Andor: StartAcquisition error. Error with spool settings.'

    def GetAcquiredData(self, imageArray):
        """
        :param imageArray:
        :return:

        This function will return the data from the last acquisition. The data
        are returned as long integers (32bit signed integers). The array must
        be large enough
        """

    def SetExposureTime(self, time):
        """
        :param time:
        :return error message(string):

        This function will set the exposure time to the nearest valid value not
        less than the given value. The actual exposure time is obtained by
        GetAcquisitionTimings().
        """
        error = self.dll.SetExposureTime(c_float(time))

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetExposureTime error. System not initalized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetExposureTime error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetExposureTime error. Exposure time invalid.'

