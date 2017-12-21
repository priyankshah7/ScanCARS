import time
import numpy as np
from PyQt5 import QtCore

from scancars.sdk.andor import Cam
from scancars.utils import toggle, post

andor = Cam()

# TODO Check to see if pyqtSlot can be used for method-only instead of within class using the run method
# TODO Try called the stop method directly when stopping a signal instead of sending a signal to it.


class Signals(QtCore.QObject):
    finished = QtCore.pyqtSignal()


class Initialize(QtCore.QRunnable):
    def __init__(self, ui):
        super(Initialize, self).__init__()
        self.signals = Signals()
        self.ui = ui

    @QtCore.pyqtSlot()
    def run(self):
        toggle.deactivate_buttons(self.ui)

        randtrack = np.array([int(self.ui.CameraOptions_track1lower.text()),
                              int(self.ui.CameraOptions_track1upper.text()),
                              int(self.ui.CameraOptions_track2lower.text()),
                              int(self.ui.CameraOptions_track2upper.text())])

        errorinitialize = andor.initialize()
        if errorinitialize != 'DRV_SUCCESS':
            post.eventlog(self.ui, 'Andor: Initialize error. ' + errorinitialize)
            return
        andor.getdetector()
        andor.setshutter(1, 2, 0, 0)
        andor.setreadmode(2)
        andor.setrandomtracks(2, randtrack)
        andor.setadchannel(1)
        andor.settriggermode(0)
        andor.sethsspeed(1, 0)
        andor.setvsspeed(4)

        andor.dim = andor.width * andor.randomtracks

        toggle.activate_buttons(self.ui)
        self.signals.finished.emit()


class Shutdown(QtCore.QRunnable):
    def __init__(self, ui):
        super(Shutdown, self).__init__()
        self.signals = Signals()
        self.ui = ui

    @QtCore.pyqtSlot()
    def run(self):
        andor.setshutter(1, 2, 0, 0)
        andor.iscooleron()
        if andor.coolerstatus == 0:
            andor.shutdown()

        elif andor.coolerstatus == 1:
            andor.cooleroff()
            while andor.temperature < -20:
                time.sleep(1)
            andor.shutdown()

        self.signals.finished.emit()
