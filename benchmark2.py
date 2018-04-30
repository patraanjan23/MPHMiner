import re
import sys
from os import name as _os_name
from pathlib import Path

from PyQt5 import QtCore, QtWidgets

from benchmark_v2_form import Ui_Form


class BenchmarkGui(QtWidgets.QWidget, Ui_Form):
    benchmark_terminated = QtCore.pyqtSignal()
    start_benchmark = QtCore.pyqtSignal()

    def __init__(self, algorithms: list, duration=60, benchmark_file="benchmark.txt",
                 algorithms_file="algorithms.txt"):
        super(BenchmarkGui, self).__init__()
        self.setupUi(self)
        self.setMinimumSize(320, 480)

        # Important class variables
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
        self.enabled_algos = 0
        self.duration = duration * 1000
        self.wait_duration = 1000 * 2
        self.backup_dir = "backup"
        self.binary = "./bin/ccminer.exe"
        self.insert_env = False
        if _os_name == "posix":
            self.binary = "./bin/ccminer_linux"
            self.insert_env = True
        self.params = "--benchmark --no-color"
        self.regex = re.compile(r'Total:\s\d*\.\d*\s[kMGT]?H/s')

        # Process and Timer initializations
        self.process = QtCore.QProcess()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        # big_timer needed for the multi-algo benchmark
        self.big_timer = QtCore.QTimer()
        self.big_timer.setSingleShot(True)

        # Connecting signals
        self.timer.timeout.connect(self.terminate_benchmark)  # When timer ends kill process
        self.process.readyReadStandardOutput.connect(self.benchmark_solo)  # When process ready to be read parse
        self.btnDuration.clicked.connect(self.set_duration)  # Set duration button
        self.big_timer.timeout.connect(self.start_bench)  # The big_timer timeout emits start_benchmark signal
        self.btnBenchmark.clicked.connect(self.benchmark_multi)  # The big button to call the multi-algo benchmark
        self.btnBenchAgain.clicked.connect(self.reset_benchmark)  # The alternate big button to reset n re-bench
        self.start_benchmark.connect(self.benchmark_multi)  # On receiving the start_benchmark signal start next bench

        # Progress bar
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(self.duration)

        # New layout using checkbox
        for algo in self.algorithms:
            cb = QtWidgets.QCheckBox(algo)
            cb.stateChanged.connect(self.add_remove_algorithm)
            if self.algorithms[algo]["enabled"]:
                cb.setChecked(True)
            self.checkboxLayout.addWidget(cb)

        # Hide the alternative big button before the big button is pressed
        self.btnBenchAgain.hide()

        # Old GUI
        # for algo in self.algorithms:
        #     button = QtWidgets.QPushButton(algo)
        #     button.clicked.connect(self.benchmark_solo)
        #     self.btnGrid.addWidget(button)
        #     self.lblGrid.addWidget(QtWidgets.QLabel(button.text()))

    # Toggles the "enabled" property in the algorithm dictionary. If an algorithm is "enabled", it will be benched.
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

    # Set the duration from user input
    def set_duration(self):
        text = self.editDuration.text()
        try:
            # set duration and max for progress bar
            self.duration = float(text) * 1000
            self.progressBar.setMaximum(self.duration)
        except TypeError as e:
            print("wrong type")
        pass

    # Dummy method for testing purpose
    def check_btns(self):
        print(self.sender().text())

    def benchmark_solo(self, debug=True):

        # If the timer is already running that means a benchmark process is running, so parse the stdout.
        if self.timer.isActive():

            # Regex stuff
            #
            # The parser stores the hashrate data back to the dictionary so the data can be accessed outside the
            # benchmark process.
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

            # Updates progressbar
            self.progressBar.setValue(self.duration - self.timer.remainingTime())

        # If the timer is not running, that means a new benchmark process can be started with the timer.
        else:
            # Get the algo from the btn pressed
            algo = self.sender().text()
            print("starting benchmark {}".format(algo))

            # Set current algo
            self.current_algo = algo

            # Set environment variables for ccminer linux
            if self.insert_env:
                env = QtCore.QProcessEnvironment.systemEnvironment()
                env.insert("LD_LIBRARY_PATH", "$LD_LIBRARY_PATH:/usr/local/cuda/lib64")
                self.process.setProcessEnvironment(env)

            # Start the process with timer
            print(self.binary)
            self.process.start(self.binary, self.make_param(self.current_algo))
            self.timer.start(self.duration)

            # Reset progress bar
            self.progressBar.setValue(self.progressBar.minimum())
        pass

    # Resets the "benchmarked" property to False for all algorithms in the dictionary so that the benchmark can be
    # run again without closing the app.
    def reset_benchmark(self):
        for algo in self.algorithms:
            if self.algorithms[algo]["enabled"]:
                self.algorithms[algo]["benchmarked"] = False

        self.benchmark_multi()

    def benchmark_multi(self, debug=True):

        if self.big_timer.isActive():
            # Does nothing for now. Keeping for possible future use cases.
            pass

        else:
            if debug:
                print("running in bg")

            # Starting big_timer with duration + 5 sec to let the benchmark process (QProcess) terminate properly
            # before being called again.
            #
            # Currently using a QPushButton and clicking programmatically to call the benchmark_solo function.
            # This is not the ideal solution, but at this moment only this seems to work.
            # will work on a separate function to cleanly execute multi-algo benchmark later.

            for algo in self.algorithms:

                if self.algorithms[algo]["enabled"] and not self.algorithms[algo]["benchmarked"]:
                    # Dirty way to get the job done. Needs fix later.
                    big_duration = self.duration + self.wait_duration
                    self.big_timer.start(big_duration)
                    pseudo_button = QtWidgets.QPushButton(algo)
                    pseudo_button.clicked.connect(self.benchmark_solo)
                    self.algorithms[algo]["benchmarked"] = True
                    pseudo_button.click()

                    # Another workaround for re-benchmarking. The btnBenchAgain just resets the "benchmarked"
                    # property and calls this function again.
                    self.btnBenchmark.hide()
                    self.btnBenchAgain.show()

                    # Necessary to loop through all algorithms in the dictionary. Need to break the loop so the
                    # benchmark process is not called concurrently.
                    break

    # This method just emits the start_benchmark signal once the big_timer timeouts which in turn calls the
    # benchmark_multi method again. The only use of this is to wait the extra amount of time in big_timer, so
    # the QProcess can terminate properly.
    def start_bench(self, debug=True):
        if debug:
            print("reached here")
        self.big_timer.stop()
        self.start_benchmark.emit()

    # This method is for terminating the benchmark process started by benchmark_solo method and stop timer.
    def terminate_benchmark(self, debug=True):
        if debug:
            print("terminated")

        # Set progress to 100 when terminate
        self.progressBar.setValue(self.progressBar.maximum())

        # Actually terminate the process and timer
        if _os_name == "posix":
            self.process.terminate()
        else:
            self.process.kill()
        self.timer.stop()

    # Generates the format string for process to execute
    def make_param(self, algo: str):
        result = ("-a " + algo + " " + self.params).split()
        print(result)
        return result

    def closeEvent(self, q_close_event):
        if self.timer.isActive():
            self.timer.stop()
            self.big_timer.stop()
            self.process.kill()

        print("closing the app")
        q_close_event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    btn = BenchmarkGui(["skein", "lyra2v2", "cryptolight"])
    btn.show()
    sys.exit(app.exec_())
