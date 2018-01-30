from PyQt5.QtCore import QProcess


class BenchmarkProcess(QProcess):
    def __init__(self):
        super().__init__()
