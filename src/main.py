#! python3
from PerformanceTest import *
from Compiler import *

    
if __name__ == '__main__':
    # compiler = Compiler()
    # compiler.compile_all_benchmarks("protected")

    tester = PerformanceTester()
    tester.test_all_benchmarks("protected")