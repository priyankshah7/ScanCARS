import sys, time, ctypes
import numpy as np
from PyQt5 import QtCore

from scancars import main
from scancars.sdk import andor
from scancars.utils.toggle import Toggle

toggle = Toggle()

# TODO Check to see if pyqtSlot can be used for method-only instead of within class using the run method
# TODO Try called the stop method directly when stopping a signal instead of sending a signal to it.


class Signals(QtCore.QObject):
    finished = QtCore.pyqtSignal()


class Initialize(QtCore.QRunnable, main.ScanCARS):
    def __init__(self, parent=main.ScanCARS):
        super(Initialize, self).__init__(parent)
        self.signals = Signals()

    @QtCore.pyqtSlot()
    def run(self):
        toggle.deactivate_buttons()

        randtrack = np.array([int(self.CameraOptions_track1lower.text()),
                              int(self.CameraOptions_track1upper.text()),
                              int(self.CameraOptions_track2lower.text()),
                              int(self.CameraOptions_track2upper.text())])

        andor.initialize()
        _, width = andor.getdetector()
        andor.setshutter(1, 2, 0, 0)
        andor.setreadmode(2)
        andor.setrandomtracks(2, randtrack)
        andor.setadchannel(1)
        andor.settriggermode(0)
        andor.sethsspeed(1, 0)
        andor.setvsspeed(3)

        toggle.activate_buttons()
        self.signals.finished.emit()


class Acquire(QtCore.QRunnable):
    def __init__(self):
        super(Acquire, self).__init__()
        self.signals = Signals()

    @QtCore.pyqtSlot()
    def stop(self):
        pass

    @QtCore.pyqtSlot()
    def run(self):
        pass


class CameraTemp(QtCore.QRunnable):
    def __init__(self):
        super(CameraTemp, self).__init__()
        self.signals = Signals()

    @QtCore.pyqtSlot()
    def run(self):
        pass
