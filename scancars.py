# ScanCARS v1
# Software to control the SIPCARS experimental setup
# Priyank Shah - King's College London

import sys
import time
import clr
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore
import tkinter.filedialog
tkinter.Tk().withdraw()

from GUIWindows import WindowMAIN
from ADwinSDK import ADwin
from MyAndor.myandor import Andor


class ScanCARS(QMainWindow, WindowMAIN.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ScanCARS, self).__init__(parent)
        self.setupUi(self)

        # TODO Add options to take individual pump/Stokes. Will depend on being able to code up some shutters.
        # TODO Add a function to disable relevant buttons until camera has been cooled
        # TODO Change textboxes to spin boxes where relevant

        # ------------------------------------------------------------------------------------------------------------
        # Creating variables for tracks (perhaps create function here instead)
        self.track1 = self.track2 = self.track_diff = self.track_sum = None

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

        # Startup Processes
        self.event_date()
            # Connect to camera
            # Connect to ADwin

        # TODO Note that the number of returns aren't going to be the same as the number of error (1)
        #self.cam = Andor()
        #self.cam.Initialize()
        #cw, ch = self.cam.GetDetector()
        #self.cam.

        # TODO Follwing settings need to be used
        # SetReadMode(2)
        # SetAcquisitionMode(3) (check if kinetics or fast kinetics)
        # SetShutter(?, 0, ?, ?)
        # SetTriggerMode(0) double check this!


    # Main: defining functions
    def main_startacq(self):
        if self.Main_start_acq.text() == 'Start Acquisition':
            self.status('Acquiring...')
            self.Main_start_acq.setText('Stop Acquisition')

            time_req = float(self.SpectralAcq_time_req.text())

        elif self.Main_start_acq.text() == 'Stop Acquisition':
            self.status('')
            self.Main_start_acq.setText('Start Acquisition')

    def main_shutdown(self):
        pass

    # CameraTemp: defining functions
    def cameratemp_cooler(self):
        tempreq = int(self.CameraTemp_temp_req.text())
        self.cam.SetTemperature(tempreq)
        self.cam.CoolerON()

    # SpectraWin: defining functions
    def spectrawin_tracks(self):
        pass

    def spectrawin_sum(self):
        pass

    # Grating: defining functions
    def grating_update(self):
        pass

    # CameraOptions: defining functions
    def cameraoptions_update(self):
        track1_upper = int(self.CameraOptions_track1upper.text())
        track1_lower = int(self.CameraOptions_track1lower.text())
        track2_upper = int(self.CameraOptions_track2upper.text())
        track2_lower = int(self.CameraOptions_track2lower.text())

    def cameraoptions_openimage(self):
        pass

    # SpectralAcq: defining functions
    def spectralacq_updatetime(self):
        time_req = float(self.SpectralAcq_update_time.text())

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

    # Status: defining status and eventlog functions
    def status(self, message):
        self.Main_status.setText(message)

    def eventlog(self, message):
        self.EventLogger_box.appendPlainText('(' + time.strftime("%H:%M:%S") + ')' + ' - ' + message)

    def event_date(self):
        self.EventLogger_box.appendPlainText(
            '------------------------------------------------------------------------------------')
        self.EventLogger_box.appendPlainText(
            ' ScanCARS Software                                    Date: ' + time.strftime('%d/%m/%Y'))
        self.EventLogger_box.appendPlainText(
            '------------------------------------------------------------------------------------')


def main():
    app = QApplication(sys.argv)
    form = ScanCARS()
    form.setWindowTitle('ScanCARS v1')
    form.show()
    sys.exit(app.exec_())


# If the file is run directly and not imported, this runs the main function
if __name__ == '__main__':
    main()
