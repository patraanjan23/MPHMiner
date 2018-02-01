import json
import os
import re
import subprocess
from time import sleep
from pprint import pformat

from api_parser import MPHProfitApi


def avg(x):
    return sum(x) / len(x)


class Benchmark:
    def __init__(self, algorithms=None, binary="./bin/ccminer_linux", params="--benchmark --no-color", duration=120,
                 benchmark_file="benchmark.txt", algorithms_file="algorithms.txt",
                 benchmark_dir="benchmarks"):
        self.algorithms = algorithms
        self.binary = binary
        self.params = params
        self.duration = duration
        self.benchmark_file = benchmark_file
        self.algorithms_file = algorithms_file
        self.benchmark_dir = benchmark_dir
        if not os.path.exists(self.benchmark_dir):
            os.makedirs(self.benchmark_dir)

    @staticmethod
    def average_benchmark(benchmark_list):
        sum_samples = 0
        no_samples = len(benchmark_list)
        multiplier = 1
        if no_samples > 0:
            unit = benchmark_list[0].split()[2]
            if unit == "H/s":
                multiplier *= 10 ** 0
            elif unit == "kH/s":
                multiplier *= 10 ** 3
            elif unit == "MH/s":
                multiplier *= 10 ** 6
            elif unit == "GH/s":
                multiplier *= 10 ** 9
            elif unit == "TH/s":
                multiplier *= 10 ** 12
            else:
                print("Unknown unit for hashrate, can't calculate multiplier")

            for benchmark in benchmark_list:
                sum_samples += float(benchmark.split()[1])

            return sum_samples / no_samples * multiplier

    def start_benchmark_algo(self, algo=None):
        os.environ["LD_LIBRARY_PATH"] = "$LD_LIBRARY_PATH:/usr/local/cuda/lib64"
        if algo is not None:
            print("Benchmarking {}".format(algo))
            with open(self.benchmark_dir + "/" + algo + ".txt", "w") as algorithm:
                p = subprocess.Popen((self.binary + " -a " + algo + " " + self.params).split(), stdout=algorithm,
                                     stderr=subprocess.STDOUT)
                sleep(self.duration)
                p.terminate()
                print("{} benchmark complete".format(algo))

        else:
            with open(self.algorithms_file) as algorithms:
                for algo in algorithms:
                    self.start_benchmark_algo(algo.rstrip())

    def write_benchmarks(self):
        algorithms = {}
        regex = re.compile(r"Total:\s\d*\.\d*\s[kMGT]?H/s")

        with open(self.algorithms_file) as infile:
            for algo in infile:
                algo = algo.rstrip()
                with open("benchmarks/" + algo + ".txt") as infile_2:
                    samples = regex.findall(infile_2.read())
                    # algorithm = {"algo": algo, "hashrate": self.average_benchmark(samples)}
                    # algorithms.append(algorithm)
                    algorithms[algo] = {"hr": self.average_benchmark(samples)}

        api = MPHProfitApi()
        current_profits = api.get_json()
        viable_coins = []
        for coin in current_profits:
            if coin["algo"] in algorithms.keys():
                coin["hr"] = algorithms[coin["algo"]]["hr"]
                coin["my_profit"] = coin["profit"] * algorithms[coin["algo"]]["hr"]
            if "my_profit" in coin.keys():
                viable_coins.append({
                    "name": coin["coin_name"],
                    "algo": coin["algo"],
                    "port": coin["port"],
                    "profit": coin["profit"],
                    "my_profit": coin["my_profit"],
                    "hashrate": coin["hr"]
                })

        with open(self.benchmark_file, "w") as outfile:
            json.dump(viable_coins, outfile)
            # outfile.write(pformat(viable_coins))

    def get_benchmarks(self, forced=False, algorithms=[]):
        try:
            if forced:
                raise FileNotFoundError
            if len(algorithms) > 0:
                for algo in algorithms:
                    if not os.path.exists(self.benchmark_dir + "/" + algo + ".txt"):
                        self.start_benchmark_algo(algo)

            else:
                with open(self.algorithms_file) as infile:
                    for algo in infile:
                        algo = algo.rstrip()
                        if not os.path.exists(self.benchmark_dir + "/" + algo + ".txt"):
                            self.start_benchmark_algo(algo)

            self.write_benchmarks()
            with open(self.benchmark_file) as infile:
                data = json.load(infile)

                if len(algorithms) > 0:
                    result = []
                    for coin in data:
                        if coin["algo"] in algorithms:
                            result.append(coin)
                    return result

                return data

                # return json.load(infile)

        except FileNotFoundError:
            self.start_benchmark_algo()
            self.write_benchmarks()
            self.get_benchmarks()


if __name__ == "__main__":
    b = Benchmark()
    # b.write_benchmarks()
    # print(b.get_benchmarks(algorithms=["cryptonight", "skein"]))
