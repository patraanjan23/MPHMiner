import re
import sys
from os import name as OS_NAME
from pathlib import Path

from PyQt5 import QtCore, QtWidgets

from benchmark_v2_form import Ui_Form


class BenchmarkV2:
    def __init__(self, algorithms: list, duration: int, benchmark_file: str, algorithms_file: str):
        self.algorithms_file = Path(algorithms_file)
        self.benchmark_file = Path(benchmark_file)
        # self.algorithms = algorithms
        self.algorithms = {}
        self.current_algo = ""
        for algo in algorithms:
            self.algorithms[algo] = {
                "samples": [],
                "hashrate": 0,
                "unit": None
            }
        self.duration = duration * 1000
        self.backup_dir = "backup"
        self.binary = "./bin/ccminer_linux"
        if OS_NAME == "nt":
            self.binary = "bin/ccminer.exe"
        self.params = "--benchmark --no-color"
        self.regex = re.compile(r"Total:\s\d*\.\d*\s[kMGT]?H/s")

        self.process = QtCore.QProcess()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)

        self.timer.timeout.connect(self.terminate)
        self.process.readyReadStandardOutput.connect(self.benchmark_solo)

    def benchmark_solo(self, algo: str = None, debug=True):
        if debug:
            # print(self.timer.isActive())
            pass
        if self.timer.isActive():
            text = self.process.readAllStandardOutput().data().decode("utf-8").rstrip()
            match = self.regex.search(text)
            if match is not None:
                bm_string = match.group(0)
                hr = float(bm_string.split()[1])
                self.algorithms[self.current_algo]["samples"].append(hr)

                if len(self.algorithms[self.current_algo]["samples"]) > 0:
                    self.algorithms[self.current_algo]["hashrate"] = sum(
                        self.algorithms[self.current_algo]["samples"]) / len(
                        self.algorithms[self.current_algo]["samples"])

                if self.algorithms[self.current_algo]["unit"] is None:
                    unit = bm_string.split()[2].strip()
                    self.algorithms[self.current_algo]["unit"] = unit

                if debug:
                    # print("BM_STRING: {}\nHR: {}\nUNIT: {}".format(bm_string, hr, unit))
                    print(self.algorithms[self.current_algo])
                    pass

        else:
            print("starting benchmark")
            self.current_algo = algo
            env = QtCore.QProcessEnvironment.systemEnvironment()
            if OS_NAME == "posix":
                env.insert("LD_LIBRARY_PATH", "$LD_LIBRARY_PATH:/usr/local/cuda/lib64")
            self.process.setProcessEnvironment(env)
            self.process.start(self.binary, self.make_param(algo))
            self.timer.start(self.duration)
        pass

    def terminate(self):
        print("terminated")
        self.timer.stop()
        self.process.terminate()

    def make_param(self, algo: str):
        result = ("-a " + algo + " " + self.params).split()
        print(result)
        return result


class BenchmarkGui(QtWidgets.QWidget, Ui_Form):
    def __init__(self, algorithms: list, duration=60, benchmark_file="benchmark.txt",
                 algorithms_file="algorithms.txt"):
        super(BenchmarkGui, self).__init__()
        self.setupUi(self)

        self.algorithms_file = Path(algorithms_file)
        self.benchmark_file = Path(benchmark_file)
        self.algorithms = {}
        self.current_algo = ""
        for algo in algorithms:
            self.algorithms[algo] = {
                "samples": [],
                "hashrate": 0,
                "unit": None
            }
        self.duration = duration * 1000
        self.backup_dir = "backup"
        self.binary = "./bin/ccminer.exe"
        self.insert_env = False
        if OS_NAME == "posix":
            self.binary = "./bin/ccminer_linux"
            self.insert_env = True
        self.params = "--benchmark --no-color"
        self.regex = re.compile(r'Total:\s\d*\.\d*\s[kMGT]?H/s')

        self.process = QtCore.QProcess()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)

        self.timer.timeout.connect(self.terminate_benchmark)
        self.process.readyReadStandardOutput.connect(self.benchmark_solo)

        for algo in self.algorithms:
            button = QtWidgets.QPushButton(algo)
            button.clicked.connect(self.benchmark_solo)
            self.btnGrid.addWidget(button)
            self.lblGrid.addWidget(QtWidgets.QLabel(button.text()))

    def check_btns(self):
        print(self.sender().text())

    def benchmark_solo(self):
        debug = True
        if self.timer.isActive():
            text = self.process.readAllStandardOutput().data().decode("utf-8").rstrip()
            match = self.regex.search(text)
            if match:
                bm_string = match.group(0)
                hr = float(bm_string.split()[1])
                unit = bm_string.split()[2].strip()
                self.algorithms[self.current_algo]["samples"].append(hr)

                if len(self.algorithms[self.current_algo]["samples"]) > 0:
                    self.algorithms[self.current_algo]["hashrate"] = sum(
                        self.algorithms[self.current_algo]["samples"]) / len(
                        self.algorithms[self.current_algo]["samples"])

                if self.algorithms[self.current_algo]["unit"] is None:
                    self.algorithms[self.current_algo]["unit"] = unit

                if debug:
                    print("BM_STRING: {}\nHR: {}\nUNIT: {}".format(bm_string, hr, unit))
                    print(self.algorithms[self.current_algo])

                pass

        else:
            # get the algo from the btn pressed
            algo = self.sender().text()
            print("starting benchmark {}".format(algo))

            # set current algo
            self.current_algo = algo

            # set environment variables for ccminer linux
            if self.insert_env:
                env = QtCore.QProcessEnvironment.systemEnvironment()
                env.insert("LD_LIBRARY_PATH", "$LD_LIBRARY_PATH:/usr/local/cuda/lib64")
                self.process.setProcessEnvironment(env)

            # start the process with timer
            self.process.start(self.binary, self.make_param(self.current_algo))
            self.timer.start(self.duration)
        pass

    def terminate_benchmark(self):
        print("terminated")
        self.process.kill()
        self.timer.stop()

    def make_param(self, algo: str):
        result = ("-a " + algo + " " + self.params).split()
        print(result)
        return result


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    btn = BenchmarkGui(["skein", "lyra2v2", "cryptolight"])
    btn.show()
    sys.exit(app.exec_())
