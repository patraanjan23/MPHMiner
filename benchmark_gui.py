import sys

from PyQt5 import QtWidgets, QtCore

from benchmark import Benchmark
from benchmark_form import Ui_Form


class HashRate:
    def __init__(self, hashrate=None):
        self.base = None
        self.value = None
        self.mult = 1
        self.unit = "H/s"

        if hashrate is not None:
            self.hashrate = hashrate.split()
            self.base = float(self.hashrate[0])
            self.unit = self.hashrate[1]
            if self.unit[0] == "k":
                self.mult *= 10 ** 3
            elif self.unit[0] == "M":
                self.mult *= 10 ** 6
            elif self.unit[0] == "G":
                self.mult *= 10 ** 9
            elif self.unit[0] == "T":
                self.mult *= 10 ** 12
            else:
                pass
            self.value = self.base * self.mult

    def __repr__(self):
        return "{} {}".format(self.value, self.unit)

    def set_value(self, value: float):
        self.value = value

    def get_value_k(self):
        if self.value is not None:
            return self.value / 10 ** 3

    def get_value_m(self):
        if self.value is not None:
            return self.value / 10 ** 6

    def get_value_g(self):
        if self.value is not None:
            return self.value / 10 ** 9

    def get_value_t(self):
        if self.value is not None:
            return self.value / 10 ** 12

    def get_value(self):
        if self.value is not None:
            return self.value / 10 ** 0

    def __add__(self, other):
        result = HashRate()
        result.set_value(self.get_value() + other.get_value())
        return result

    def __mul__(self, other):
        result = HashRate()
        result.set_value(self.get_value() * other)
        return result

    @staticmethod
    def average(iterable):
        sum_iter = HashRate("0 H/s")

        for i in iterable:
            sum_iter += HashRate(i)

        return sum_iter * (1.0 / len(iterable))


class BenchmarkTableModel(QtCore.QAbstractTableModel):
    def __init__(self, tuples=[], parent=None):
        super(BenchmarkTableModel, self).__init__(parent)
        self.__tuples = [(coin["name"], coin["algo"], coin["hashrate"], coin["my_profit"], coin["port"]) for coin in
                         tuples]
        # self.dataChanged.connect(self.view.refresh)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.__tuples)

    def columnCount(self, parent=None, *args, **kwargs):
        if len(self.__tuples) > 0:
            return len(self.__tuples[0])
        else:
            return 0

    def data(self, index, role=None):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return self.__tuples[row][col]

    def headerData(self, p_int, qt__orientation, role=None):
        headers = ["Coin", "Algo", "Hash Rate (H/s)", "Profitability", "Port"]
        if role == QtCore.Qt.DisplayRole:
            if qt__orientation == QtCore.Qt.Horizontal:
                return headers[p_int]


class FloatSortModel(QtCore.QSortFilterProxyModel):
    def lessThan(self, left, right):
        return left.data() < right.data()


class Benchmarker(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setMinimumSize(640, 480)

        self.benchmark = Benchmark(binary="bin\ccminer_win.exe")
        self.benchmarks = []
        self.algorithms = []

        with open(self.benchmark.algorithms_file) as infile:
            for algo in infile:
                algo = algo.rstrip()
                cb = QtWidgets.QCheckBox(algo)
                cb.stateChanged.connect(self.set_algorithms)
                self.vboxLayout.addWidget(cb)

        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableView.verticalHeader().hide()
        self.tableView.setSortingEnabled(True)
        self.tableView.hide()

        self.btnBenchmark.clicked.connect(self.update_benchmarks)

    def update_benchmarks(self):
        self.benchmarks = self.benchmark.get_benchmarks(algorithms=self.algorithms)
        model = BenchmarkTableModel(self.benchmarks)
        proxy = FloatSortModel()
        proxy.setSourceModel(model)
        self.tableView.setModel(proxy)
        self.tableView.show()
        self.hide_cb()
        # print(self.benchmarks)
        # self.benchmarks = self.benchmark.get_benchmarks(True)
        pass

    def hide_cb(self):
        for i in range(self.vboxLayout.count()):
            cb = self.vboxLayout.itemAt(i).widget()
            cb.hide()

    def set_algorithms(self):
        child_count = self.vboxLayout.count()
        for i in range(child_count):
            cb = self.vboxLayout.itemAt(i).widget()
            if cb.isChecked() and cb.text() not in self.algorithms:
                self.algorithms.append(cb.text())
            elif not cb.isChecked() and cb.text() in self.algorithms:
                self.algorithms.remove(cb.text())
        print(self.algorithms)
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = Benchmarker()
    form.show()
    sys.exit(app.exec_())
