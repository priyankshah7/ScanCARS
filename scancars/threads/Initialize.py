import numpy as np
import time, ctypes, h5py
from PyQt5 import QtCore

from scancars.utils import toggle
from andorsdk.pyandor import ERROR_CODE

andordll = ctypes.cdll.LoadLibrary("C:\\Program Files\\Andor iXon\\Drivers\\atmcd64d")


class AndorSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()


class Andor(QtCore.QRunnable):
    def __init__(self, gui):
        super(Andor, self).__init__()
        self.gui = gui
        self.signals = AndorSignals()

    @QtCore.pyqtSlot()
    def run(self):
        toggle.deactivate_buttons(self.gui)

        # Initializing the camera
        messageInitialize = self.gui.cam.Initialize()
        if messageInitialize is not None:
            self.gui.post.eventlog(self.gui, messageInitialize)
            return

        # Setting the shutter
        messageSetShutter = self.gui.cam.SetShutter(1, 2, 0, 0)
        if messageSetShutter is not None:
            self.gui.post.eventlog(self.gui, messageSetShutter)
            return

        # Setting read mode to Random Track and setting track positions
        messageSetReadMode = self.gui.cam.SetReadMode(2)
        if messageSetReadMode is not None:
            self.gui.post.eventlog(self.gui, messageSetReadMode)
            return

        RandomTrackposition = np.array([int(self.gui.CameraOptions_track1lower.text()),
                                        int(self.gui.CameraOptions_track1upper.text()),
                                        int(self.gui.CameraOptions_track2lower.text()),
                                        int(self.gui.CameraOptions_track2upper.text())])

        messageSetRandomTrack = self.gui.cam.SetRandomTracks(2, RandomTrackposition)
        if messageSetRandomTrack is not None:
            self.gui.post.eventlog(self.gui, messageSetRandomTrack)
            return

        # Getting and setting AD channel
        messageGetNumberADChannels = self.gui.cam.GetNumberADChannels()
        if messageGetNumberADChannels is not None:
            self.gui.post.eventlog(self.gui, messageGetNumberADChannels)
            return

        messageSetADChannel = self.gui.cam.SetADChannel(1)
        if messageSetADChannel is not None:
            self.gui.post.eventlog(self.gui, messageSetADChannel)
            return

        # Setting trigger mode
        messageSetTriggerMode = self.gui.cam.SetTriggerMode(0)
        if messageSetTriggerMode is not None:
            self.gui.post.eventlog(self.gui, messageSetRandomTrack)
            return

        # Getting the detector chip size
        messageGetDetector = self.gui.cam.GetDetector()
        if messageGetDetector is not None:
            self.gui.post.eventlog(self.gui, messageGetDetector)
            return

        # Setting horizontal and vertical shift speeds
        messageSetHSSpeed = self.gui.cam.SetHSSpeed(1, 0)
        if messageSetHSSpeed is not None:
            self.gui.post.eventlog(self.gui, messageSetHSSpeed)
            return

        messageSetVSSpeed = self.gui.cam.SetVSSpeed(3)
        if messageSetVSSpeed is not None:
            self.gui.post.eventlog(self.gui, messageSetVSSpeed)
            return

        toggle.activate_buttons(self.gui)
        self.signals.finished.emit()

