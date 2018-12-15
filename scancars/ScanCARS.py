import sys
import configparser
import subprocess
from PyQt5 import QtCore
from PyQt5.Qt import QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyleFactory

from scancars.gui import dialogs
from scancars.gui.forms import main as main_window
from scancars.utils import post
from scancars.sdk.andor import pyandor
from scancars.src import (
    initialize_andor, initialize_isoplane, main_startacq, main_shutdown, cameratemp_cooler,
    grating_update, grating_state, camtracks_view, camtracks_update, spectralacq_update,
    spectralacq_start, hyperacq_start, hyperacq_update_time
)


class ScanCARS(QMainWindow, main_window.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ScanCARS, self).__init__(parent)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle('ScanCARS')

        # TODO Add options to take individual pump/Stokes. Will depend on being able to code up some shutters.
        # TODO Add control for the Nikon microscope with micro-manager

        # NOTE To build, run: pyinstaller --onefile --windowed build.spec

        # ------- STARTUP PROCESSES ---------------------------------------------------------

        # Retrieving config values
        config = configparser.ConfigParser()
        config.read('config.ini')
        default_vals = config['DEFAULT']
        self.camtrackLower1.setValue(default_vals.getint('camtrackLower1'))
        self.camtrackUpper1.setValue(default_vals.getint('camtrackUpper1'))
        self.camtrackLower2.setValue(default_vals.getint('camtrackLower2'))
        self.camtrackUpper2.setValue(default_vals.getint('camtrackUpper2'))
        self.spectralRequiredTime.setValue(default_vals.getfloat('spec_exposuretime'))
        self.spectralBackgroundFrames.setValue(default_vals.getint('spec_background_frames'))
        self.spectralFrames.setValue(default_vals.getint('spec_spectral_frames'))
        self.hyperspectralRequiredTime.setValue(default_vals.getfloat('hyp_exposuretime'))
        self.hyperspectralBackgroundFrames.setValue(default_vals.getint('hyp_background_frames'))
        self.hyperspectralXPix.setValue(default_vals.getint('num_x_pix'))
        self.hyperspectralYPix.setValue(default_vals.getint('num_y_pix'))
        self.hyperspectralZPix.setValue(default_vals.getint('num_z_pix'))
        self.hyperspectralXYStep.setValue(default_vals.getfloat('xy_step'))
        self.hyperspectralZStep.setValue(default_vals.getfloat('z_step'))
        self.cameratempRequiredTemp.setValue(default_vals.getint('temp'))

        # Initiating instances of a threadpool and the Andor class
        self.threadpool = QtCore.QThreadPool()
        self.andor = pyandor.Cam()

        # Variables for acquisition and temp. monitoring loops
        self.acquiring = False
        self.ccdacquiring = False
        self.spectralacquiring = False
        self.hyperacquiring = False
        self.acquisition_cancelled = False
        self.gettingtemp = False
        self.grating = False

        # Data variables
        self.spectral_data = None
        self.hyperspectral_data = None

        # Storing exposure times
        self.exposuretime = float(self.spectralRequiredTime.text())
        self.darkexposure = 0.1

        # Creating variables to store instances of the camera and track/sum dialogs
        self.winspecsum = dialogs.SPECSUM()
        self.winspecsum.setWindowTitle('Sum Track Spectrum')
        self.winspecdiff = dialogs.SPECDIFF()
        self.winspecdiff.setWindowTitle('Difference Track Spectrum')
        self.winccdlive = dialogs.CCDLIVE()
        self.winccdlive.setWindowTitle('Live CCD View')

        # Plot/Image settings
        self.specwinMain.plotItem.showGrid(x=True, y=True, alpha=0.2)
        self.specwinPrevious.plotItem.showGrid(x=True, y=True, alpha=0.2)
        self.specwinMain.setXRange(-10, 1030, padding=0)
        self.specwinPrevious.setXRange(-10, 1030, padding=0)
        self.specwinMain.plotItem.setMenuEnabled(False)
        self.specwinPrevious.plotItem.setMenuEnabled(False)
        self.imagewinMain.ui.histogram.setMinimumWidth(10)
        self.imagewinMain.ui.histogram.vb.setMinimumWidth(5)
        self.imagewinMain.ui.roiBtn.hide()
        self.imagewinMain.ui.menuBtn.hide()

        self.specwinMain.clear()
        self.winspecsum.specwinSum.clear()
        self.winspecdiff.specwinDiff.clear()
        self.track1plot = self.specwinMain.plot(pen=(190, 70, 45), name='track1')
        self.track2plot = self.specwinMain.plot(pen=(25, 85, 120), name='track2')
        self.diffplot = self.specwinMain.plot(pen='w', name='trackdiff')
        self.sumdialogplot = self.winspecsum.specwinSum.plot(pen=(25, 85, 120), name='sum')
        self.diffdialogplot = self.winspecdiff.specwinDiff.plot(pen=(25, 85, 120), name='difference')
        self.previousplot = self.specwinPrevious.plot(pen='w', name='previousdiff')

        # Hyperspectral imaging settings
        hyperacq_update_time(self)

        # Connecting buttons to methods
        self.buttonMainStartAcquisition.clicked.connect(lambda: main_startacq(self))
        self.buttonMainShutdown.clicked.connect(lambda: main_shutdown(self))
        self.buttonCameratempCooler.clicked.connect(lambda: cameratemp_cooler(self))
        self.buttonDialogsDifference.clicked.connect(lambda: self.winspecdiff.show())
        self.buttonDialogsSum.clicked.connect(lambda: self.winspecsum.show())
        self.buttonGratingUpdate.clicked.connect(lambda: grating_update(self))
        self.buttonGratingState.clicked.connect(lambda: grating_state(self))
        self.buttonCamtrackUpdate.clicked.connect(lambda: camtracks_update(self))
        self.buttonCamtrackView.clicked.connect(lambda: camtracks_view(self))
        self.buttonSpectralUpdate.clicked.connect(lambda: spectralacq_update(self))
        self.buttonSpectralStart.clicked.connect(lambda: spectralacq_start(self))
        self.buttonHyperspectralStart.clicked.connect(lambda: hyperacq_start(self))
        self.buttonHyperspectralTime.clicked.connect(lambda: hyperacq_update_time(self))
        self.actionOpen_Data_Folder.triggered.connect(lambda: self.open_data_folder())

        # Initialising the camera
        initialize_andor(self)
        self.width = self.andor.width

        # Initialising the PI Isoplane if it is able to connect
        # self.isoplane = None
        # initialize_isoplane(self)

        # Misc
        self.progressbar.setValue(0)

    # Menu functions
    @staticmethod
    def open_data_folder():
        subprocess.Popen('explorer "C:\\Users\\CARS\\Documents\\SIPCARS\\Data"')

    def closeEvent(self, event):
        # Method to carry out operations upon closing the main window
        self.andor.iscooleron()
        error_setshutter = self.andor.setshutter(1, 2, 0, 0)
        if self.andor.coolerstatus == 1 or error_setshutter == 'DRV_SUCCESS':
            event.ignore()
            post.eventlog(self, 'ScanCARS needs to SHUTDOWN first.')

        else:
            if self.winspecsum.isVisible() or self.winspecdiff.isVisible():
                self.winspecsum.close()
                self.winspecdiff.close()


def main():
    app = QApplication(sys.argv)

    # Setting the dark-themed Fusion style for the GUI
    app.setStyle(QStyleFactory.create('Fusion'))
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(23, 23, 23))
    dark_palette.setColor(QPalette.WindowText, QColor(200, 200, 200))
    dark_palette.setColor(QPalette.Base, QColor(18, 18, 18))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, QColor(200, 200, 200))
    dark_palette.setColor(QPalette.Button, QColor(33, 33, 33))
    dark_palette.setColor(QPalette.ButtonText, QColor(200, 200, 200))
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    dark_palette.setColor(QPalette.Active, QPalette.Button, QColor(33, 33, 33))
    dark_palette.setColor(QPalette.Disabled, QPalette.Button, QColor(20, 20, 20))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 120, 120))
    app.setPalette(dark_palette)

    form = ScanCARS()
    form.show()
    sys.exit(app.exec_())


# If the file is run directly and not imported, this runs the main function
if __name__ == '__main__':
    main()
sys.exit(1)
