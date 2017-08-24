# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DV.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!
import re

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(930, 698)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.routerdate = QtWidgets.QTextEdit(self.centralwidget)
        self.routerdate.setGeometry(QtCore.QRect(410, 30, 471, 311))
        self.routerdate.setObjectName("routerdate")
        self.programdate = QtWidgets.QTextEdit(self.centralwidget)
        self.programdate.setGeometry(QtCore.QRect(410, 370, 471, 301))
        self.programdate.setObjectName("programdate")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 111, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 101, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.nodeinf = QtWidgets.QLineEdit(self.centralwidget)
        self.nodeinf.setGeometry(QtCore.QRect(130, 36, 201, 31))
        self.nodeinf.setObjectName("nodeinf")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 77, 111, 20))
        self.label_3.setObjectName("label_3")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(10, 119, 111, 20))
        self.label_6.setObjectName("label_6")
        self.outnodeinf = QtWidgets.QLineEdit(self.centralwidget)
        self.outnodeinf.setGeometry(QtCore.QRect(130, 119, 201, 31))
        self.outnodeinf.setObjectName("outnodeinf")
        self.innodeinf = QtWidgets.QLineEdit(self.centralwidget)
        self.innodeinf.setGeometry(QtCore.QRect(130, 76, 201, 31))
        self.innodeinf.setObjectName("innodeinf")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(410, 10, 130, 17))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(410, 350, 130, 17))
        self.label_5.setObjectName("label_5")
        self.addrouterButton = QtWidgets.QPushButton(self.centralwidget)
        self.addrouterButton.setGeometry(QtCore.QRect(140, 200, 99, 27))
        self.addrouterButton.setObjectName("addrouterButton")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(140, 340, 99, 27))
        self.startButton.setObjectName("startButton")
        # self.updateButton = QtWidgets.QPushButton(self.centralwidget)
        # self.updateButton.setGeometry(QtCore.QRect(140,245,99,27))
        # self.updateButton.setObjectName("updateButton")
        self.loaddataButton = QtWidgets.QPushButton(self.centralwidget)
        self.loaddataButton.setGeometry(QtCore.QRect(140, 270, 99, 27))
        self.loaddataButton.setObjectName("loaddataButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "输入拓扑信息:"))
        self.label_2.setText(_translate("MainWindow", "节点名称及cpu数量:"))
        self.label_3.setText(_translate("MainWindow", "流入节点及信息："))
        self.label_4.setText(_translate("MainWindow", "节点添加日志："))
        self.label_5.setText(_translate("MainWindow", "程序仿真日志:"))
        self.label_6.setText(_translate("MainWindow", "流出节点及信息："))
        self.addrouterButton.setText(_translate("MainWindow", "添加"))
        self.startButton.setText(_translate("MainWindow", "仿真开始"))
        # self.updateButton.setText(_translate("MainWindow", "更新"))
        self.loaddataButton.setText(_translate("MainWindow", "从文件读入"))
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(w)
    w.show()
    nodeinf = 'a:5:867387w'
    pattert = re.compile(r'(\w+):(\d+):(\d+)')
    matchs = pattert.search(nodeinf)
    print(matchs.group(1),matchs.group(2),matchs.group(3))

    sys.exit(app.exec_())