from PyQt5.QtWidgets import QMainWindow

from scancars.gui.forms import camera, specsum, spectracks


class CAMERA(QMainWindow, camera.Ui_Dialog):
    def __init__(self, parent=None):
        super(CAMERA, self).__init__(parent)
        self.setupUi(self)


class SPECTRACKS(QMainWindow, spectracks.Ui_Dialog):
    def __init__(self, parent=None):
        super(SPECTRACKS, self).__init__(parent)
        self.setupUi(self)


class SPECSUM(QMainWindow, specsum.Ui_Dialog):
    def __init__(self, parent=None):
        super(SPECSUM, self).__init__(parent)
        self.setupUi(self)
