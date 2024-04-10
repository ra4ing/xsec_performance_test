import pandas as pd
import matplotlib.pyplot as plt

class PerformanceComparison:
    def __init__(self, csv_file_path):
        """
        Initializes the PerformanceComparison class by loading the CSV data.
        """
        self.data = pd.read_csv(csv_file_path)
    
    def plot_comparison(self, metric):
        """
        Plots a bar chart comparison for the given metric between original and protected file types, using file names as x-axis labels,
        and shows the performance degradation percentage. The y-axis is displayed on a logarithmic scale.
        """
        print(metric)
        # Ensuring that file names are unique and sorted for consistent plotting
        file_names = sorted(set(self.data['File Name']))
        
        # Initialize a DataFrame to hold the metric values for original and protected types
        comparison_data = pd.DataFrame(index=file_names, columns=['Original', 'Protected'])
        
        # Populate the DataFrame with metric values
        for file_name in file_names:
            original_value = self.data[(self.data['File Name'] == file_name) & (self.data['File Type'] == 'original')][metric].values
            protected_value = self.data[(self.data['File Name'] == file_name) & (self.data['File Type'] == 'protected')][metric].values
            comparison_data.at[file_name, 'Original'] = original_value[0] if len(original_value) > 0 else None
            comparison_data.at[file_name, 'Protected'] = protected_value[0] if len(protected_value) > 0 else None
        
        # Calculate the performance degradation percentage
        comparison_data['Degradation (%)'] = ((comparison_data['Protected'] - comparison_data['Original']) / comparison_data['Original']) * 100
        
        # Width of the bars in the bar chart
        bar_width = 0.35
        
        # Plotting
        plt.figure(figsize=(14, 8))
        indices = range(len(comparison_data))
        plt.bar([i - bar_width/2 for i in indices], comparison_data['Original'], width=bar_width, label='Original', alpha=0.8)
        plt.bar([i + bar_width/2 for i in indices], comparison_data['Protected'], width=bar_width, label='Protected', alpha=0.8)
        
        # Annotate performance degradation percentage
        for idx, pct in enumerate(comparison_data['Degradation (%)']):
            if not pd.isnull(pct):  # Check if pct is not NaN
                plt.text(idx, max(comparison_data.loc[file_names[idx], ['Original', 'Protected']]), f'{pct:.2f}%', ha='center', va='bottom')
        
        # Using logarithmic scale for y-axis if necessary
        plt.yscale('log')
        
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


