import time
from PyQt5 import QtCore


class MonitorTemperatureThread(QtCore.QRunnable):
    def __init__(self, ui):
        super(MonitorTemperatureThread, self).__init__()
        self.ui = ui
        self.mutex = QtCore.QMutex()

    @QtCore.pyqtSlot()
    def stop(self):
        self.mutex.lock()
        self.ui.gettingtemp = False
        self.mutex.unlock()

    @QtCore.pyqtSlot()
    def run(self):
        while self.ui.gettingtemp:
            if not self.ui.acquiring:
                self.ui.andor.gettemperature()
                self.ui.cameratempActualTemp.setText(str(self.ui.andor.temperature))
            time.sleep(4)
