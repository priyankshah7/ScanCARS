from PyQt5.QtWidgets import QMainWindow
from guiForms import WindowCAMERA


class CAMERA(QMainWindow, WindowCAMERA.Ui_Dialog):
    def __init__(self, parent=None):
        super(CAMERA, self).__init__(parent)
        self.setupUi(self)

