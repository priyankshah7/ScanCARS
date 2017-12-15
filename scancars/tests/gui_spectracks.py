import sys, time
import numpy as np
from ctypes import *
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

from scancars.forms import WindowSPECTRACKS
from andorsdk.pyandor import Andor

class SPECTRACKS(QMainWindow, WindowSPECTRACKS.Ui_Dialog):
    def __init__(self, parent=None):
        super(SPECTRACKS, self).__init__(parent)
        self.setupUi(self)

        self.cam = Andor()
        self.cam.Initialize()
        self.cam.SetShutter(1, 2, 0, 0)
        self.cam.SetReadMode(2)

        RandomTrackposition = np.array([165, 198, 211, 244])

        self.cam.SetRandomTracks(2, RandomTrackposition)
        self.cam.GetNumberADChannels()
        self.cam.SetADChannel(1)
        self.cam.SetTriggerMode(0)
        self.cam.GetDetector()
        self.cam.SetHSSpeed(1, 0)
        self.cam.SetVSSpeed(3)


class StartAcq(QRunnable):
    def __init__(self):
        super(StartAcq, self).__init__()

        self.cam = Andor()

    @pyqtSlot()
    def run(self):
        self.cam.SetAcquisitionMode(1)
        self.cam.SetShutter(1, 1, 0, 0)

    def getdata(self):
        dim = 512 * 2
        imagearray = c_int * dim
        cimage = imagearray()

        messageGetData = dll.GetAcquiredData(pointer(cimage), dim)
        if messageGetData is not None:
            print(messageGetData)

        return cimage


def main():
    app = QApplication(sys.argv)
    form = SPECTRACKS()
    form.setWindowTitle('ScanCARS')
    form.show()
    sys.exit(app.exec_())


# If the file is run directly and not imported, this runs the main function
if __name__ == '__main__':
    main()