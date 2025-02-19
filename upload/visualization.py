'''
   CS5001
   Final Project
   Fall 2024
   Tong Wu
''' 

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class Visualization:
    """
    Class for creating visualizations for the data analysis results
    """
    def __init__(self):
        """Initialize visualization class"""
        plt.style.use('default')

    def plot_correlation_scatter(self, scatter_data, regression_equation=None):
        """Create scatter plot with regression line
        
        Parameters:
            scatter_data (pd.DataFrame): DataFrame with 'Terms_of_Trade' and 'Net_Total' columns
            regression_equation (str): The equation of the regression line
            
        Returns:
            matplotlib.figure.Figure: The created scatter plot
        """
        # Create figure
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Create scatter plot
        ax.scatter(scatter_data['Terms_of_Trade'], scatter_data['Net_Total'], 
                  alpha=0.5, color='blue', label='Data Points')
        
        if regression_equation:
            # Plot regression line
            x = scatter_data['Terms_of_Trade']
            y_pred = scatter_data['Regression_Line']
            ax.plot(x, y_pred, color='red', linestyle='--', label='Regression Line')
            
            # Add regression equation
            ax.text(0.05, 0.95, f'Equation: {regression_equation}', 
                   transform=ax.transAxes, fontsize=10)
        
        ax.set_title('Terms of Trade vs Net Trade Values')
        ax.set_xlabel('Terms of Trade')
        ax.set_ylabel('Net Trade Values')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Adjust layout
        fig.tight_layout()
        
        return fig

    def plot_regional_trade_pie(self, data, trade_type):
        """
        Create a pie chart for regional trade distribution
        
        Parameters:
            data (pd.DataFrame): DataFrame containing Region and Share columns
            trade_type (str): Type of trade ('Export' or 'Import')
            
        Returns:
            matplotlib.figure.Figure: Figure containing the pie chart
            
        Raises:
            ValueError: If data is invalid or visualization fails
        """
        if data is None or data.empty:
            raise ValueError("Invalid data for pie chart")
        
        if 'Region' not in data.columns or 'Share' not in data.columns:
            raise ValueError("Data must contain 'Region' and 'Share' columns")
        
        if trade_type not in ['Export', 'Import']:
            raise ValueError("Trade type must be either 'Export' or 'Import'")
        
        # Create figure
        fig = Figure(figsize=(10, 8))
        ax = fig.add_subplot(111)
        
        # Get top 5 regions and combine others
        top_5_regions = data.nlargest(5, 'Share')
        others_share = data.nsmallest(len(data)-5, 'Share')['Share'].sum()
        
        # Combine data for plotting
        plot_data = pd.concat([
            top_5_regions,
            pd.DataFrame({'Region': ['Others'], 'Share': [others_share]})
        ])
        
        # Define colors and explode
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#99ccff']
        explode = [0.05] * len(plot_data)  # Slight separation for all slices
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            plot_data['Share'],
            explode=explode,
            labels=plot_data['Region'],
            colors=colors,
            autopct='%1.1f%%',
            pctdistance=0.85,
            startangle=90
        )
        
        # Add title
        ax.set_title(f'Regional {trade_type} Distribution', pad=20, size=14)
        
        # Create legend
        legend_labels = [f"{region} ({share:.1f}%)" 
                        for region, share in zip(plot_data['Region'], plot_data['Share'])]
        ax.legend(
            wedges,
            legend_labels,
            title="Regions",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        
        # Style the chart
        plt.setp(autotexts, size=8, weight="bold")
        plt.setp(texts, size=8)
        
        # Adjust layout to prevent legend cutoff
        fig.tight_layout()
        
        return fig

    def plot_monthly_trends(self, trends_df, trade_type):
        """Create line plot for monthly trends"""
        # Create figure
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        # Process date column
        date_col = 'REF_DATE' if 'REF_DATE' in trends_df.columns else 'Date'
        if not pd.api.types.is_datetime64_any_dtype(trends_df[date_col]):
            trends_df[date_col] = pd.to_datetime(trends_df[date_col])
        
        # Get value column
        value_col = 'VALUE' if 'VALUE' in trends_df.columns else 'Value'
        
        # Get region column
        region_col = 'Region' if 'Region' in trends_df.columns else 'GEO'
        
        # Get top 5 regions
        top_regions = (trends_df.groupby(region_col)[value_col]
                      .mean()
                      .sort_values(ascending=False)
                      .head(5)
                      .index)
        
        # Filter data for top 5 regions
        trends_df = trends_df[trends_df[region_col].isin(top_regions)]
        
        # Plot trends
        colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC']
        for i, region in enumerate(top_regions):
            region_data = trends_df[trends_df[region_col] == region]
            ax.plot(region_data[date_col], 
                   region_data[value_col], 
                   label=region,
                   color=colors[i],
                   marker='o',
                   markersize=4,
                   linewidth=2)
        
        ax.set_title(f'Monthly {trade_type} Trends by Region')
        ax.set_xlabel('Date')
        ax.set_ylabel('Value (CAD)')
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        ax.tick_params(axis='x', rotation=45)
        
        # Add legend
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        # Adjust layout
        fig.tight_layout()
        
        return fig

    def visualize_analysis_results(self, analysis_results):
        """Create all visualizations for the analysis results"""
        try:
            # Clear any existing windows
            self.clear_plots()
            
            # Create correlation plot
            if 'correlation_data' in analysis_results:
                scatter_data = analysis_results['correlation_data'].get('scatter_data')
                regression_equation = analysis_results['correlation_data'].get('regression_equation')
                if scatter_data is not None and not scatter_data.empty:
                    self.plot_correlation_scatter(scatter_data, regression_equation)

            # Create regional trade visualizations
            if 'regional_data' in analysis_results:
                regional_data = analysis_results['regional_data']
                
                # Export visualizations
                if 'Export' in regional_data:
                    export_data = pd.DataFrame({
                        'Region': [item[0] for item in regional_data['Export']['top_regions']],
                        'Share': [item[1] for item in regional_data['Export']['top_regions']]
                    })
                    self.plot_regional_trade_pie(export_data, 'Export')
                    
                    if 'trends' in regional_data['Export']:
                        self.plot_monthly_trends(regional_data['Export']['trends'], 'Export')
                
                # Import visualizations
                if 'Import' in regional_data:
                    import_data = pd.DataFrame({
                        'Region': [item[0] for item in regional_data['Import']['top_regions']],
                        'Share': [item[1] for item in regional_data['Import']['top_regions']]
                    })
                    self.plot_regional_trade_pie(import_data, 'Import')
                    
                    if 'trends' in regional_data['Import']:
                        self.plot_monthly_trends(regional_data['Import']['trends'], 'Import')
        
        except Exception as e:
            print(f"Error in visualization: {str(e)}")
