import time
import ctypes
import numpy as np
from PyQt5 import QtCore


class WorkerSignals(QtCore.QObject):
    dataLiveAcquire = QtCore.pyqtSignal()


class CcdAcquireThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(CcdAcquireThread, self).__init__()
        self.signals = WorkerSignals()
        self.ui = ui
        self.cimage = (ctypes.c_int * self.ui.andor.height * self.ui.andor.width)()

        self.mutex = QtCore.QMutex()

    @QtCore.pyqtSlot()
    def stop(self):
        self.mutex.lock()
        self.ui.ccdacquiring = False
        self.mutex.unlock()

    @QtCore.pyqtSlot()
    def run(self):
        self.ui.ccdacquiring = True
        while self.ui.ccdacquiring:
            self.ui.andor.startacquisition()
            self.ui.andor.waitforacquisition()
            self.ui.andor.getacquireddata(self.cimage, numscans=1, acqtype='image')

            self.signals.dataLiveAcquire.emit()

        else:
            # Storing the positions of the random tracks in an array
            randtrack = np.array([int(self.ui.camtrackLower1.text()),
                                  int(self.ui.camtrackUpper1.text()),
                                  int(self.ui.camtrackLower2.text()),
                                  int(self.ui.camtrackUpper2.text())])

            self.ui.andor.setshutter(1, 2, 0, 0)  # Ensuring the shutter is closed
            self.ui.andor.setreadmode(2)  # Setting the read mode to Random Tracks
            self.ui.andor.setrandomtracks(2, randtrack)
            self.ui.andor.setexposuretime(self.exposuretime)

            time.sleep(1)
