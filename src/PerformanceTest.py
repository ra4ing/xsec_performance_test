import csv
import os
import re
import subprocess


class PerformanceTester:
    def __init__(self, output_csv="performance_data.csv"):
        self.command = "/usr/bin/time -v perf stat -e cycles,instructions,cache-misses,cache-references qemu-riscv64 "
        self.relative_work_dir = "../build/"
        self.output_csv = "../data/" + output_csv
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.work_dir = os.path.join(self.script_dir)

        self.headers = ["File Name", "File Type", "Maximum resident set size (kbytes)", "Cycles", "Instructions", "Cache Misses", "Cache References"]
        self.__reset_and_prepare_csv()

        self.success = []
        self.failed = []

    def test(self, file_name, file_type="original"):
        
        process = subprocess.Popen(self.command + self.relative_work_dir + file_type + "/" + file_name, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=self.work_dir, shell=True)
        stdout, stderr = process.communicate()
        result = self.__parse_output(stdout, stderr)

        if process.returncode != 0:
            print("* [Failed] " + file_name)
            self.failed.append(file_name)
        else:
            print("[Success] " + file_name)
            self.success.append(file_name)
            self.__write_to_csv(result, file_name, file_type)
    

    def test_all_benchmarks(self, file_type="original"):
        print("Start test...")
        base_dir = "build/" + file_type
        for file_name in os.listdir(base_dir):
            self.test(file_name, file_type)
        self.print_result()


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
            "Maximum resident set size (kbytes)": r"Maximum resident set size \(kbytes\): (\d+)",
            "Cycles": r"(\d+(?:,\d+)*) +cycles",
            "Instructions": r"(\d+(?:,\d+)*) +instructions",
            "Cache Misses": r"(\d+(?:,\d+)*) +cache-misses",
            "Cache References": r"(\d+(?:,\d+)*) +cache-references"
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
        # 注意：这里假设metrics字典的键与headers中的一致
        row = [file_name, file_type] + [metrics.get(h, "N/A") for h in self.headers[2:]]
        with open(os.path.join(self.work_dir, self.output_csv), "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)


    def __reset_and_prepare_csv(self):
        # 删除旧的CSV文件，如果它存在的话
        csv_path = os.path.join(self.work_dir, self.output_csv)
        if os.path.exists(csv_path):
            os.remove(csv_path)
        
        # 创建一个新的CSV文件并写入表头
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers)