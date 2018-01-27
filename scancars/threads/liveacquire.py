import ctypes
from PyQt5 import QtCore


class WorkerSignals(QtCore.QObject):
    dataLiveAcquire = QtCore.pyqtSignal()


class LiveAcquireThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(LiveAcquireThread, self).__init__()
        self.signals = WorkerSignals()
        self.ui = ui
        self.cimage = (ctypes.c_int * self.ui.andor.dim)()

        self.mutex = QtCore.QMutex()

    @QtCore.pyqtSlot()
    def stop(self):
        self.mutex.lock()
        self.ui.acquiring = False
        self.mutex.unlock()

    @QtCore.pyqtSlot()
    def run(self):
        self.ui.acquiring = True
        while self.ui.acquiring:
            self.ui.andor.startacquisition()
            self.ui.andor.waitforacquisition()
            self.ui.andor.getacquireddata(self.cimage)

            self.signals.dataLiveAcquire.emit()
