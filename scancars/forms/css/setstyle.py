# Imports the css file and allows a PyQt app to call it
from PyQt5 import QtCore


def setstyle(ui):
    stylefile = QtCore.QFile('./forms/css/styletemp.css')
    stylefile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    ui.setStyleSheet(str(stylefile.readAll(), 'utf-8'))
    stylefile.close()
