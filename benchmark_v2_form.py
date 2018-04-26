# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/otakulabs/PycharmProjects/MPHMiner/benchmark_v2_form.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(640, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.editDuration = QtWidgets.QLineEdit(Form)
        self.editDuration.setObjectName("editDuration")
        self.horizontalLayout.addWidget(self.editDuration)
        self.btnDuration = QtWidgets.QPushButton(Form)
        self.btnDuration.setObjectName("btnDuration")
        self.horizontalLayout.addWidget(self.btnDuration)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.checkboxLayout = QtWidgets.QVBoxLayout()
        self.checkboxLayout.setObjectName("checkboxLayout")
        self.horizontalLayout_2.addLayout(self.checkboxLayout)
        self.labelLayout = QtWidgets.QVBoxLayout()
        self.labelLayout.setObjectName("labelLayout")
        self.horizontalLayout_2.addLayout(self.labelLayout)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.lblGrid = QtWidgets.QGridLayout()
        self.lblGrid.setObjectName("lblGrid")
        self.verticalLayout.addLayout(self.lblGrid)
        self.btnGrid = QtWidgets.QGridLayout()
        self.btnGrid.setObjectName("btnGrid")
        self.verticalLayout.addLayout(self.btnGrid)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.btnBenchmark = QtWidgets.QPushButton(Form)
        self.btnBenchmark.setObjectName("btnBenchmark")
        self.verticalLayout.addWidget(self.btnBenchmark)
        self.btnBenchAgain = QtWidgets.QPushButton(Form)
        self.btnBenchAgain.setObjectName("btnBenchAgain")
        self.verticalLayout.addWidget(self.btnBenchAgain)
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Duration"))
        self.editDuration.setToolTip(_translate("Form", "Duration"))
        self.editDuration.setWhatsThis(_translate("Form", "Duration"))
        self.btnDuration.setText(_translate("Form", "Set"))
        self.btnBenchmark.setText(_translate("Form", "Benchmark"))
        self.btnBenchAgain.setText(_translate("Form", "Benchmark"))
