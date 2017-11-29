import platform
from ctypes import *
from PIL import Image
import sys


class Andor:
    def __init__(self):
        # Loading the Andor dll driver
        self.dll = cdll.LoadLibrary("C:\\Program Files\\Andor SOLIS\\Drivers\\atmcd64d")

        cw = c_int()
        ch = c_int()

        self.dll.GetDetector(byref(cw), byref(ch))

    def __del__(self):
        error = self.dll.ShutDown()

    # TODO Not including EMCCD functions just yet. Will do so only if required.
    # TODO There are some functions which have additional returns that need to be coded

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

    def GetTemperature(self):
        """
        :return error message(string):

        This function returns the temperature of the detector to the nearest degree.
        It also gives the status of the cooling process.
        """
        temperature = c_int()
        error = self.dll.GetTemperature(temperature)

        if ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: GetTemperature error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: GetTemperature error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_ERROR_ACK':
            return 'Andor: GetTemperature error. Unable to communicate with card.'

        # TODO There are 5 other DRV returns here which give the status of the temp

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

    def GetNumberADChannels(self):
        """
        :return:

        As your Andor SDK system may be capable of operating with more than one
        A-D converter, this function will tell you the number available.
        """
        noChannels = c_int()

        error = self.dll.GetNumberADChannels(noChannels)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

    def SetADChannel(self, channel):
        """
        :param channel:
        :return error message(string):

        This function will set the AD channel to one of the possible A-Ds of the
        system. This AD channel will be used for all subsequent operations
        performed by the system.
        """
        error = self.dll.SetADChannel(channel)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetADChannel error. Index is out of range.'

    def GetBitDepth(self, channel):
        """
        :param channel:
        :return error message(string):

        This function will retrieve the size in bits of the dynamic range for
        any available AD channel.
        """
        bitDepth = c_int

        error = self.dll.GetBitDepth(channel, byref(bitDepth))

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: GetBitDepth error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: GetBitDepth error. Invalid channel.'

    def SetOutputAmplifier(self, type):
        """
        :param type:
        :return error message(string):

        Some EMCCD systems have the capability to use a second output amplifier.
        This function will set the type of output amplifier to be used when
        reading data from the head of these systems.

        int type:
            0: Standard EMCCD gain register
            1: Conventional CCD register
        """
        error = self.dll.SetOutputAmplifier(type)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetOutputAmplifier error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetOutputAmplifier error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetOutputAmplifier error. Output amplifier type invalid.'

    def GetNumberHSSpeeds(self, channel, type):
        """
        :param: channel, type
        :return: error message (string)

        int channel:
            The AD channel

        int type:
            0: Electron mulitiplication
            1: Conventional

        As your Andor SDK system is capable of operating at more than one
        horizontal shift speed, this function will return the actual number of
        speeds possible.
        """
        numberHSS = c_int()

        error = self.dll.GetNumberHSSpeeds(channel, type, byref(numberHSS))

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: GetNumberHSSpeeds error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: GetNumberHSSpeeds error. Invalid channel.'

        elif ERROR_CODE[error] == 'DRV_P2INVALID':
            return 'Andor: GetNumberHSSpeeds error. Invalid horizontal read mode.'

    def GetHSSpeed(self, channel, type, index):
        """
        :param channel:
        :param type:
        :param index:
        :return error message(string):

        As your Andor system is capable of operating at more than one horizontal shift
        speed this function will return the actual speeds available. The value
        returned is in MHz.

        int channel
            the AD channel

        int type
            0: electron multiplication
            1: conventional

        int index
            values that it can take are between 0 and HSSpeed-1
        """
        HSSpeed = c_float()

        error = self.dll.GetHSSpeed(channel, type, index, byref(HSSpeed))

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: GetHSSpeed error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: GetHSSpeed error. Invalid channel.'

        elif ERROR_CODE[error] == 'DRV_P2INVALID':
            return 'Andor: GetHSSpeed error. Invalid horizontal read mode.'

        elif ERROR_CODE[error] == 'DRV_P3INVALID':
            return 'Andor: GetHSSpeed error. Invalid index.'

    def SetHSSpeed(self, type, index):
        """
        :param type:
        :param index:
        :return error message(string):

        This function will set the speed at which the pixels are shifted into the output
        node during the readout phase of an acquisition. Typically your camera will be
        capable of operating at several horizontal shift speeds. To get the actual speed
        that an index corresponds to, use the GetHSSpeed function.

        int type
            0: electron multiplication
            1: conventional

        int index
            Valid values between 0 to GetNumberHSSpeeds()-1
        """
        error = self.dll.SetHSSpeed(type, index)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetHSSpeed error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetHSSpeed error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetHSSpeed error. Mode is invalid.'

        elif ERROR_CODE[error] == 'DRV_P2INVALID':
            return 'Andor: SetHSSpeed error. Index is out of range.'

    def GetNumberVSSpeeds(self):
        """
        :return error message(string):

        As your Andor system may be capable of operating at more than one vertical
        shift speed this function will return the actual number of speeds available.
        """
        noVSSpeeds = c_int()

        error = self.dll.GetNumberVSSpeeds(byref(noVSSpeeds))

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: GetNumberVSSpeeds error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: GetNumberVSSpeeds error. Acquisition in progress.'

    def GetVSSpeed(self, index):
        """
        :param index:
        :return error message(string):

        As your Andor SDK system may be capable of operating at more than one vertical
        shift speed this function will return the actual speeds available. The value
        returned is in ms.
        """
        VSSpeed = c_float()

        error = self.dll.GetVSSpeed(index, byref(VSSpeed))

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: GetVSSpeed error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: GetVSSpeed error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: GetVSSpeed error. Invalid index.'

    def SetVSSpeed(self, index):
        """
        :param index:
        :return error message(string):

        This function will set the vertical speed to be used for subsequent acquisitions.
        """
        error = self.dll.SetVSSpeed(index)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            pass

        elif ERROR_CODE[error] == 'DRV_NOT_INITIALIZED':
            return 'Andor: SetVSSpeed error. System not initialized.'

        elif ERROR_CODE[error] == 'DRV_ACQUIRING':
            return 'Andor: SetVSSpeed error. Acquisition in progress.'

        elif ERROR_CODE[error] == 'DRV_P1INVALID':
            return 'Andor: SetVSSpeed error. Index out of range.'



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