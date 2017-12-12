from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject

import time
# TODO Need to implement this such that it is possible to switch the cooler on and OFF


class CoolerOnSignals(QObject):
    finished = pyqtSignal()


class CoolerOn(QRunnable):
    def __init__(self, gui):
        super(CoolerOn, self).__init__()
        self.gui = gui
        self.signals = CoolerOnSignals()

    @pyqtSlot()
    def run(self):
        tempreq = int(self.gui.CameraTemp_temp_req.text())
        messageSetTemperature = self.gui.cam.SetTemperature(tempreq)
        if messageSetTemperature is not None:
            self.gui.post.eventlog(self.gui, messageSetTemperature)
            return

        messageCoolerON = self.gui.cam.CoolerON()
        if messageCoolerON is not None:
            self.gui.post.eventlog(self.gui, messageCoolerON)
            return

        self.signals.finished.emit()


class CoolerOffSignals(QObject):
    finished = pyqtSignal()


class CoolerOff(QRunnable):
    def __init__(self, gui):
        super(CoolerOff, self).__init__()
        self.gui = gui
        self.signals = CoolerOffSignals()

    @pyqtSlot()
    def run(self):
        messageCoolerOFF = self.gui.cam.CoolerOFF()
        if messageCoolerOFF is not None:
            self.gui.post.eventlog(self.gui, messageCoolerOFF)
            return

        self.signals.finished.emit()


class AndorTemperatureSignals(QObject):
    finished = pyqtSignal()


class AndorTemperature(QRunnable):
    def __init__(self, gui):
        super(AndorTemperature, self).__init__()
        self.gui = gui
        self.signals = AndorTemperatureSignals()
        self.condition = True

    @pyqtSlot()
    def stop(self):
        self.condition = False

    @pyqtSlot()
    def run(self):
        self.condition = True

        while self.condition:
            messageGetStatus = self.gui.cam.GetStatus()
            if messageGetStatus == 'DRV_ACQUIRING':
                pass

            else:
                messageGetTemperature = self.gui.cam.GetTemperature()
                if messageGetTemperature is not None:
                    self.gui.post.eventlog(self.gui, messageGetTemperature)
                    return
                else:
                    self.gui.CameraTemp_temp_actual.setText(str(self.gui.cam.temperature))
                    time.sleep(2)
