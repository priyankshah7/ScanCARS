import time
import numpy as np
from PyQt5 import QtCore

from scancars.sdk.andor.pyandor import Cam
from scancars.utils import toggle, post

andor = Cam()


class WorkerSignals(QtCore.QObject):
    finishedInitialize = QtCore.pyqtSignal()
    finishedShutdown = QtCore.pyqtSignal()
    finishedAcquire = QtCore.pyqtSignal()
    finishedAcquireStop = QtCore.pyqtSignal()


class AndorThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(AndorThread, self).__init__()
        self.signals = WorkerSignals()
        self.ui = ui

    @QtCore.pyqtSlot()
    def shutdown(self):
        andor.setshutter(1, 2, 0, 0)
        andor.iscooleron()
        if andor.coolerstatus == 0:
            andor.shutdown()

        elif andor.coolerstatus == 1:
            andor.cooleroff()
            while andor.temperature < -20:
                time.sleep(1)
            andor.shutdown()

        self.signals.finishedShutdown.emit()

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
        self.signals.finishedInitialize.emit()


class TemperatureThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(TemperatureThread, self).__init__()
        self.ui = ui
        self.tempcondition = None

    @QtCore.pyqtSlot()
    def stop(self):
        self.tempcondition = False

    @QtCore.pyqtSlot()
    def run(self):
        self.tempcondition = True
        while self.tempcondition:
            andor.gettemperature()
            self.ui.CameraTemp_temp_actual.setText(str(andor.temperature))
            time.sleep(2)


class AcquireThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(AcquireThread, self).__init__()
        self.signals = WorkerSignals()
        self.ui = ui
        self.acquirecondition = None

        self.width = andor.width

        self.track1plot = self.ui.Main_specwin.plot()
        self.track2plot = self.ui.Main_specwin.plot()
        self.diffplot = self.ui.Main_specwin.plot()

    @QtCore.pyqtSlot()
    def stop(self):
        toggle.activate_buttons()
        post.status(self.ui, '')
        self.ui.Main_start_acq.setText('Start Acquisition')

        self.acquirecondition = False
        andor.setshutter(1, 2, 0, 0)

        self.signals.finishedAcquireStop.emit()

    @QtCore.pyqtSlot()
    def run(self):
        toggle.deactivate_buttons(self.ui, main_start_acq_stat=True)
        post.status(self.ui, 'Acquiring...')
        self.ui.Main_start_acq.setText('Stop Acquisition')

        self.ui.Main_specwin.clear()

        andor.setacquisitionmode(1)
        andor.setshutter(1, 1, 0, 0)

        self.acquirecondition = True
        while self.acquirecondition:
            # TODO Shouldn't get exptime like this, store in the main gui and retrieve from there
            andor.setexposuretime(float(self.ui.SpectralAcq_time_req.text()))
            andor.startacquisition()
            andor.waitforacquisition()
            andor.getacquireddata()

            imagearray = andor.imagearray

            self.track1plot.setData(imagearray[0:self.width - 1], pen='r', name='track1')
            self.track2plot.setData(imagearray[self.width:(2 * self.width) - 1], pen='g', name='track2')
            self.diffplot.setData(imagearray[self.width:(2 * self.width) - 1] - imagearray[0:self.width - 1],
                                  pen='w', name='trackdiff')

            andor.freeinternalmemory()


class SpectralThread(QtCore.QRunnable):
    pass


class HyperspectralThread(QtCore.QRunnable):
    pass