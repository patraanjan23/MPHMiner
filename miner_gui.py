import sys
from PyQt5 import QtWidgets, QtCore, QtGui

from miner_form import Ui_Form


# ic_close = QtGui.QIcon("../icons/close.png")
# ic_minimize = QtGui.QIcon("../icons/minimize.png")
# ic_restore = QtGui.QIcon("../icons/restore.png")
# ic_maximize = QtGui.QIcon("../icons/maximize.png")


class Miner(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # Vars
        self.clicked_pt = None
        self.drag_pt = None

        # Methods
        self.btnClose.setIcon(QtGui.QIcon("../icons/close.png"))
        self.btnMinimize.setIcon(QtGui.QIcon("../icons/minimize.png"))
        self.btnRestore.setIcon(QtGui.QIcon("../icons/restore.png"))
        self.btnConfig.setIcon(QtGui.QIcon("../icons/config.png"))

        self.btnClose.clicked.connect(self.close)
        self.btnMinimize.clicked.connect(self.show_minimized)
        self.btnRestore.clicked.connect(self.show_restored)

    def show_restored(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def show_minimized(self):
        self.showMinimized()

    def mousePressEvent(self, q_mouse_event):
        self.clicked_pt = QtCore.QPoint(q_mouse_event.x(), q_mouse_event.y())

    def mouseMoveEvent(self, q_mouse_event):
        if True in map(lambda child: child.underMouse(), self.findChildren(QtWidgets.QPushButton)):
            pass
        else:
            self.drag_pt = QtCore.QPoint(q_mouse_event.x() + self.x() - self.clicked_pt.x(),
                                         q_mouse_event.y() + self.y() - self.clicked_pt.y())
            if self.drag_pt is not None:
                self.move(self.drag_pt)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = Miner()
    form.show()
    sys.exit(app.exec_())
