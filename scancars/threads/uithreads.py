import time, ctypes
import multiprocessing as mp
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore

from scancars.sdk.andor.pyandor import Cam
from scancars.gui.forms import main
from scancars.utils import toggle, post


class WorkerSignals(QtCore.QObject):
    finishedAcquire = QtCore.pyqtSignal()
    finishedAcquireStop = QtCore.pyqtSignal()


class TempProcess:
    # Attempting to use multiprocessing here instead of multithreading. (FIXME)
    def __init__(self, ui):
        self.ui = ui

    def start(self):
        p = mp.Process(target=self.worker())
        p.start()

    def stop(self):
        self.ui.tempcondition = None

    def worker(self):
        while self.ui.gettingtemp:
            self.ui.andor.gettemperature()
            self.ui.CameraTemp_temp_actual.setText(str(self.ui.andor.temperature))
            time.sleep(4)


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
            self.ui.andor.gettemperature()
            self.ui.CameraTemp_temp_actual.setText(str(self.ui.andor.temperature))
            time.sleep(4)


class AcquireThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(AcquireThread, self).__init__()
        self.signals = WorkerSignals()
        self.ui = ui
        self.acquirecondition = None

        self.width = self.ui.andor.width

    @QtCore.pyqtSlot()
    def run(self):
        # Test bringing this into the main gui (TODO)???
        toggle.deactivate_buttons(self.ui, main_start_acq_stat=True)
        post.status(self.ui, 'Acquiring...')
        self.ui.Main_start_acq.setText('Stop Acquisition')

        self.ui.Main_specwin.clear()
        self.ui.Main_specwin.setXRange(-10, 520, padding=0)
        track1plot = self.ui.Main_specwin.plot(pen='r', name='track1')
        track2plot = self.ui.Main_specwin.plot(pen='g', name='track2')
        diffplot = self.ui.Main_specwin.plot(pen='w', name='trackdiff')

        cimage = (ctypes.c_int * self.ui.andor.dim)()

        self.ui.andor.freeinternalmemory()
        self.ui.andor.setacquisitionmode(1)
        self.ui.andor.setshutter(1, 1, 0, 0)
        self.ui.andor.setexposuretime(self.ui.exposuretime)

        while self.ui.acquiring:
            self.ui.andor.startacquisition()
            self.ui.andor.waitforacquisition()
            # self.ui.andor.getstatus()
            # while self.ui.andor.getstatusval == 'DRV_ACQUIRING':
            #     time.sleep(self.ui.exposuretime / 10)
            #     self.ui.andor.getstatus()

            self.ui.andor.getacquireddata(cimage)

            track1plot.setData(self.ui.andor.imagearray[0:self.width - 1])
            track2plot.setData(self.ui.andor.imagearray[self.width:(2 * self.width) - 1])
            diffplot.setData(
                self.ui.andor.imagearray[self.width:(2 * self.width) - 1] - self.ui.andor.imagearray[0:self.width - 1],)


# class AcquireTest(QtCore.QThread):
#     def __init__(self, ui):
#         super(AcquireTest, self).__init__(ui)
#         self.signals = WorkerSignals()
#         self.ui = ui
#         self.acquirecondition = None
#
#         self.width = andor.width
#
#     # @QtCore.pyqtSlot()
#     def stop(self):
#         toggle.activate_buttons(self.ui)
#         post.status(self.ui, '')
#         self.ui.Main_start_acq.setText('Start Acquisition')
#
#         self.acquirecondition = False
#         andor.setshutter(1, 2, 0, 0)

        # self.signals.finishedAcquireStop.emit()
    #
    # @QtCore.pyqtSlot()
    # def run(self):
    #     toggle.deactivate_buttons(self.ui, main_start_acq_stat=True, spectralacq_update_stat=True)
    #     post.status(self.ui, 'Acquiring...')
    #     self.ui.Main_start_acq.setText('Stop Acquisition')
    #
    #     self.ui.Main_specwin.clear()
    #     track1plot = self.ui.Main_specwin.plot()
    #     track2plot = self.ui.Main_specwin.plot()
    #     diffplot = self.ui.Main_specwin.plot()
    #
    #     andor.setacquisitionmode(1)
    #     andor.setshutter(1, 1, 0, 0)
    #
    #     # self.acquirecondition = True
    #     # while self.acquirecondition:
    #     while self.ui.acquiring:
    #         andor.setexposuretime(self.ui.exposuretime)
    #         andor.startacquisition()
    #         andor.waitforacquisition()
    #         andor.getacquireddata()
    #
    #         track1plot.setData(andor.imagearray[0:self.width - 1], pen='r', name='track1')
    #         track2plot.setData(andor.imagearray[self.width:(2 * self.width) - 1], pen='g', name='track2')
    #         diffplot.setData(andor.imagearray[self.width:(2 * self.width) - 1] - andor.imagearray[0:self.width - 1],
    #                          pen='w', name='trackdiff')
    #
    #         andor.freeinternalmemory()
    #
    #         QApplication.processEvents()


class SpectralThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(SpectralThread, self).__init__()
        self.ui = ui

    @QtCore.pyqtSlot()
    def run(self):
        toggle.deactivate_buttons(self.ui)
        self.ui.spectralacquiring = True
        post.status(self.ui, 'Spectral acquisition in progress...')

        exposuretime = float(self.ui.SpectralAcq_time_req.text())
        frames = int(self.ui.SpectralAcq_frames.text())
        darkcount = int(self.ui.SpectralAcq_darkfield.text())

        # Expected time
        total = (darkcount * self.ui.darkexposure) + (frames * exposuretime)
        progress_darkcount = ((darkcount * self.ui.darkexposure)/total) * 100

        # Darkcount acquisitions
        self.ui.andor.setacquisitionmode(3)
        self.ui.andor.setshutter(1, 2, 0, 0)
        self.ui.andor.setexposuretime(float(self.ui.darkexposure))
        self.ui.andor.setnumberaccumulations(1)
        self.ui.andor.setnumberkinetics(darkcount)
        self.ui.andor.setkineticcycletime(0.05)

        time.sleep(2)

        self.ui.andor.startacquisition()

        self.ui.andor.getstatus()
        while self.ui.andor.getstatusval == 'DRV_ACQUIRING':
            time.sleep(self.ui.darkexposure/10)
            self.ui.andor.getstatus()

        self.ui.andor.getacquireddata_kinetic(darkcount)
        darkcount_data = self.ui.andor.imagearray

        self.ui.Main_progress.setValue(progress_darkcount)

        # Spectral acquisitions
        self.ui.andor.setshutter(1, 1, 0, 0)
        self.ui.andor.setexposuretime(exposuretime)
        self.ui.andor.setnumberkinetics(frames)
        self.ui.andor.setacquisitionmode(3)

        time.sleep(2)

        self.ui.andor.startacquisition()

        self.ui.andor.getstatus()
        while self.ui.andor.getstatusval == 'DRV_ACQUIRING':
            time.sleep(exposuretime/10)
            self.ui.andor.getstatus()

        self.ui.andor.getacquireddata_kinetic(frames)
        spectral_data = self.ui.andor.imagearray

        # Post-process
        acquireddata = np.mean(spectral_data, 1) - np.mean(darkcount_data, 1)

        self.ui.Main_specwin.clear()
        self.ui.Main_specwin.plot(acquireddata[0:511], pen='r')
        self.ui.Main_specwin.plot(acquireddata[512:1023], pen='g')
        self.ui.Main_specwin.plot(acquireddata[512:1023]-acquireddata[0:511], pen='w')

        post.status(self.ui, '')
        self.ui.spectralacquiring = False
        self.ui.Main_progress.setValue(100)
        toggle.activate_buttons(self.ui)


class HyperspectralThread(QtCore.QRunnable):
    pass


# from scancars.gui.forms import main
#
#
# class TestThread(QtCore.QRunnable, main.Ui_MainWindow):
#     def __init__(self):
#         super(TestThread, self).__init__()
#         self.
