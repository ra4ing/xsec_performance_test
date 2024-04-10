#! python3
from performance_test import *
from compiler import *
from analysis import *

def compile():
    compiler = Compiler()
    compiler.compile_all_benchmarks()
    compiler.compile_all_benchmarks("protected")
    

def test():
    tester = PerformanceTester()
    tester.test_all_benchmarks()
    tester.test_all_benchmarks("protected")


def analysis():
    analyser = PerformanceComparison("data/performance_data.csv")
    analyser.plot_comparison("Cycles")
    analyser.plot_comparison("Instructions")
    analyser.plot_comparison("Cache Misses")
    analyser.plot_comparison("Cache References")
    analyser.plot_comparison("Elapsed Time")
    analyser.plot_comparison("User Time")
    analyser.plot_comparison("System Time")
    analyser.plot_comparison("CPU Percentage")
    analyser.plot_comparison("Maximum resident set size (kbytes)")

if __name__ == '__main__':
    # compiel()
    test()
    analysis()