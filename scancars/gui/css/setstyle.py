# Imports the css file and allows a PyQt app to call it
from PyQt5 import QtCore

# TODO Need to add css files for deactivated buttons etc and then add relevant methods here


def main(ui):
    stylefile = QtCore.QFile('./gui/css/main.css')
    stylefile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    ui.setStyleSheet(str(stylefile.readAll(), 'utf-8'))
    stylefile.close()


def deactivate_all(ui):
    pass
