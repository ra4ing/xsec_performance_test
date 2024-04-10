import os
import subprocess


class Compiler:
    def __init__(self):
        self.output_dir = "../build/"
        self.target_dir = "../benchmark/"
        self.command = f"clang --gcc-toolchain=$HOME/tools/riscv -target riscv64-unknown-elf -march=rv64gc_xs -mabi=lp64d "

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.work_dir = os.path.join(self.script_dir)
        self.success = []
        self.failed = []


    def compile(self, source_file,  file_type="original"):
        # print(source_file)
        output_executable = os.path.splitext(os.path.basename(source_file))[0]
        target_path = self.target_dir + ("original" if file_type == "original" else "protected") + "/" + source_file
        output_path = self.output_dir + ("original" if file_type == "original" else "protected") + "/" + output_executable

        process = subprocess.Popen(self.command + target_path + " -o " + output_path + " -lm", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=self.work_dir, shell=True)
        stdout, stderr = process.communicate()
        print(stderr)
        if process.returncode != 0:
            print("* [Failed] " + source_file + "compiled failed.")
            self.failed.append(source_file)
        else:
            print("[Success] " + source_file + "compiled success.")
            self.success.append(source_file)
        # self.__handle_output(stdout, stderr)
    

    def compile_all_benchmarks(self, file_type="original"):
        print("Start compile...")
        base_dir = "benchmark/" + file_type
        for folder_name in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder_name)
            if os.path.isdir(folder_path):
                for file_name in os.listdir(folder_path):
                    if file_name.endswith('.c'):
                        self.compile(os.path.join(folder_name, file_name), file_type)
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

    def __handle_output(self, stdout, stderr):
        # This method can be used to log the output to a file or take any other action based on the compilation output
        output_log_path = os.path.join(self.work_dir, self.output_dir, "compilation_log.txt")
        with open(output_log_path, "w") as log_file:
            if stderr:
                log_file.write("Compilation Errors:\n")
                log_file.write(stderr)
            if stdout:
                log_file.write("\nCompilation Output:\n")
                log_file.write(stdout)
        print(f"Compilation output has been logged to {output_log_path}")
