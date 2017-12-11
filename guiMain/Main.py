from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject

import time


class StartAcq(QRunnable):
    def __init__(self, gui):
        super(StartAcq, self).__init__()
        self.gui = gui
        self.condition = True
        self.exposurereq = float(self.gui.SpectralAcq_time_req.text())

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
        # TODO add code to stop acquisition as well

    @pyqtSlot()
    def run(self):
        messageSetAcquisitionMode = self.gui.cam.SetAcquisitionMode(1)
        if messageSetAcquisitionMode is not None:
            self.gui.post.eventlog(self.gui, messageSetAcquisitionMode)
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

        while self.condition:
            messageSetExposureTime = self.gui.cam.SetExposureTime(self.exposurereq)
            if messageSetExposureTime is not None:
                self.gui.post.eventlog(self.gui, messageSetExposureTime)
                return

            messageStartAcquisition = self.gui.cam.StartAcquisition()
            if messageStartAcquisition is not None:
                self.gui.post.eventlog(self.gui, messageStartAcquisition)
                self.gui.cam.AbortAcquisition()
                return

            else:
                self.gui.post.eventlog(self.gui, 'Acquiring...')
                self.gui.Main_start_acq.setText('Stop Acquisition')

                self.gui.cam.GetAcquiredData16()

                self.gui.post.eventlog(self.gui, str(type(self.gui.cam.imagearray)))

                # TODO if using, make sure to include self.gui
                # self.track1 = self.cam.imagearray[0:self.cam.width-1]
                # self.track2 = self.cam.imagearray[self.cam.width:2*self.cam.width - 1]
                # self.trackdiff = self.track2 - self.track1
                # self.tracksum = self.track1 + self.track2

                # # Plotting tracks and different spectra
                # self.Main_specwin.clear()
                # self.Main_specwin.plot(self.track1, pen='r', name='track1')
                # self.Main_specwin.plot(self.track2, pen='g', name='track2')
                # self.Main_specwin.plot(self.trackdiff, pen='w', name='trackdiff')

            self.gui.post.status(self.gui, 'Acquiring...')


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
