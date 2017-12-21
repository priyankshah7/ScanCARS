import time
from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject

from scancars.sdk.andor import Cam

andor = Cam()


class Signals(QObject):
    finished = pyqtSignal()


class AndorTemperature(QRunnable):
    def __init__(self, ui):
        super(AndorTemperature, self).__init__()
        self.ui = ui
        self.signals = Signals()
        self.condition = True

    @pyqtSlot()
    def stop(self):
        self.condition = False

    @pyqtSlot()
    def run(self):
        self.condition = True

        while self.condition:
            andor.gettemperature()
            self.ui.CameraTemp_temp_actual.setText(str(andor.temperature))
            time.sleep(2)
