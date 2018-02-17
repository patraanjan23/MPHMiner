# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/otakulabs/PycharmProjects/MPHMiner/benchmark_v2_form.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblGrid = QtWidgets.QGridLayout()
        self.lblGrid.setObjectName("lblGrid")
        self.verticalLayout.addLayout(self.lblGrid)
        self.btnGrid = QtWidgets.QGridLayout()
        self.btnGrid.setObjectName("btnGrid")
        self.verticalLayout.addLayout(self.btnGrid)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

