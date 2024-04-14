import csv
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class PerformanceComparison:
    def __init__(self, csv_file_path):
        """
        Initializes the PerformanceComparison class by loading the CSV data.
        """
        self.relative_work_dir = "../build/"
        self.csv_file_path = csv_file_path
        self.headers = ["File Name", "File Type", "Cycles", "Instructions", "Cache Misses", "Cache References", "Elapsed Time", "User Time", "System Time", "CPU Percentage", "Maximum resident set size (kbytes)"]
        self.data = pd.read_csv(csv_file_path)

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.work_dir = os.path.join(self.script_dir)
        self.before_process_csv_path = os.path.join(self.work_dir, "../data/csv/")

        # Ensure data is integrated from multiple CSV files
        self.__integrate_data()


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
        plt.savefig(f"data/plt/Analysis of {metric}.png", dpi=1080)


    def plot_boxplot_comparison(self, metric):
        """
        Plots a boxplot for each unique file name (without type), showing the distribution of the given metric for 'no_extension', 'original', 'protected' file types. The y-axis is displayed on a logarithmic scale.
        """
        print(metric)
        
        # Unique file names (without types)
        file_names = sorted(set(self.integrated_data['File Name']))

        # Prepare figure
        plt.figure(figsize=(len(file_names) * 2, 6))

        # Define colors for each file type
        colors = ['#D7191C', '#2C7BB6', '#FABE2C']
        file_types = ['no_extension', 'original', 'protected']

        positions = np.arange(len(file_names)) * 4  # Spacing between groups of box plots

        for i, file_name in enumerate(file_names):
            # Data for the current file name across all file types
            for j, file_type in enumerate(file_types):
                data = self.integrated_data[(self.integrated_data['File Name'] == file_name) & (self.integrated_data['File Type'] == file_type)][metric].dropna()
                pos = positions[i] + j
                box = plt.boxplot(data, positions=[pos], widths=0.5, patch_artist=True,
                                boxprops=dict(facecolor=colors[j], color=colors[j]),
                                medianprops=dict(color='black'),
                                whiskerprops=dict(color=colors[j]),
                                capprops=dict(color=colors[j]),
                                flierprops=dict(markeredgecolor=colors[j], marker='o', markersize=5))
            
        # Customizing the plot
        plt.xticks(positions + 1, file_names, rotation=45, ha="right")
        plt.ylabel(metric)
        plt.title(f'Comparison of {metric} Across File Types')
        plt.yscale('log')

        # Adding legend manually
        for i, file_type in enumerate(file_types):
            plt.plot([], c=colors[i], label=file_type.capitalize(), marker='s', linestyle='None', markersize=10)
        plt.legend()

        plt.tight_layout()
        plt.savefig(f"data/plt/Box Diagram of {metric}.png", dpi=1080)


    def __integrate_data(self):
        """
        Reads and integrates data from multiple CSV files into a single DataFrame.
        """
        all_data = []

        # Iterate over all CSV files in the specified directory
        for file in os.listdir(self.before_process_csv_path):
            if file.endswith(".csv"):
                file_path = os.path.join(self.before_process_csv_path, file)
                # Extracting file_name (without type) and file_type from the file name
                base_name = file[:-4]  # Remove '.csv'
                parts = base_name.rsplit('-', 1)  # Split on the last underscore to separate type
                file_name, file_type = parts[0], parts[1]
                
                temp_df = pd.read_csv(file_path)
                temp_df['File Name'] = file_name
                temp_df['File Type'] = file_type
                all_data.append(temp_df)

        # Combine all data into a single DataFrame
        self.integrated_data = pd.concat(all_data, ignore_index=True)


    def visualize_performance_loss_distribution(self, metric):
        """
        Visualizes the distribution of performance loss percentage for 'original' and 'protected' compared to 'no_extension'.
        :param integrated_data: DataFrame containing integrated data with 'File Name', 'File Type', and the metric columns.
        :param metric: The metric to evaluate performance loss on.
        """
        # Calculate performance loss percentage for each file name
        performance_loss = []
        file_names = self.integrated_data['File Name'].unique()
        
        for file_name in file_names:
            no_ext_median = self.integrated_data[(self.integrated_data['File Name'] == file_name) & (self.integrated_data['File Type'] == 'no_extension')][metric].median()
            for file_type in ['original', 'protected']:
                file_median = self.integrated_data[(self.integrated_data['File Name'] == file_name) & (self.integrated_data['File Type'] == file_type)][metric].median()
                loss_percentage = ((file_median - no_ext_median) / no_ext_median) * 100
                performance_loss.append({'File Name': file_name, 'File Type':"Degratation of " + file_type + " from no_extension", 'Loss Percentage': loss_percentage})
        
        performance_loss_df = pd.DataFrame(performance_loss)
        
        # Plotting
        plt.figure(figsize=(12, 6))
        
        # Histogram
        plt.subplot(1, 2, 1)
        sns.histplot(data=performance_loss_df, x='Loss Percentage', hue='File Type', kde=False, bins=20)
        plt.title('Histogram of Loss Percentage')
        plt.xlabel('Loss Percentage')
        plt.ylabel('Frequency')

                # Annotations of medians
        medians_text = "Medium:\n"
        for file_type in performance_loss_df['File Type'].unique():
            median_val = performance_loss_df[performance_loss_df['File Type'] == file_type]['Loss Percentage'].median()
            medians_text += f"{file_type}: {median_val:.2f}%\n"
        
        # Place medians in a text box on the plot
        plt.gcf().text(0.2, 0.75, medians_text, fontsize=9, verticalalignment='center', bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="black", lw=1, alpha=0.5))
        
        # Density Plot
        plt.subplot(1, 2, 2)
        ax = sns.kdeplot(data=performance_loss_df, x='Loss Percentage', hue='File Type', fill=True)
        plt.title('Density Plot of Loss Percentage')
        plt.xlabel('Loss Percentage')
        plt.ylabel('Density')

        plt.tight_layout()
        plt.savefig(f"data/plt/Distribution Visualization of {metric}.png", dpi=1080)
        # plt.show()
