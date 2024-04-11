import csv
import os
import re
import subprocess
import pandas as pd

class PerformanceTester:
    def __init__(self, output_csv="performance_data.csv"):
        self.sec_extension_command = "/usr/bin/time -v perf stat -e cycles,instructions,cache-misses,cache-references -r 100 qemu-riscv64 "
        self.no_extension_command = "/usr/bin/time -v perf stat -e cycles,instructions,cache-misses,cache-references -r 100 $HOME/tools/evaluation/qemu/build/qemu-riscv64 "
        self.relative_work_dir = "../build/"
        self.output_csv = "../data/" + output_csv
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.work_dir = os.path.join(self.script_dir)

        self.headers = ["File Name", "File Type", "Cycles", "Instructions", "Cache Misses", "Cache References", "Elapsed Time", "User Time", "System Time", "CPU Percentage", "Maximum resident set size (kbytes)"]

        self.success = []
        self.failed = []

    def test(self, file_name, file_type, iterations=20):
        """
        Tests a given file multiple times, computes the average of the performance metrics, and writes the results to the CSV file.
        
        :param file_name: Name of the file to test.
        :param file_type: Type of the file ('original' or 'protected').
        :param iterations: Number of iterations to run the test and compute the average.
        """
        # Initialize dictionary to sum up the metrics
        metrics_sum = {
            "Cycles": 0, "Instructions": 0, "Cache Misses": 0, "Cache References": 0,
            "Elapsed Time": 0.0, "User Time": 0.0, "System Time": 0.0,
            "CPU Percentage": 0, "Maximum resident set size (kbytes)": 0
        }
        successful_runs = 0
        
        command = ""
        if file_type == "no_extension":
            command = self.no_extension_command
        else:
            command = self.sec_extension_command

        for _ in range(iterations):
            # Execute the test command
            process = subprocess.Popen(command + self.relative_work_dir + file_type + "/" + file_name, 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=self.work_dir, shell=True)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                # Parse the performance metrics from stderr
                result = self.__parse_output(stdout, stderr)
                successful_runs += 1
                
                # Sum up the metrics for averaging later
                for key, value in result.items():
                    if value != "N/A":
                        metrics_sum[key] += float(value.replace(',', ''))
            else:
                print("* [Failed] " + file_name)
                self.failed.append(file_name)
                return  # Stop testing this file after a failure
        
        # Only proceed if there were successful test runs
        if successful_runs > 0:
            # Calculate average of the metrics
            avg_metrics = {key: value / successful_runs for key, value in metrics_sum.items()}
            
            print("[Success] " + file_name)
            self.success.append(file_name)
            
            # Write the averaged metrics to CSV
            self.__write_to_csv(avg_metrics, file_name, file_type)
        

    def test_all_benchmarks(self, file_type):
        self.success = []
        self.failed = []
        self.warm_up("coulomb_double", file_type, 5)
        print("Start test...")
        base_dir = "build/" + file_type
        for file_name in os.listdir(base_dir):
            self.test(file_name, file_type)
        self.print_result()

    def warm_up(self, file_name, file_type, iterations=5):
        """
        Performs warm-up tests to minimize the impact of caching and other system states on test results.

        :param file_name: Name of the test file.
        :param file_type: Type of test file (original or protected).
        :param iterations: The number of iterations for the warm-up test.
        """
        warm_up_command = self.sec_extension_command + self.relative_work_dir + file_type + "/" + file_name
        print(f"Starting warm-up for {file_name} ({iterations} iterations)...")
        for _ in range(iterations):
            subprocess.run(warm_up_command, shell=True, cwd=self.work_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Warm-up completed.")

    def print_result(self):
        if self.success:
            print("success:")
            print("\n".join(["- " + item for item in self.success]))
        else:
            print("no success")
        print()

        if self.failed:
            print("failed:")
            print("\n".join(["- " + item for item in self.failed]))
        else:
            print("no failed")    
        print()  

    def __parse_output(self, stdout, stderr):
        metrics_patterns = {
            "Cycles": r"(\d+(?:,\d+)*)\s+cycles",
            "Instructions": r"(\d+(?:,\d+)*)\s+instructions",
            "Cache Misses": r"(\d+(?:,\d+)*)\s+cache-misses",
            "Cache References": r"(\d+(?:,\d+)*)\s+cache-references",
            "Elapsed Time": r"([\d.]+) seconds time elapsed",
            "User Time": r"([\d.]+) seconds user",
            "System Time": r"([\d.]+) seconds sys",
            "CPU Percentage": r"Percent of CPU this job got: ([\d]+)%",
            "Maximum resident set size (kbytes)": r"Maximum resident set size \(kbytes\): (\d+)"
        }

        results = {}
        for key, pattern in metrics_patterns.items():
            match = re.search(pattern, stderr)
            if match:
                results[key] = match.group(1).replace(',', '')
            else:
                results[key] = "N/A"
        return results

    
    def __write_to_csv(self, metrics, file_name, file_type):
        row = [file_name, file_type] + [metrics.get(h, "N/A") for h in self.headers[2:]]
        with open(os.path.join(self.work_dir, self.output_csv), "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)


    def reset_and_prepare_csv(self):
        # Delete old CSV file if it exists
        csv_path = os.path.join(self.work_dir, self.output_csv)
        if os.path.exists(csv_path):
            os.remove(csv_path)
        
        # Create a new CSV file and write the header
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers)
