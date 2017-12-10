# ScanCARS v1
# Software to control the SIPCARS experimental setup
# Priyank Shah - King's College London

import sys
import time
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore

from guiForms import WindowMAIN
from guiFunctions import toggle, post
from guiFunctions.graphing import *
from guiMain import Initialize, Main, CameraTemp, Grating, CameraOptions, SpectralAcq, HyperAcq

from AndorSDK.pyandor import Andor


class ScanCARS(QMainWindow, WindowMAIN.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ScanCARS, self).__init__(parent)
        self.setupUi(self)

        # TODO Add options to take individual pump/Stokes. Will depend on being able to code up some shutters.
        # TODO Change textboxes to spin boxes where relevant
        # TODO If speed becomes an issue, consider using numba package with jit decorator
            # Required to use maths functions instead of numpy
        # TODO Move all non-GUI functions to separate threads

        # TODO Reconsidering separating main functions completely.......

        # ------------------------------------------------------------------------------------------------------------
        # Importing relevant methods and classes
        self.post = post
        self.threadpool = QtCore.QThreadPool()

        # Creating variables for tracks (perhaps create function here instead)
        self.track1 = None
        self.track2 = None
        self.trackdiff = None
        self.tracksum = None

        # Main: connecting buttons to functions
        self.Main_start_acq.clicked.connect(lambda: self.main_startacq())
        self.Main_shutdown.clicked.connect(lambda: self.main_shutdown())

        # CameraTemp: connecting buttons to functions
        self.CameraTemp_cooler_on.clicked.connect(lambda: self.cameratemp_cooler())

        # SpectraWin: connecting buttons to functions
        self.SpectraWin_single_track.clicked.connect(lambda: self.spectrawin_tracks())
        self.SpectraWin_sum_track.clicked.connect(lambda: self.spectrawin_sum())

        # Grating: connecting buttons to functions
        self.Grating_update.clicked.connect(lambda: self.grating_update())

        # CameraOptions: connecting buttons to functions
        self.CameraOptions_update.clicked.connect(lambda: self.cameraoptions_update())
        self.CameraOptions_openimage.clicked.connect(lambda: self.cameraoptions_openimage())

        # SpectralAcq: connecting buttons to functions
        self.SpectralAcq_update_time.clicked.connect(lambda: self.spectralacq_updatetime())
        self.SpectralAcq_start.clicked.connect(lambda: self.spectralacq_start())

        # HyperAcq: connecting buttons to functions
        self.HyperAcq_start.clicked.connect(lambda: self.hyperacq_start())

        # ------------------------------------------------------------------------------------------------------------

        # ------------------------------------------------------------------------------------------------------------
        # Startup Processes
        post.event_date(self)

        # Initializing the camera
        self.cam = Andor()
        self.initialize_andor()
        # TODO Working, but there's an issue with the comment showing up in the event dialog

        # ------------------------------------------------------------------------------------------------------------

    def __del__(self):
        post.eventlog(self, 'An error has occurred. This program will exit after the Andor camera has shut down.')

        messageCoolerOFF = self.cam.CoolerOFF()
        if messageCoolerOFF is not None:
            post.eventlog(self, messageCoolerOFF)

        messageShutDown = self.cam.ShutDown()
        if messageShutDown is not None:
            post.eventlog(self, messageShutDown)

    # Initialize: defining functions
    def initialize_andor(self):
        initialize = Initialize.Andor(self)
        self.threadpool.start(initialize)
        initialize.signals.finished.connect(lambda: initialize_event())

        def initialize_event():
            post.eventlog(self, 'Andor: Successfully initialized.')
            gettemperature = CameraTemp.AndorTemperature(self)
            self.threadpool.start(gettemperature)

    # Main: defining functions
    def main_startacq(self):
        # If acquisition is not alreadly running:
        if self.Main_start_acq.text() == 'Start Acquisition':
            # Setting the acquisition mode to single scan
            messageSetAcquisitionMode = self.cam.SetAcquisitionMode(1)
            if messageSetAcquisitionMode is not None:
                post.eventlog(self, messageSetAcquisitionMode)
                return

            messageSetExposureTime = self.cam.SetExposureTime(float(self.SpectralAcq_time_req.text()))
            if messageSetExposureTime is not None:
                post.eventlog(self, messageSetExposureTime)
                return

            messageGetAcquisitionTimings = self.cam.GetAcquisitionTimings()
            if messageGetAcquisitionTimings is not None:
                post.eventlog(self, messageGetAcquisitionTimings)
                return
            else:
                self.SpectralAcq_actual_time.setText(str("%.4f" % round(self.cam.exposure, 4)))

            messageSetShutter = self.cam.SetShutter(1, 0, 0, 0)
            if messageSetShutter is not None:
                post.eventlog(self, messageSetShutter)
                return

            # ... functions to start acquiring ...

            messageStartAcquisition = self.cam.StartAcquisition()
            if messageStartAcquisition is not None:
                post.eventlog(self, messageStartAcquisition)
                self.cam.AbortAcquisition()
                return
            else:
                # post.status(self, 'Acquiring...')
                # self.Main_start_acq.setText('Stop Acquisition')

                self.cam.GetAcquiredData16()

                post.eventlog(self, str(type(self.cam.imagearray)))

                # self.track1 = self.cam.imagearray[0:self.cam.width-1]
                # self.track2 = self.cam.imagearray[self.cam.width:2*self.cam.width - 1]
                # self.trackdiff = self.track2 - self.track1
                # self.tracksum = self.track1 + self.track2

                # # Plotting tracks and different spectra
                # self.Main_specwin.clear()
                # self.Main_specwin.plot(self.track1, pen='r', name='track1')
                # self.Main_specwin.plot(self.track2, pen='g', name='track2')
                # self.Main_specwin.plot(self.trackdiff, pen='w', name='trackdiff')

            post.status(self, 'Acquiring...')

        # If acquisition is to be stopped:
        elif self.Main_start_acq.text() == 'Stop Acquisition':
            post.status(self, '')
            self.Main_start_acq.setText('Start Acquisition')

    def main_shutdown(self):
        messageIsCoolerOn = self.cam.IsCoolerOn()
        if messageIsCoolerOn is not None:
            post.eventlog(self, messageIsCoolerOn)

        else:
            if self.cam.coolerstatus == 0:
                messageShutDown = self.cam.ShutDown()
                if messageShutDown is not None:
                    post.eventlog(self, messageShutDown)

                post.eventlog(self, 'ScanCARS can now be safely closed.')

            elif self.cam.coolerstatus == 1:
                cooleroff = CameraTemp.CoolerOff(self)
                self.threadpool.start(cooleroff)
                cooleroff.signals.finished.connect(lambda: post.eventlog(self, 'Andor: Cooler switched off...'))
                self.CameraTemp_temp_actual.setStyleSheet("QLineEdit {background: #191919}")

                post.eventlog(self, '...waiting for the camera to heat up to -20C')

                while self.cam.temperature < -20:
                    pass

                else:
                    messageShutDown = self.cam.ShutDown()
                    if messageShutDown is not None:
                        post.eventlog(self, messageShutDown)

                post.eventlog(self, 'ScanCARS can now be safely closed.')

    # CameraTemp: defining functions
    def cameratemp_cooler(self):
        messageIsCoolerOn = self.cam.IsCoolerOn()
        if messageIsCoolerOn is not None:
            post.eventlog(self, messageIsCoolerOn)

        else:
            if self.cam.coolerstatus == 0:
                cooleron = CameraTemp.CoolerOn(self)
                self.threadpool.start(cooleron)
                cooleron.signals.finished.connect(lambda: post.eventlog(self, 'Andor: Cooler on.'))
                self.CameraTemp_temp_actual.setStyleSheet("QLineEdit {background: #323e30}")

            elif self.cam.coolerstatus == 1:
                cooleroff = CameraTemp.CoolerOff(self)
                self.threadpool.start(cooleroff)
                cooleroff.signals.finished.connect(lambda: post.eventlog(self, 'Andor: Cooler switched off.'))
                self.CameraTemp_temp_actual.setStyleSheet("QLineEdit {background: #191919}")

            else:
                post.eventlog(self, 'An error has occured. Possibly related to the GUI itself?')

    # SpectraWin: defining functions
    def spectrawin_tracks(self):
        pass

    def spectrawin_sum(self):
        pass

    # Grating: defining functions

    # CameraOptions: defining functions
    def cameraoptions_update(self):
        update = CameraOptions.Update(self)
        self.threadpool.start(update)

    # SpectralAcq: defining functions
    def spectralacq_updatetime(self):
        messageSetExposureTime = self.cam.SetExposureTime(float(self.SpectralAcq_time_req.text()))
        if messageSetExposureTime is not None:
            post.eventlog(self, messageSetExposureTime)

        # To retrieve the data
        # messageGetAcquiredData16 = self.cam.GetAcquiredData16()
        # if messageGetAcquiredData16 is not None:
        #     post.eventlog(self, messageGetAcquiredData16)

    def spectralacq_start(self):
        time_req = float(self.SpectralAcq_update_time.text())
        darkfield_req = int(self.SpectralAcq_darkfield.text())

    # HyperAcq: defining functions
    def hyperacq_start(self):
        xpixel = int(self.HyperAcq_xpixel.text())
        ypixel = int(self.HyperAcq_ypixel.text())
        zpixel = int(self.HyperAcq_zpixel.text())

        xystep = float(self.HyperAcq_xystep.text())
        zstep = float(self.HyperAcq_zstep.text())

        time_req = float(self.HyperAcq_time_req.text())
        darkfield_req = int(self.HyperAcq_darkfield.text())


def main():
    app = QApplication(sys.argv)
    form = ScanCARS()
    form.setWindowTitle('ScanCARS')
    form.show()
    sys.exit(app.exec_())


# If the file is run directly and not imported, this runs the main function
if __name__ == '__main__':
    main()
