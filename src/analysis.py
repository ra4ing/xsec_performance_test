import csv
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class PerformanceComparison:
    def __init__(self, csv_file_path):
        """
        Initializes the PerformanceComparison class by loading the CSV data.
        """
        self.relative_work_dir = "../build/"
        self.csv_file_path = csv_file_path
        self.headers = ["File Name", "File Type", "Cycles", "Instructions", "Cache Misses", "Cache References", "Elapsed Time", "User Time", "System Time", "CPU Percentage", "Maximum resident set size (kbytes)"]
        self.data = pd.read_csv(csv_file_path)


    def __write_to_csv(self, metrics, file_name, file_type):
        row = [file_name, file_type] + [metrics.get(h, "N/A") for h in self.headers[2:]]
        with open(self.csv_file_path, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)
    

    def calculate_and_save_averages(self, file_type = "original"):
        """
        Calculates and returns the average values of each metric for both original and protected file types.
        """
        # Remove previous 'Average' entries for the given file type
        self.data = self.data[~((self.data['File Name'] == 'Average') & (self.data['File Type'] == file_type))]
        
        # Write the filtered data back to the CSV, effectively removing the old 'Average' entries
        self.data.to_csv(self.csv_file_path, index=False)
        # Initialize a dictionary to store the average metrics
        average_metrics = {}
        
        # List of metrics to calculate averages for
        metrics = ["Cycles", "Instructions", "Cache Misses", "Cache References", "Elapsed Time", "User Time", "System Time", "CPU Percentage", "Maximum resident set size (kbytes)"]
        
        for metric in metrics:
            # Calculate average for original files
            average_avg = self.data[self.data['File Type'] == file_type][metric].astype(float).mean()
            average_metrics[metric] = average_avg


        self.__write_to_csv(average_metrics, "Average", file_type)
        self.data = pd.read_csv(self.csv_file_path)


    def plot_comparison(self, metric):
        """
        Plots a bar chart comparison for the given metric between original and protected file types, using file names as x-axis labels,
        and shows the performance degradation percentage. The y-axis is displayed on a logarithmic scale.
        """
        print(metric)
        # Ensuring that file names are unique and sorted for consistent plotting
        file_names = sorted(set(self.data['File Name']))
        
        # Initialize a DataFrame to hold the metric values for original and protected types
        comparison_data = pd.DataFrame(index=file_names, columns=['No_Extension', 'Original', 'Protected'])
        
        # Populate the DataFrame with metric values
        for file_name in file_names:
            no_extension_value = self.data[(self.data['File Name'] == file_name) & (self.data['File Type'] == 'no_extension')][metric].values
            original_value = self.data[(self.data['File Name'] == file_name) & (self.data['File Type'] == 'original')][metric].values
            protected_value = self.data[(self.data['File Name'] == file_name) & (self.data['File Type'] == 'protected')][metric].values
            comparison_data.at[file_name, 'No_Extension'] = no_extension_value[0] if len(no_extension_value) > 0 else None
            comparison_data.at[file_name, 'Original'] = original_value[0] if len(original_value) > 0 else None
            comparison_data.at[file_name, 'Protected'] = protected_value[0] if len(protected_value) > 0 else None
        
        # Calculate the performance degradation percentage
        # comparison_data['Degradation (%) Original'] = ((comparison_data['Protected'] - comparison_data['Original']) / comparison_data['Original']) * 100
        comparison_data['Degradation (%) No_Extension vs Original'] = ((comparison_data['Original'] - comparison_data['No_Extension']) / comparison_data['No_Extension']) * 100
        comparison_data['Degradation (%) No_Extension vs Protected'] = ((comparison_data['Protected'] - comparison_data['No_Extension']) / comparison_data['No_Extension']) * 100

        
        # Width of the bars in the bar chart
        bar_width = 0.25
        
        # Plotting
        plt.figure(figsize=(14, 8))
        indices = np.arange(len(comparison_data))
        plt.bar(indices - bar_width, comparison_data['No_Extension'], width=bar_width, label='No Extension', alpha=0.8)
        plt.bar(indices, comparison_data['Original'], width=bar_width, label='Original', alpha=0.8)
        plt.bar(indices + bar_width, comparison_data['Protected'], width=bar_width, label='Protected', alpha=0.8)


        
        # Annotate performance degradation percentage
        for idx, (index, row) in enumerate(comparison_data.iterrows()):
            base_height = max(row[['No_Extension', 'Original', 'Protected']].dropna())
            # if not pd.isnull(row['Degradation (%) Original']):
            #     plt.text(idx, base_height * 1.05, f'{row["Degradation (%) Original"]:.2f}%', ha='center', va='bottom', rotation=75)
            if not pd.isnull(row['Degradation (%) No_Extension vs Original']):
                plt.text(idx - bar_width, base_height * 1.10, f'{row["Degradation (%) No_Extension vs Original"]:.2f}%', ha='center', va='bottom', color='blue', rotation=75)
            if not pd.isnull(row['Degradation (%) No_Extension vs Protected']):
                plt.text(idx + bar_width, base_height * 1.15, f'{row["Degradation (%) No_Extension vs Protected"]:.2f}%', ha='center', va='bottom', color='red', rotation=75)

        # plt.text(-0.5, base_height * 2.5, 'Red %: Degradation from No Extension to Protected', color='red', fontsize=10, verticalalignment='top')
        # plt.text(-0.5, base_height * 2.6, 'Blue %: Degradation from No Extension to Original', color='blue', fontsize=10, verticalalignment='top')


        # Using logarithmic scale for y-axis if necessary
        plt.yscale('log')

        # Determine the position for the static annotation on a log scale
        y_min, y_max = plt.ylim()
        log_range = np.log10(y_max) - np.log10(y_min)  # Calculate the log range of the current plot
        red_base_position = 10 ** (np.log10(y_max) - log_range * 0.03)
        blue_base_position = 10 ** (np.log10(y_max) - log_range * 0.06)

        plt.text(-1, red_base_position, 'Red %: Degradation from No Extension to Protected', color='red', fontsize=10, verticalalignment='top')
        plt.text(-1, blue_base_position, 'Blue %: Degradation from No Extension to Original', color='blue', fontsize=10, verticalalignment='top')

        # Adding plot details
        plt.title(f'Comparison of {metric} Between Original and Protected Files')
        plt.xlabel('File Name')
        plt.ylabel(metric)
        plt.xticks(indices, file_names, rotation=45, ha="right")
        plt.legend()
        plt.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
        plt.tight_layout()
        # plt.show()
        plt.savefig(f"data/Analysis of {metric}.png", dpi=1080)


