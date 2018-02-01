# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/otakulabs/PycharmProjects/MPHMiner/benchmark_form.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(318, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.vboxLayout = QtWidgets.QVBoxLayout()
        self.vboxLayout.setObjectName("vboxLayout")
        self.verticalLayout.addLayout(self.vboxLayout)
        self.tableView = QtWidgets.QTableView(Form)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.btnBenchmark = QtWidgets.QPushButton(Form)
        self.btnBenchmark.setObjectName("btnBenchmark")
        self.verticalLayout.addWidget(self.btnBenchmark)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.btnBenchmark.setText(_translate("Form", "Benchmark"))

