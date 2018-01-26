from PyQt5.QtWidgets import QMainWindow

from scancars.gui.forms import camera, winspecsum, winspecdiff


class CAMERA(QMainWindow, camera.Ui_Dialog):
    def __init__(self, parent=None):
        super(CAMERA, self).__init__(parent)
        self.setupUi(self)


class SPECDIFF(QMainWindow, winspecdiff.Ui_MainWindow):
    def __init__(self, parent=None):
        super(SPECDIFF, self).__init__(parent)
        self.setupUi(self)


class SPECSUM(QMainWindow, winspecsum.Ui_MainWindow):
    def __init__(self, parent=None):
        super(SPECSUM, self).__init__(parent)
        self.setupUi(self)
