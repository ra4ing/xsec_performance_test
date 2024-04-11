#! python3
from performance_test import *
from compiler import *
from analysis import *

def compile():
    compiler = Compiler()
    compiler.compile_all_benchmarks("no_extension")
    compiler.compile_all_benchmarks("original")
    compiler.compile_all_benchmarks("protected")
    

def test():
    tester = PerformanceTester()
    tester.reset_and_prepare_csv()
    tester.test_all_benchmarks("no_extension")
    tester.test_all_benchmarks("original")
    tester.test_all_benchmarks("protected")


def analysis():
    analyser = PerformanceComparison("data/performance_data.csv")
    analyser.calculate_and_save_averages("no_extension")
    analyser.calculate_and_save_averages("original")
    analyser.calculate_and_save_averages("protected")
    analyser.plot_comparison("Cycles")
    analyser.plot_comparison("Instructions")
    analyser.plot_comparison("Cache Misses")
    analyser.plot_comparison("Cache References")
    analyser.plot_comparison("Elapsed Time")
    analyser.plot_comparison("Maximum resident set size (kbytes)")

if __name__ == '__main__':
    # compile()
    # test()
    analysis()
