# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WindowCAMERA.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 800)
        Dialog.setStyleSheet("background: #191919")
        self.CameraOptions_VIEW = ImageView(Dialog)
        self.CameraOptions_VIEW.setGeometry(QtCore.QRect(0, 0, 801, 801))
        self.CameraOptions_VIEW.setObjectName("CameraOptions_VIEW")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))

from pyqtgraph import ImageView
