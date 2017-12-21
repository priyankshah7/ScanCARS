import time, ctypes
import numpy as np
from PyQt5 import QtCore

from scancars.sdk.andor import Cam
from scancars.utils import toggle, post

andor = Cam()


class Signals(QtCore.QObject):
    finished = QtCore.pyqtSignal()


class Acquire(QtCore.QRunnable):
    def __init__(self, ui):
        super(Acquire, self).__init__()
        self.signals = Signals()
        self.ui = ui

        self.condition = False
        self.track1 = None
        self.track2 = None
        self.trackdiff = None

    @QtCore.pyqtSlot()
    def run(self):
        andor.setacquisitionmode(1)
        andor.setshutter(1, 1, 0, 0)

        self.ui.post.status(self.ui, 'Acquiring...')
        self.ui.Main_start_acq.setText('Stop Acquisition')

        self.condition = True
        while self.condition:
            andor.setexposuretime(float(self.ui.SpectralAcq_time_req.text()))
            andor.startacquisition()
            andor.waitforacquisition()
            error = andor.getacquireddata()
            if error != 'DRV_SUCCESS':
                self.ui.post.eventdialog(self.ui, error)

            # self.ui.post.eventlog(self.ui, 'huhh2...')
            # self.track1 = andor.imagearray[0:andor.width-1]
            # self.track2 = andor.imagearray[andor.width:(2*andor.width)-1]
            # self.trackdiff = self.track2 - self.track1
            #
            # self.ui.Main_specwin.clear()
            # self.ui.Main_specwin.plot(self.track1, pen='r', name='track1')
            # self.ui.Main_specwin.plot(self.track2, pen='g', name='track2')
            # self.ui.Main_specwin.plot(self.trackdiff, pen='w', name='trackdiff')
            #
            # andor.freeinternalmemory()
            # QtCore.QCoreApplication.processEvents()