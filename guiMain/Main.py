from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject

import time


class StartAcq(QRunnable):
    def __init__(self, gui):
        super(StartAcq, self).__init__()
        self.gui = gui
        self.condition = True

    @pyqtSlot()
    def stop(self):
        self.condition = False

    @pyqtSlot()
    def run(self):
        messageSetAcquisitionMode = self.gui.cam.SetAcquisitionMode(1)
        if messageSetAcquisitionMode is not None:
            self.gui.post.eventlog(self.gui, messageSetAcquisitionMode)
            return

        messageSetExposureTime = self.gui.cam.SetExposureTime(float(self.gui.SpectralAcq_time_req.text()))
        if messageSetExposureTime is not None:
            self.gui.post.eventlog(self.gui, messageSetExposureTime)
            return

        messageGetAcquisitionTimings = self.gui.cam.GetAcquisitionTimings()
        if messageGetAcquisitionTimings is not None:
            self.gui.post.eventlog(self.gui, messageGetAcquisitionTimings)
            return
        else:
            self.gui.SpectralAcq_actual_time.setText(str("%.4f" % round(self.gui.cam.exposure, 4)))

        messageSetShutter = self.gui.cam.SetShutter(1, 0, 0, 0)
        if messageSetShutter is not None:
            self.gui.post.eventlog(self.gui, messageSetShutter)
            return

        # ... functions to start acquiring ...

        messageStartAcquisition = self.gui.cam.StartAcquisition()
        if messageStartAcquisition is not None:
            self.gui.post.eventlog(self.gui, messageStartAcquisition)
            self.gui.cam.AbortAcquisition()
            return

class Shutdown(QRunnable):
    def __init__(self, gui):
        super(Shutdown, self).__init__()
        self.gui = gui

    @pyqtSlot()
    def run(self):
        messageCoolerOFF = self.gui.cam.CoolerOFF()
        if messageCoolerOFF is not None:
            self.gui.post.eventlog(self.gui, messageCoolerOFF)

        else:
            self.gui.post.eventlog(self.gui, 'Andor: Waiting for camera to heat up (~2.5 minutes)...')
            time.sleep(150)

            messageShutDown = self.gui.cam.ShutDown()
            if messageShutDown is not None:
                self.gui.post.eventlog(self.gui, messageShutDown)
