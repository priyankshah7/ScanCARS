import time, ctypes
from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject
from PyQt5 import QtCore

andordll = ctypes.cdll.LoadLibrary("C:\\Program Files\\Andor iXon\\Drivers\\atmcd64d")


class StartAcq(QRunnable):
    def __init__(self, gui):
        super(StartAcq, self).__init__()
        self.gui = gui
        self.condition = True
        self.exposurereq = None
        self.width = self.gui.cam.width
        self.track1 = None
        self.track2 = None
        self.trackdiff = None
        self.tracksum = None

    @pyqtSlot()
    def exposure(self):
        self.exposurereq = float(self.gui.SpectralAcq_time_req.text())
        messageGetAcquisitionTimings = self.gui.cam.GetAcquisitionTimings()
        if messageGetAcquisitionTimings is not None:
            self.gui.post.eventlog(self.gui, messageGetAcquisitionTimings)
            return
        else:
            self.gui.SpectralAcq_actual_time.setText(str("%.4f" % round(self.gui.cam.exposure, 4)))

    @pyqtSlot()
    def stop(self):
        self.condition = False
        self.gui.post.status(self.gui, '')
        self.gui.Main_start_acq.setText('Start Acquisition')

        # self.gui.cam.AbortAcquisition()
        andordll.AbortAcquisition()
        andordll.SetShutter(1, 2, 0, 0)

        # TODO add code to stop acquisition as well

    @pyqtSlot()
    def run(self):
        # messageSetAcquisitionMode = self.gui.cam.SetAcquisitionMode(1)
        # if messageSetAcquisitionMode is not None:
        #     self.gui.post.eventlog(self.gui, messageSetAcquisitionMode)
        #     return
        andordll.SetAcquisitionMode(1)

        # messageSetShutter = self.gui.cam.SetShutter(1, 1, 0, 0)
        # if messageSetShutter is not None:
        #     self.gui.post.eventlog(self.gui, messageSetShutter)
        #     return
        andordll.SetShutter(1, 1, 0, 0)

        self.gui.post.status(self.gui, 'Acquiring...')
        self.gui.Main_start_acq.setText('Stop Acquisition')

        self.exposurereq = float(self.gui.SpectralAcq_time_req.text())

        self.condition = True
        while self.condition:
            # self.gui.cam.SetExposureTime(self.exposurereq)
            # self.gui.cam.StartAcquisition()
            andordll.SetExposureTime(ctypes.c_float(self.exposurereq))
            # andordll.StartAcquisition()
            #
            # # self.gui.cam.WaitForAcquisition()
            # andordll.WaitForAcquisition()
            #
            # imagearray = self.gui.cam.GetAcquiredData()
            #
            # self.track1 = imagearray[0:self.width-1]
            # self.track2 = imagearray[self.width:(2*self.width)-1]
            # self.trackdiff = self.track2 - self.track1
            # self.tracksum = self.track1 + self.track2
            #
            # self.gui.Main_specwin.clear()
            # self.gui.Main_specwin.plot(self.track1, pen='r', name='track1')
            # self.gui.Main_specwin.plot(self.track2, pen='g', name='track2')
            # self.gui.Main_specwin.plot(self.trackdiff, pen='w', name='trackdiff')

        #     # self.gui.cam.FreeInternalMemory()
        #     andordll.FreeInternalMemory()
        #     QtCore.QCoreApplication.processEvents()

        self.gui.post.eventlog(self.gui, 'stopped.')

            # TODO When completing the above, add checks to see if spectracks/specwin is open
                # isVis = self.winspectracks.isVisisble()
                # if the window is open it will return True (else it'll return False)


class Shutdown(QRunnable):
    def __init__(self, gui):
        super(Shutdown, self).__init__()
        self.gui = gui

    @pyqtSlot()
    def run(self):
        # TODO Do this here or on the GUI thread??
        messageCoolerOFF = self.gui.cam.CoolerOFF()
        if messageCoolerOFF is not None:
            self.gui.post.eventlog(self.gui, messageCoolerOFF)

