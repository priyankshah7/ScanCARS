# Python version of the Andor SDK

import ctypes
import numpy as np

# Loading the Andor dll driver
dll = ctypes.cdll.LoadLibrary("C:\\Program Files\\Andor iXon\\Drivers\\atmcd64d")


class Cam:
    def __init__(self):
        self.width = None
        self.temperature = None
        self.coolerstatus = None
        self.exposure = None
        self.kinetic = None
        self.acquisitionmode = None
        self.getstatus = None
        self.randomtracks = None
        self.imagearray = None
        self.dim = None

    def initialize(self):
        error = dll.Initialize("C:\\Program Files\\Andor iXon")
        return ERROR_CODE[error]

    def cooleron(self):
        error = dll.CoolerON()
        return ERROR_CODE[error]

    def cooleroff(self):
        error = dll.CoolerOFF()
        return ERROR_CODE[error]

    def settemperature(self, temperature):
        """
        :param temperature:
        :return: error message(string)

        This function will set the desired temperature of the detector. To turn
        cooling ON and OFF use the CoolerON and CoolerOFF functions
        """
        error = dll.SetTemperature(temperature)
        return ERROR_CODE[error]

    def gettemperature(self):
        """
        :return error message(string):

        This function returns the temperature of the detector to the nearest degree.
        It also gives the status of the cooling process.
        """
        temperature = ctypes.c_int()
        error = dll.GetTemperature(ctypes.byref(temperature))
        self.temperature = temperature.value
        return ERROR_CODE[error]

    def shutdown(self):
        error = dll.ShutDown()
        return ERROR_CODE[error]

    def setreadmode(self, mode):
        # 0: Full vertical binning
        # 1: multi track
        # 2: random track
        # 3: single track
        # 4: image
        error = dll.SetReadMode(mode)
        return ERROR_CODE[error]

    def setacquisitionmode(self, mode):
        # 1: Single Scan
        # 2: Accumulate
        # 3: Kinetics
        # 4: Fast Kinetics
        # 5: Run till abort

        error = dll.SetAcquisitionMode(mode)
        return ERROR_CODE[error]

    def setnumberkinetics(self, numkin):
        """
        :param numkin:
        :return error message(string):

        This function will set the number of scans to be taken during a single
        acquisition sequence. This will only take effect if the acquisition
        mode is Kinetic Series.
        """
        error = dll.SetNumberKinetics(numkin)
        return ERROR_CODE[error]

    def setnumberaccumulations(self, number):
        """
        :param number:
        :return error message(string):

        This function will set the number of scans accumulated in memory.
        This will only take effect if the acquisition mode is either
        Accumulate or Kinetic Series.
        """
        error = dll.SetNumberKinetics(number)
        return ERROR_CODE[error]

    def setaccumulationcycletime(self, time):
        """
        :param time:
        :return error message(string):

        This function will set the accumulation cycle time to the nearest
        valid value not less than the given value. The actual cycle time used is
        obtained by GetAcquisitionTimings.
        """
        error = dll.SetAccumulationCycleTime(time)
        return ERROR_CODE[error]

    def setkineticcycletime(self, time):
        """
        :param time:
        :return error message(string):

         This function will set the kinetic cycle time to the nearest valid value
         not less than the given value. The actual time used is obtained
         by GetAcquisitionTimings.
        """
        error = dll.SetKineticCycleTime(time)
        return ERROR_CODE[error]

    def setshutter(self, typeshut, mode, closingtime, openingtime):
        """
        :param typeshut:
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
        error = dll.SetShutter(typeshut, mode, closingtime, openingtime)
        return ERROR_CODE[error]

    def startacquisition(self):
        """
        :return error message(string):

        This function starts an acquisition. The status of the acquisition can
        be monitored via GetStatus().
        """
        error = dll.StartAcquisition()
        return ERROR_CODE[error]

    def getacquireddata(self):
        """
        This function will return the data from the last acquisition. The data
        are returned as long integers (32bit signed integers). The array must
        be large enough
        """
        # TODO Can only be used for spectra (not for CCD tracks unless updated)
        self.imagearray = None

        cimageArray = ctypes.c_int * self.dim
        cimage = cimageArray()

        # error = dll.GetAcquiredData16(ctypes.pointer(cimage), self.dim)
        # self.imagearray = np.asarray(cimage[:], dtype=np.uint16)
        error = dll.GetAcquiredData(ctypes.pointer(cimage), self.dim)
        self.imagearray = np.asarray(cimage[:])
        return ERROR_CODE[error]

    def setexposuretime(self, time):
        """
        :param time:
        :return error message(string):

        This function will set the exposure time to the nearest valid value not
        less than the given value. The actual exposure time is obtained by
        GetAcquisitionTimings().
        """
        error = dll.SetExposureTime(ctypes.c_float(time))
        return ERROR_CODE[error]

    def getnumberadchannels(self):
        """
        :return:

        As your Andor SDK system may be capable of operating with more than one
        A-D converter, this function will tell you the number available.
        """
        nochannels = ctypes.c_int()

        error = dll.GetNumberADChannels(nochannels)
        return ERROR_CODE[error]

    def setadchannel(self, channel):
        """
        :param channel:
        :return error message(string):

        This function will set the AD channel to one of the possible A-Ds of the
        system. This AD channel will be used for all subsequent operations
        performed by the system.
        """
        error = dll.SetADChannel(channel)
        return ERROR_CODE[error]

    def getbitdepth(self, channel):
        """
        :param channel:
        :return error message(string):

        This function will retrieve the size in bits of the dynamic range for
        any available AD channel.
        """
        bitdepth = ctypes.c_int

        error = dll.GetBitDepth(channel, ctypes.byref(bitdepth))
        return ERROR_CODE[error]

    def getnumberhsspeeds(self, channel, typehss):
        """
        :param: channel, typehss
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
        numberhss = ctypes.c_int()

        error = dll.GetNumberHSSpeeds(channel, typehss, ctypes.byref(numberhss))
        return ERROR_CODE[error]

    def gethsspeed(self, channel, typehss, index):
        """
        :param channel:
        :param typehss:
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
        hsspeed = ctypes.c_float()

        error = dll.GetHSSpeed(channel, typehss, index, ctypes.byref(hsspeed))
        return ERROR_CODE[error]

    def sethsspeed(self, typehss, index):
        """
        :param typehss:
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
        error = dll.SetHSSpeed(typehss, index)
        return ERROR_CODE[error]

    def getnumbervsspeeds(self):
        """
        :return error message(string):

        As your Andor system may be capable of operating at more than one vertical
        shift speed this function will return the actual number of speeds available.
        """
        novsspeeds = ctypes.c_int()

        error = dll.GetNumberVSSpeeds(ctypes.byref(novsspeeds))
        return ERROR_CODE[error]

    def getvsspeed(self, index):
        """
        :param index:
        :return error message(string):

        As your Andor SDK system may be capable of operating at more than one vertical
        shift speed this function will return the actual speeds available. The value
        returned is in ms.
        """
        vsspeed = ctypes.c_float()

        error = dll.GetVSSpeed(index, ctypes.byref(vsspeed))
        return ERROR_CODE[error]

    def setvsspeed(self, index):
        """
        :param index:
        :return error message(string):

        This function will set the vertical speed to be used for subsequent acquisitions.
        """
        error = dll.SetVSSpeed(index)
        return ERROR_CODE[error]

    def getstatus(self):
        """
        :return error message(string):

        This function will return the current status of the Andor SDK system. This function
        should be called before an acquisition is started to ensure that it is IDLE and
        during an acquisition to monitor the process.
        """
        status = ctypes.c_long()

        error = dll.GetStatus(ctypes.byref(status))
        self.getstatus = status.value
        return ERROR_CODE[error]

    def abortacquisition(self):
        """
        :return error message(string):

        This function aborts the current acquisition if one is active.
        """
        error = dll.AbortAcquisition()
        return ERROR_CODE[error]

    def iscooleron(self):
        """
        :return error message(string):

        This function checks the status of the cooler.
        """
        coolerstatus = ctypes.c_int()

        error = dll.IsCoolerOn(ctypes.byref(coolerstatus))
        self.coolerstatus = coolerstatus.value
        return ERROR_CODE[error]

    def getdetector(self):
        """
        :return error message(string):

        This function returns the size of the detector in pixels. The horizontal axis is
        taken to be the axis parallel to the readout register.
        """
        cw = ctypes.c_int()
        ch = ctypes.c_int()

        error = dll.GetDetector(ctypes.byref(cw), ctypes.byref(ch))
        self.width = cw.value
        return ERROR_CODE[error]

    def setrandomtracks(self, numtracks, areas):
        """
        :param numtracks:
        :param areas:
        :return error message(string):

        This function will set the Random-Track parameters. The positions of the tracks are
        validated to ensure that the tracks are in increasing order and do not overlap.
        The horizontal binning is set via the SetCustomTrackHBin function. The vertical
        binning is set to the height of each track.

        e.g. Tracks specified as 20 30 31 40 has the first track starting at row 20 and
        finishing at 30 and the second track starting at 31 and finishing at 40.
        """
        areas_to_pass = areas.ctypes.data_as(ctypes.POINTER(ctypes.c_long))

        error = dll.SetRandomTracks(numtracks, areas_to_pass)
        self.randomtracks = numtracks
        return ERROR_CODE[error]

    def settriggermode(self, mode):
        """
        :param mode:
        :return error message(string):

        This function will set the trigger mode that the camera will operate in.

        int mode
            0: Internal
            1: External
            6: External start
            7: External exposure (bulb)
            9. External FVB EM (only valid for EM Newton models)
            10.Software Trigger
            12.External charge shifting
        """
        error = dll.SetTriggerMode(mode)
        return ERROR_CODE[error]

    def getacquisitiontimings(self):
        """
        :return error message(string):

        This function will return the current valid acquisition timing information. This
        function should be used after all the acquisitions setting have been set
        e.g. SetExposureTime, SetKineticCycleTime and SetReadMode etc. The values returned
        are the actual times used in subsequent acquisitions.
        """
        exposure = ctypes.c_float()
        accumulate = ctypes.c_float()
        kinetic = ctypes.c_float()

        error = dll.GetAcquisitionTimings(ctypes.byref(exposure), ctypes.byref(accumulate), ctypes.byref(kinetic))
        self.exposure = exposure.value
        self.kinetic = kinetic.value
        return ERROR_CODE[error]

    def setbaselineclamp(self, state):
        """
        :param state:
        :return error message(string):

        This function turns on and off the baseline clamp functionality. With this feature
        enabled, the baseline level of each scan in a kinetic series will be more consistent
        across the sequence.

        int state
            0: Disable baseline clamp
            1: Enable baseline clamp
        """
        error = dll.SetBaselineClamp(state)
        return ERROR_CODE[error]

    def freeinternalmemory(self):
        """
        :return error message(string):

        This function will deallocate any memory used internally to store the previously acquired
        data. Note that once this function has been called, data from last acquisition cannot
        be retrieved.
        """
        error = dll.FreeInternalMemory()
        return ERROR_CODE[error]

    def waitforacquisition(self):
        error = dll.WaitForAcquisition()
        return ERROR_CODE[error]


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
    20094: "DRV_RANDOM_TRACK_ERROR",
    20095: "DRV_INVALID_TRIGGER_MODE",
    20099: "DRV_BINNING_ERROR",
    20990: "DRV_NOCAMERA",
    20991: "DRV_NOT_SUPPORTED",
    20992: "DRV_NOT_AVAILABLE"
}