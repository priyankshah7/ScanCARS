from PyQt5.QtWidgets import QMainWindow

from scancars.gui.forms import winspecsum, winspecdiff, winccdlive


class SPECDIFF(QMainWindow, winspecdiff.Ui_MainWindow):
    def __init__(self, parent=None):
        super(SPECDIFF, self).__init__(parent)
        self.setupUi(self)


class SPECSUM(QMainWindow, winspecsum.Ui_MainWindow):
    def __init__(self, parent=None):
        super(SPECSUM, self).__init__(parent)
        self.setupUi(self)


class CCDLIVE(QMainWindow, winccdlive.Ui_MainWindow):
    def __init__(self, parent=None):
        super(CCDLIVE, self).__init__(parent)
        self.setupUi(self)
