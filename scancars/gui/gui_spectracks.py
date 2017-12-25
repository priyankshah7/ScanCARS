from PyQt5.QtWidgets import QMainWindow

from gui.forms import WindowSPECTRACKS


class SPECTRACKS(QMainWindow, WindowSPECTRACKS.Ui_Dialog):
    def __init__(self, parent=None):
        super(SPECTRACKS, self).__init__(parent)
        self.setupUi(self)
