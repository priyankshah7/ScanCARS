import time, ctypes
import multiprocessing as mp
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore

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
            self.ui.cameratempActualTemp.setText(str(self.ui.andor.temperature))
            time.sleep(4)


# class ShutDown(QtCore.QRunnable):
#     def __init__(self, ui):
#         super(ShutDown, self).__init__()
#         self.ui = ui
#
#     @QtCore.pyqtSlot()
#     def run(self):
#         self.ui.acquiring = False
#         self.ui.gettingtemp = False
#
#         self.ui.andor.setshutter(1, 2, 0, 0)
#         self.ui.andor.iscooleron()
#         self.ui.andor.gettemperature()
#
#         if self.ui.andor.coolerstatus == 0 and self.ui.andor.temperature


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

