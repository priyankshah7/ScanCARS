# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WindowSPECSUM.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1600, 900)
        Dialog.setStyleSheet("background: #191919")
        self.SpecWin_sum = PlotWidget(Dialog)
        self.SpecWin_sum.setGeometry(QtCore.QRect(0, 0, 1591, 901))
        self.SpecWin_sum.setObjectName("SpecWin_sum")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))

from pyqtgraph import PlotWidget
