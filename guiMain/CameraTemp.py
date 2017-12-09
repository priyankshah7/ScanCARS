from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject

# TODO Need to implement this such that it is possible to switch the cooler on and OFF

class Cooler(QRunnable):
    def __init__(self, gui):
        super(Cooler, self).__init__()
        self.gui = gui

    @pyqtSignal
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

        self.gui.post.eventlog(self.gui, 'Andor: Cooler on.')
