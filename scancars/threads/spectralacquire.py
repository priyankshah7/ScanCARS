import ctypes
from PyQt5 import QtCore


class WorkerSignals(QtCore.QObject):
    dataSpectralAcquire = QtCore.pyqtSignal(int)
    finishedSpectralAcquire = QtCore.pyqtSignal()


class SpectralAcquireThread(QtCore.QRunnable):
    def __init__(self, ui, frames, darkcount):
        super(SpectralAcquireThread, self).__init__()
        self.signals = WorkerSignals()
        self.ui = ui
        self.cimage = (ctypes.c_long * self.ui.andor.dim)()

        self.frames = frames
        self.darkcount = darkcount

        self.mutex = QtCore.QMutex()

    @QtCore.pyqtSlot()
    def stop(self):
        self.mutex.lock()
        self.ui.spectralacquiring = False
        self.ui.acquisition_cancelled = True
        self.mutex.unlock()

    @QtCore.pyqtSlot(int)
    def run(self):
        # # Dark acquisition
        # self.ui.andor.setshutter(1, 2, 0, 0)
        # self.ui.andor.setexposuretime(self.ui.darkexposure)
        # self.ui.andor.setacquisitionmode(1)
        #
        # time.sleep(0.5)
        #
        # numscan = 0
        # while numscan < self.darkcount:
        #     self.ui.andor.startacquisition()
        #     self.ui.andor.waitforacquisition()
        #     self.ui.andor.getacquireddata(self.cimage, 1)
        #
        #     self.signals.dataSpectralAcquire.emit(numscan)
        #
        #     numscan += 1

        numscan = 0
        self.ui.spectralacquiring = True
        while numscan < self.frames and self.ui.spectralacquiring is True:
            self.ui.andor.startacquisition()
            self.ui.andor.waitforacquisition()
            self.ui.andor.getacquireddata(self.cimage, 1)

            self.signals.dataSpectralAcquire.emit(numscan)

            numscan += 1

        else:
            self.ui.andor.setshutter(1, 2, 0, 0)

        self.ui.spectralacquiring = False
        self.signals.finishedSpectralAcquire.emit()
