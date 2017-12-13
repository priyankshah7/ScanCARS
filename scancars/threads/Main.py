from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject

import time


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

        messageGetStatus = self.gui.cam.GetStatus()
        if messageGetStatus == 'DRV_ACQUIRING':
            self.gui.cam.AbortAcquisition()

        # TODO add code to stop acquisition as well

    @pyqtSlot()
    def run(self):
        messageSetAcquisitionMode = self.gui.cam.SetAcquisitionMode(1)
        if messageSetAcquisitionMode is not None:
            self.gui.post.eventlog(self.gui, messageSetAcquisitionMode)
            return

        messageSetShutter = self.gui.cam.SetShutter(1, 1, 0, 0)
        if messageSetShutter is not None:
            self.gui.post.eventlog(self.gui, messageSetShutter)
            return

        self.gui.post.status(self.gui, 'Acquiring...')
        self.gui.Main_start_acq.setText('Stop Acquisition')

        self.exposurereq = float(self.gui.SpectralAcq_time_req.text())

        while self.condition:
            # messageSetExposureTime = self.gui.cam.SetExposureTime(self.exposurereq)
            # if messageSetExposureTime is not None:
            #     self.gui.post.eventlog(self.gui, messageSetExposureTime)
            #     return
            #
            # messageGetAcquisitionTimings = self.gui.cam.GetAcquisitionTimings()
            # if messageGetAcquisitionTimings is not None:
            #     self.gui.post.eventlog(self.gui, messageGetAcquisitionTimings)
            #     return
            # else:
            #     self.gui.SpectralAcq_actual_time.setText(str("%.4f" % round(self.gui.cam.exposure, 4)))

            messageStartAcquisition = self.gui.cam.StartAcquisition()
            if messageStartAcquisition is not None:
                self.gui.post.eventlog(self.gui, messageStartAcquisition)
                self.gui.cam.AbortAcquisition()
                return

            time.sleep(self.exposurereq)

            messageGetStatus = self.gui.cam.GetStatus()
            if messageGetStatus == 'DRV_IDLE':
                messageGetAcquiredData = self.gui.cam.GetAcquiredData()
                if messageGetAcquiredData is not None:
                    self.gui.post.eventlog(self.gui, messageGetAcquiredData)
                    return

                else:
                    self.track1 = self.gui.cam.imagearray[0:self.width-1]
                    self.track2 = self.gui.cam.imagearray[self.width:2 * self.width - 1]
                    self.trackdiff = self.track2 - self.track1
                    self.tracksum = self.track1 + self.track2

                    self.gui.Main_specwin.clear()
                    self.gui.Main_specwin.plot(self.track1, pen='r', name='track1')
                    self.gui.Main_specwin.plot(self.track2, pen='g', name='track2')
                    self.gui.Main_specwin.plot(self.trackdiff, pen='w', name='trackdiff')

            # TODO Need to include GetStatus() here as well to know when the acquisition is complete

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

