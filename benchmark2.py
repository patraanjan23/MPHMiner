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
    benchmark_terminated = QtCore.pyqtSignal()
    start_benchmark = QtCore.pyqtSignal()

    def __init__(self, algorithms: list, duration=60, benchmark_file="benchmark.txt",
                 algorithms_file="algorithms.txt"):
        super(BenchmarkGui, self).__init__()
        self.setupUi(self)
        self.setMinimumSize(320, 480)

        self.algorithms_file = Path(algorithms_file)
        self.benchmark_file = Path(benchmark_file)
        self.algorithms = {}
        self.current_algo = ""
        for algo in algorithms:
            self.algorithms[algo] = {
                "enabled": True,
                "samples": [],
                "hashrate": 0,
                "unit": None,
                "benchmarked": False
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

        # set duration
        self.btnDuration.clicked.connect(self.set_duration)

        # progress bar
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(self.duration)

        # new layout using checkbox
        self.enabled_algos = 0
        self.wait_duration = 1000
        self.wait_timer = QtCore.QTimer()
        self.wait_timer.setSingleShot(True)
        self.big_timer = QtCore.QTimer()
        self.big_timer.setSingleShot(True)

        self.btnBenchAgain.hide()

        self.big_timer.timeout.connect(self.start_bench)
        self.btnBenchmark.clicked.connect(self.benchmark_multi)
        self.btnBenchAgain.clicked.connect(self.reset_benchmark)
        self.start_benchmark.connect(self.benchmark_multi)

        for algo in self.algorithms:
            cb = QtWidgets.QCheckBox(algo)
            cb.stateChanged.connect(self.add_remove_algorithm)
            if self.algorithms[algo]["enabled"]:
                cb.setChecked(True)
            self.checkboxLayout.addWidget(cb)

        # for algo in self.algorithms:
        #     button = QtWidgets.QPushButton(algo)
        #     button.clicked.connect(self.benchmark_solo)
        #     self.btnGrid.addWidget(button)
        #     self.lblGrid.addWidget(QtWidgets.QLabel(button.text()))

    def add_remove_algorithm(self):
        debug = True
        cb = self.sender()
        if cb.isChecked():
            self.enabled_algos += 1
            self.algorithms[cb.text()]["enabled"] = True
        else:
            self.enabled_algos -= 1
            self.algorithms[cb.text()]["enabled"] = False
        if debug:
            print(self.algorithms)

    def set_duration(self):
        text = self.editDuration.text()
        try:
            # set duration and max for progress bar
            self.duration = float(text) * 1000
            self.progressBar.setMaximum(self.duration)
        except TypeError as e:
            print("wrong type")
        pass

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
            self.progressBar.setValue(self.duration - self.timer.remainingTime())

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

            # reset progress bar
            self.progressBar.setValue(0)
        pass

    def reset_benchmark(self):
        for algo in self.algorithms:
            if self.algorithms[algo]["enabled"]:
                self.algorithms[algo]["benchmarked"] = False

        self.benchmark_multi()

    def benchmark_multi(self):
        debug = True

        if self.big_timer.isActive():
            pass
        else:
            print("running in bg")
            for algo in self.algorithms:
                if self.algorithms[algo]["enabled"] and not self.algorithms[algo]["benchmarked"]:
                    big_duration = self.duration + 5000  # self.enabled_algos * (self.duration * 1000 + self.wait_duration)
                    self.big_timer.start(big_duration)
                    btn = QtWidgets.QPushButton(algo)
                    btn.clicked.connect(self.benchmark_solo)
                    self.algorithms[algo]["benchmarked"] = True
                    btn.click()
                    self.btnBenchmark.hide()
                    self.btnBenchAgain.show()
                    break

    def start_bench(self):
        print("reached here")
        self.big_timer.stop()
        self.start_benchmark.emit()

    def terminate_benchmark(self):
        # set progress to 100 when terminate
        self.progressBar.setValue(self.progressBar.maximum())

        # actually terminate
        print("terminated")
        if OS_NAME == "posix":
            self.process.terminate()
        else:
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
