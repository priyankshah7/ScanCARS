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
        # 0: Single Scan
        # 1: Accumulate
        # 2: Kinetics
        # 3: Fast Kinetics
        # 4: Run till abort

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

