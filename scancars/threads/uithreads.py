import time
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from scancars.sdk.andor.pyandor import Cam
from scancars.gui.forms import main
from scancars.utils import toggle, post

andor = Cam()


class WorkerSignals(QtCore.QObject):
    finishedShutdown = QtCore.pyqtSignal()
    finishedAcquire = QtCore.pyqtSignal()
    finishedAcquireStop = QtCore.pyqtSignal()


class TemperatureThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(TemperatureThread, self).__init__()
        self.ui = ui
        # self.tempcondition = None

    # TODO Need to take condtion from the gui instead of here to stop when shutting down

    @QtCore.pyqtSlot()
    def stop(self):
        self.ui.gettingtemp = False

    @QtCore.pyqtSlot()
    def run(self):
        while self.ui.gettingtemp:
            andor.gettemperature()
            self.ui.CameraTemp_temp_actual.setText(str(andor.temperature))
            time.sleep(4)


class AcquireThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(AcquireThread, self).__init__()
        self.signals = WorkerSignals()
        self.ui = ui
        self.acquirecondition = None

        self.width = andor.width

    @QtCore.pyqtSlot()
    def run(self):
        toggle.deactivate_buttons(self.ui, main_start_acq_stat=True, spectralacq_update_stat=True)
        post.status(self.ui, 'Acquiring...')
        self.ui.Main_start_acq.setText('Stop Acquisition')

        self.ui.Main_specwin.clear()
        track1plot = self.ui.Main_specwin.plot()
        track2plot = self.ui.Main_specwin.plot()
        diffplot = self.ui.Main_specwin.plot()

        andor.setacquisitionmode(1)
        andor.setshutter(1, 1, 0, 0)

        # self.acquirecondition = True
        # while self.acquirecondition:
        while self.ui.acquiring:
            andor.setexposuretime(self.ui.exposuretime)
            andor.startacquisition()
            andor.waitforacquisition()
            andor.getacquireddata()

            track1plot.setData(andor.imagearray[0:self.width - 1], pen='r', name='track1')
            track2plot.setData(andor.imagearray[self.width:(2 * self.width) - 1], pen='g', name='track2')
            diffplot.setData(andor.imagearray[self.width:(2 * self.width) - 1] - andor.imagearray[0:self.width - 1],
                             pen='w', name='trackdiff')

            andor.freeinternalmemory()

            QApplication.processEvents()


class AcquireTest(QtCore.QThread):
    def __init__(self, ui):
        super(AcquireTest, self).__init__(ui)
        self.signals = WorkerSignals()
        self.ui = ui
        self.acquirecondition = None

        self.width = andor.width

    # @QtCore.pyqtSlot()
    def stop(self):
        toggle.activate_buttons(self.ui)
        post.status(self.ui, '')
        self.ui.Main_start_acq.setText('Start Acquisition')

        self.acquirecondition = False
        andor.setshutter(1, 2, 0, 0)

        # self.signals.finishedAcquireStop.emit()

    @QtCore.pyqtSlot()
    def run(self):
        toggle.deactivate_buttons(self.ui, main_start_acq_stat=True, spectralacq_update_stat=True)
        post.status(self.ui, 'Acquiring...')
        self.ui.Main_start_acq.setText('Stop Acquisition')

        self.ui.Main_specwin.clear()
        track1plot = self.ui.Main_specwin.plot()
        track2plot = self.ui.Main_specwin.plot()
        diffplot = self.ui.Main_specwin.plot()

        andor.setacquisitionmode(1)
        andor.setshutter(1, 1, 0, 0)

        # self.acquirecondition = True
        # while self.acquirecondition:
        while self.ui.acquiring:
            andor.setexposuretime(self.ui.exposuretime)
            andor.startacquisition()
            andor.waitforacquisition()
            andor.getacquireddata()

            track1plot.setData(andor.imagearray[0:self.width - 1], pen='r', name='track1')
            track2plot.setData(andor.imagearray[self.width:(2 * self.width) - 1], pen='g', name='track2')
            diffplot.setData(andor.imagearray[self.width:(2 * self.width) - 1] - andor.imagearray[0:self.width - 1],
                             pen='w', name='trackdiff')

            andor.freeinternalmemory()

            QApplication.processEvents()


class SpectralThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(SpectralThread, self).__init__()
        self.ui = ui

    @QtCore.pyqtSlot()
    def run(self):
        self.ui.spectralacquiring = True
        post.status(self.ui, 'Spectral acquisition in progress...')

        exposuretime = float(self.ui.SpectralAcq_time_req.text())
        frames = int(self.ui.SpectralAcq_frames.text())
        darkcount = int(self.ui.SpectralAcq_darkfield.text())

        # Darkcount acquisitions
        andor.setacquisitionmode(3)
        andor.setshutter(1, 2, 0, 0)
        andor.setexposuretime(float(self.ui.darkexposure))
        andor.setnumberaccumulations(1)
        andor.setnumberkinetics(100)    # Need to change back to normal
        andor.setkineticcycletime(0.05)

        time.sleep(2)

        error = andor.startacquisition()
        andor.waitforacquisition()
        andor.getacquireddata_kinetic(100)  # Need to change back
        darkcount_data = andor.imagearray

        print(error)
        print('darkcount finished')

        # Spectral acquisitions
        andor.setshutter(1, 1, 0, 0)
        andor.setexposuretime(exposuretime)
        andor.setnumberkinetics(100)    # Need to change back to normal
        andor.setacquisitionmode(3)

        time.sleep(2)

        andor.startacquisition()
        andor.waitforacquisition()
        andor.getacquireddata_kinetic(100)  # Need to change back
        spectral_data = andor.imagearray

        print('spectra finished')

        # Post-process
        acquireddata = spectral_data - np.mean(darkcount_data, 0)

        self.ui.Main_specwin.clear()
        self.ui.Main_specwin.plot(spectral_data[5, 0:511])
        self.ui.Main_specwin.plot(spectral_data[5, 512:1023])

        print('postprocess finished')

        post.status(self.ui, '')
        self.ui.spectralacquiring = False


class HyperspectralThread(QtCore.QRunnable):
    pass


# from scancars.gui.forms import main
#
#
# class TestThread(QtCore.QRunnable, main.Ui_MainWindow):
#     def __init__(self):
#         super(TestThread, self).__init__()
#         self.
