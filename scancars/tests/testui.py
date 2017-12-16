# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'testui.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.specwin = PlotWidget(self.centralwidget)
        self.specwin.setGeometry(QtCore.QRect(0, 0, 1401, 591))
        self.specwin.setObjectName("specwin")
        self.startacq = QtWidgets.QPushButton(self.centralwidget)
        self.startacq.setGeometry(QtCore.QRect(640, 610, 121, 31))
        self.startacq.setObjectName("startacq")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1400, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.startacq.setText(_translate("MainWindow", "Start"))

from pyqtgraph import PlotWidget
