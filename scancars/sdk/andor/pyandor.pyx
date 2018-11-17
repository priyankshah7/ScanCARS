import ctypes
import numpy as np
# cimport numpy as np

# Loading the Andor dll driver from the Andor SDK library (ignore other souorces of the driver)
dll = ctypes.cdll.LoadLibrary("C:\\Program Files\\Andor SDK\\atmcd64d")


cdef class Cam:
    cdef public int width
    cdef public int height
    cdef public float temperature
    cdef public int coolerstatus
    cdef public float exposure
    cdef public float kinetic
    cdef public str getstatusval
    cdef public int randomtracks
    # cdef public np.ndarray imagearray
    cdef public imagearray
    cdef public int dim

    cpdef str initialize(self):
        cdef int error
        error = dll.Initialize("C:\\Program Files\\Andor SDK")
        return ERROR_CODE[error]

    cpdef str cooleron(self):
        cdef int error
        error = dll.CoolerON()
        return ERROR_CODE[error]

    cpdef str cooleroff(self):
        cdef int error
        error = dll.CoolerOFF()
        return ERROR_CODE[error]

    cpdef str settemperature(self, temperature):
        cdef int error
        error = dll.SetTemperature(temperature)
        return ERROR_CODE[error]

    cpdef str gettemperature(self):
        cdef int error
        temperature = ctypes.c_int()
        error = dll.GetTemperature(ctypes.byref(temperature))
        self.temperature = temperature.value
        return ERROR_CODE[error]

    cpdef str shutdown(self):
        cdef int error
        error = dll.ShutDown()
        return ERROR_CODE[error]

    cpdef str setreadmode(self, mode):
        cdef int error
        error = dll.SetReadMode(mode)
        return ERROR_CODE[error]

    cpdef str setacquisitionmode(self, mode):
        cdef int error
        error = dll.SetAcquisitionMode(mode)
        return ERROR_CODE[error]

    cpdef str setnumberkinetics(self, numkin):
        cdef int error
        error = dll.SetNumberKinetics(numkin)
        return ERROR_CODE[error]

    cpdef str setnumberaccumulations(self, number):
        cdef int error
        error = dll.SetNumberAccumulations(number)
        return ERROR_CODE[error]

    cpdef str setaccumulationcycletime(self, time):
        cdef int error
        error = dll.SetAccumulationCycleTime(ctypes.c_float(time))
        return ERROR_CODE[error]

    cpdef str setkineticcycletime(self, time):
        cdef int error
        error = dll.SetKineticCycleTime(ctypes.c_float(time))
        return ERROR_CODE[error]

    cpdef str setshutter(self, int typeshut, int mode, int closingtime, int openingtime):
        cdef int error
        error = dll.SetShutter(typeshut, mode, closingtime, openingtime)
        return ERROR_CODE[error]

    cpdef str startacquisition(self):
        cdef int error
        error = dll.StartAcquisition()
        return ERROR_CODE[error]

    cpdef str getacquireddata(self, cimage, int numscans=1, str acqtype='spectral'):
        cdef int error

        if acqtype == 'spectral':
            error = dll.GetAcquiredData(ctypes.pointer(cimage), self.dim*numscans)
            self.imagearray = np.asarray(cimage[:])
            return ERROR_CODE[error]

        elif acqtype == 'image':
            error = dll.GetAcquiredData(ctypes.pointer(cimage), self.width*self.height)
            self.imagearray = np.asarray(cimage[:])
            return ERROR_CODE[error]

    cpdef str setframetransfermode(self, mode):
        cdef int error
        error = dll.SetFrameTransferMode(mode)
        return ERROR_CODE[error]

    cpdef str setexposuretime(self, time):
        cdef int error
        error = dll.SetExposureTime(ctypes.c_float(time))
        return ERROR_CODE[error]

    cpdef str getnumberadchannels(self):
        cdef int error
        nochannels = ctypes.c_int()
        error = dll.GetNumberADChannels(nochannels)
        return ERROR_CODE[error]

    cpdef str setadchannel(self, channel):
        cdef int error
        error = dll.SetADChannel(channel)
        return ERROR_CODE[error]

    cpdef str getbitdepth(self, channel):
        cdef int error
        bitdepth = ctypes.c_int
        error = dll.GetBitDepth(channel, ctypes.byref(bitdepth))
        return ERROR_CODE[error]

    cpdef str getnumberhsspeeds(self, channel, typehss):
        cdef int error
        numberhss = ctypes.c_int()
        error = dll.GetNumberHSSpeeds(channel, typehss, ctypes.byref(numberhss))
        return ERROR_CODE[error]

    cpdef str gethsspeed(self, channel, typehss, index):
        cdef int error
        hsspeed = ctypes.c_float()
        error = dll.GetHSSpeed(channel, typehss, index, ctypes.byref(hsspeed))
        return ERROR_CODE[error]

    cpdef str sethsspeed(self, typehss, index):
        cdef int error
        error = dll.SetHSSpeed(typehss, index)
        return ERROR_CODE[error]

    cpdef str getnumbervsspeeds(self):
        cdef int error
        novsspeeds = ctypes.c_int()
        error = dll.GetNumberVSSpeeds(ctypes.byref(novsspeeds))
        return ERROR_CODE[error]

    cpdef str getvsspeed(self, index):
        cdef int error
        vsspeed = ctypes.c_float()
        error = dll.GetVSSpeed(index, ctypes.byref(vsspeed))
        return ERROR_CODE[error]

    cpdef str setvsspeed(self, index):
        cdef int error
        error = dll.SetVSSpeed(index)
        return ERROR_CODE[error]

    cpdef str getstatus(self):
        cdef int error
        status = ctypes.c_long()
        error = dll.GetStatus(ctypes.byref(status))
        self.getstatusval = ERROR_CODE[status.value]
        return ERROR_CODE[error]

    cpdef str abortacquisition(self):
        cdef int error
        error = dll.AbortAcquisition()
        return ERROR_CODE[error]

    cpdef str iscooleron(self):
        cdef int error
        coolerstatus = ctypes.c_int()
        error = dll.IsCoolerOn(ctypes.byref(coolerstatus))
        self.coolerstatus = coolerstatus.value
        return ERROR_CODE[error]

    cpdef str getdetector(self):
        cdef int error
        cw = ctypes.c_int()
        ch = ctypes.c_int()
        error = dll.GetDetector(ctypes.byref(cw), ctypes.byref(ch))
        self.width = cw.value
        self.height = ch.value
        return ERROR_CODE[error]

    cpdef str setrandomtracks(self, int numtracks, areas):
        cdef int error
        areas_to_pass = areas.ctypes.data_as(ctypes.POINTER(ctypes.c_long))
        error = dll.SetRandomTracks(numtracks, areas_to_pass)
        self.randomtracks = numtracks
        return ERROR_CODE[error]

    cpdef str settriggermode(self, int mode):
        cdef int error
        error = dll.SetTriggerMode(mode)
        return ERROR_CODE[error]

    cpdef str getacquisitiontimings(self):
        cdef int error
        exposure = ctypes.c_float()
        accumulate = ctypes.c_float()
        kinetic = ctypes.c_float()

        error = dll.GetAcquisitionTimings(ctypes.byref(exposure), ctypes.byref(accumulate), ctypes.byref(kinetic))
        self.exposure = exposure.value
        self.kinetic = kinetic.value
        return ERROR_CODE[error]

    cpdef str freeinternalmemory(self):
        cdef int error
        error = dll.FreeInternalMemory()
        return ERROR_CODE[error]

    cpdef str waitforacquisition(self):
        cdef int error
        error = dll.WaitForAcquisition()
        return ERROR_CODE[error]


cdef dict ERROR_CODE = {
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

