'''
   CS5001
   Final Project
   Fall 2024
   Tong Wu
''' 

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import requests

# Import your custom modules
from commodity import Commodity
from monthly_commodity_price_index import MonthlyCommodityPriceIndex
from model import Model
from visualization import Visualization
from data_process import data_process
from config import url_commodity, url_price_index, url_regional

class Interface:
    """
    A class to create and manage the trade analysis dashboard interface.
    
    This class handles the creation of the graphical user interface for the trade
    analysis dashboard, including data visualization, analysis controls, and result
    display. It integrates various data processing and analysis components to
    provide a comprehensive trade analysis tool.
    
    Attributes:
        root (tk.Tk): Main window of the application
        viz (Visualization): Visualization utility instance
        model (Model): Data analysis model instance
        analysis_results: Storage for analysis results
        main_frame (ttk.Frame): Main container frame
        left_frame (ttk.Frame): Left side control panel
        right_frame (ttk.Frame): Right side display area
        selected_product: Currently selected product for analysis
    """

    def __init__(self):
        """
        Initialize the main interface window and setup UI components.
        """
        self.root = tk.Tk()
        self.root.title("Trade Analysis Dashboard")
        self.root.geometry("1600x900")  # Increased window size
        
        self.viz = Visualization()
        self.model = Model()
        
        # Store analysis results for all products
        self.analysis_results = None
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for main frame
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)  # Give more weight to plot column
        self.main_frame.rowconfigure(2, weight=1)  # Make results area expandable
        
        # Create left and right frames
        self.left_frame = ttk.Frame(self.main_frame)
        self.right_frame = ttk.Frame(self.main_frame)
        
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        self.right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Configure weights for right frame
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)
        
        # Add selected_product as instance variable
        self.selected_product = None
        
        self._create_product_selection()
        self._create_analysis_buttons()
        self._create_results_area()
        self._create_plot_area()

    def _create_product_selection(self):
        """
        Create the product selection area in the interface.
        
        Sets up a listbox for product selection and associated controls.
        """
        # Product selection frame
        product_frame = ttk.LabelFrame(self.left_frame, text="Product Selection", padding="5")
        product_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Configure column weights
        product_frame.columnconfigure(0, weight=1)
        
        # Product listbox with increased height and width
        self.product_listbox = tk.Listbox(product_frame, height=15, width=60)
        self.product_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        scrollbar = ttk.Scrollbar(product_frame, orient=tk.VERTICAL, command=self.product_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        h_scrollbar = ttk.Scrollbar(product_frame, orient=tk.HORIZONTAL, command=self.product_listbox.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.product_listbox.configure(yscrollcommand=scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.product_listbox.configure(wrap=None)
        
        # Configure row weight to allow vertical expansion
        product_frame.rowconfigure(0, weight=1)

    def _create_analysis_buttons(self):
        """
        Create analysis control buttons.
        
        Sets up buttons for different types of analysis operations.
        """
        self.button_frame = ttk.LabelFrame(self.left_frame, text="Analysis Options", padding="5")
        self.button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Create buttons (initially disabled)
        buttons = [
            ("Correlation Analysis", self._run_correlation_analysis),
            ("Export Distribution", self._show_export_distribution),
            ("Export Trends", self._show_export_trends),
            ("Import Distribution", self._show_import_distribution),
            ("Import Trends", self._show_import_trends)
        ]
        
        # Configure grid weights
        for i in range(2):  # rows
            self.button_frame.rowconfigure(i, weight=1)
        for i in range(3):  # columns
            self.button_frame.columnconfigure(i, weight=1)
        
        # Create and grid buttons
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(self.button_frame, text=text, command=command, state='disabled')
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky=(tk.W, tk.E))

    def _create_results_area(self):
        """
        Create the results display area.
        
        Sets up a text widget for displaying analysis results.
        """
        results_frame = ttk.LabelFrame(self.left_frame, text="Analysis Results Preview", padding="5")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure weights
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Text widget for results
        self.results_text = tk.Text(results_frame, height=15, width=60)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for results
        results_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        results_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=results_scroll.set)

    def _create_plot_area(self):
        """
        Create the plotting area for data visualization.
        
        Sets up a frame for displaying matplotlib plots.
        """
        # Create plot frame
        self.plot_frame = ttk.LabelFrame(self.right_frame, text="Visualization", padding="5")
        self.plot_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure weights for plot frame
        self.plot_frame.columnconfigure(0, weight=1)
        self.plot_frame.rowconfigure(0, weight=1)
        
        # Create initial empty figure
        self.figure = Figure(figsize=(8, 6))
        self.plot_canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def _update_plot(self, figure):
        """
        Update the plot display with a new figure
        
        Parameters:
            figure: matplotlib Figure object to display
            
        Raises:
            ValueError: If figure is invalid
        """
        if figure is None:
            raise ValueError("Invalid figure object")
        
        # Clear existing plot if any
        if hasattr(self, 'plot_canvas') and self.plot_canvas is not None:
            self.plot_canvas.get_tk_widget().destroy()
        
        # Create new canvas with the figure
        self.plot_canvas = FigureCanvasTkAgg(figure, master=self.plot_frame)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Force update
        self.root.update_idletasks()

    def _load_products(self):
        """
        Load products into listbox
        
        Returns:
            bool: True if products loaded successfully, False otherwise
        """
        if not hasattr(self, 'commodity_pivot') or self.commodity_pivot.empty:
            return False
        
        products = sorted(self.commodity_pivot.index.get_level_values(
            'North American Product Classification System (NAPCS)').unique())
        
        if not products:
            return False
        
        self.product_listbox.delete(0, tk.END)
        for product in products:
            self.product_listbox.insert(tk.END, product)
        
        return True

    def _run_correlation_analysis(self):
        """
        Execute correlation analysis for the selected product
        """
        try:
            # Validate product selection
            self._check_product_selected()
            
            # Get product data
            product_data = self.commodity_pivot.xs(self.selected_product, 
                level='North American Product Classification System (NAPCS)')
            
            # Validate price index data
            if not hasattr(self, 'price_index_pivot') or self.price_index_pivot.empty:
                raise ValueError("Price index data not loaded")
            
            # Perform correlation analysis
            correlation_data = self.model.correlation_analysis(product_data, self.price_index_pivot)
            if not correlation_data:
                raise ValueError("Failed to perform correlation analysis")
            
            # Validate correlation results
            required_fields = ['correlation', 'scatter_data', 'regression_equation']
            for field in required_fields:
                if field not in correlation_data:
                    raise ValueError(f"Missing required correlation data: {field}")
            
            self.analysis_results = {'correlation_data': correlation_data}
            
            # Create and update plot
            fig = self.viz.plot_correlation_scatter(
                correlation_data['scatter_data'],
                correlation_data.get('regression_equation')
            )
            self._update_plot(fig)
        except Exception as e:
            self._handle_error(e)

    def _show_export_distribution(self):
        """
        Display export distribution analysis showing top 5 regions and Others
        
        Raises:
            ValueError: If data processing or visualization fails
        """
        # Validate product selection
        self._check_product_selected()
        
        # Filter regional data for selected product
        regional_df_filtered = self.regional_df[
            self.regional_df['North American Product Classification System (NAPCS)'] == self.selected_product
        ].copy()
        
        if regional_df_filtered.empty:
            raise ValueError("No regional data available for this product")
        
        regional_df_filtered.loc[:, 'REF_DATE'] = pd.to_datetime(regional_df_filtered['REF_DATE'])
        regional_results = self.model.analyze_regional_trade_share(regional_df_filtered)
        
        if not regional_results or 'Export' not in regional_results:
            raise ValueError("Failed to analyze regional trade data")
        
        # Create DataFrame with all regions
        export_data = pd.DataFrame({
            'Region': [region for region, _ in regional_results['Export']['top_regions']],
            'Share': [share for _, share in regional_results['Export']['top_regions']]
        })
        
        # Create and display plot
        fig = self.viz.plot_regional_trade_pie(export_data, 'Export')
        self._update_plot(fig)
        
        # Display results in text area
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Export Distribution Analysis for {self.selected_product}:\n")
        self.results_text.insert(tk.END, "-" * 50 + "\n")
        self.results_text.insert(tk.END, "Top 5 Regions:\n")
        
        # Display top 5 regions in text
        top_5_data = export_data.nlargest(5, 'Share')
        for _, row in top_5_data.iterrows():
            self.results_text.insert(tk.END, f"{row['Region']}: {row['Share']:.1f}%\n")
        
        # Display Others
        others_share = export_data.nsmallest(len(export_data)-5, 'Share')['Share'].sum()
        self.results_text.insert(tk.END, f"Others: {others_share:.1f}%\n")

    def _show_export_trends(self):
        """Show export trends line plot"""
        try:
            if not self._check_product_selected():
                return
            
            # Filter regional data for selected product
            regional_df_filtered = self.regional_df[
                self.regional_df['North American Product Classification System (NAPCS)'] == self.selected_product
            ].copy()
            
            if regional_df_filtered.empty:
                messagebox.showwarning("Warning", "No regional data available for this product")
                return
            
            regional_df_filtered.loc[:, 'REF_DATE'] = pd.to_datetime(regional_df_filtered['REF_DATE'])
            regional_results = self.model.analyze_regional_trade_share(regional_df_filtered)
            
            if regional_results and 'Export' in regional_results and 'trends' in regional_results['Export']:
                trends_data = regional_results['Export']['trends']
                
                # Create and display plot
                fig = self.viz.plot_monthly_trends(trends_data, 'Export')
                self._update_plot(fig)
                
                # Display results in text area
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "Export Trends Analysis:\n")
                self.results_text.insert(tk.END, "-" * 30 + "\n")
                self.results_text.insert(tk.END, str(trends_data))
                
        except Exception as e:
            self._handle_error(e)

    def _show_import_distribution(self):
        """
        Display import distribution analysis showing top 5 regions and Others
        
        Raises:
            ValueError: If data processing or visualization fails
        """
        # Validate product selection
        self._check_product_selected()
        
        # Filter regional data for selected product
        regional_df_filtered = self.regional_df[
            self.regional_df['North American Product Classification System (NAPCS)'] == self.selected_product
        ].copy()
        
        if regional_df_filtered.empty:
            raise ValueError("No regional data available for this product")
        
        regional_df_filtered.loc[:, 'REF_DATE'] = pd.to_datetime(regional_df_filtered['REF_DATE'])
        regional_results = self.model.analyze_regional_trade_share(regional_df_filtered)
        
        if not regional_results or 'Import' not in regional_results:
            raise ValueError("Failed to analyze regional trade data")
        
        # Get top 5 regions and calculate Others
        top_regions = regional_results['Import']['top_regions'][:5]  # Get only top 5
        other_share = sum(share for _, share in regional_results['Import']['top_regions'][5:])
        
        # Create DataFrame with top 3 and Others
        import_data = pd.DataFrame({
            'Region': [region for region, _ in top_regions] + ['Others'],
            'Share': [share for _, share in top_regions] + [other_share]
        })
        
        # Create and display plot
        fig = self.viz.plot_regional_trade_pie(import_data, 'Import')
        self._update_plot(fig)
        
        # Display results in text area
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Import Distribution Analysis:\n")
        self.results_text.insert(tk.END, "-" * 30 + "\n")
        self.results_text.insert(tk.END, "Top 5 Regions:\n")
        for i, (region, share) in enumerate(top_regions, 1):
            self.results_text.insert(tk.END, f"{i}. {region}: {share:.1f}%\n")
        self.results_text.insert(tk.END, f"Others: {other_share:.1f}%\n")

    def _show_import_trends(self):
        """Show import trends line plot"""
        try:
            if not self._check_product_selected():
                return
            
            # Filter regional data for selected product
            regional_df_filtered = self.regional_df[
                self.regional_df['North American Product Classification System (NAPCS)'] == self.selected_product
            ].copy()
            
            if regional_df_filtered.empty:
                messagebox.showwarning("Warning", "No regional data available for this product")
                return
            
            regional_df_filtered.loc[:, 'REF_DATE'] = pd.to_datetime(regional_df_filtered['REF_DATE'])
            regional_results = self.model.analyze_regional_trade_share(regional_df_filtered)
            
            if regional_results and 'Import' in regional_results and 'trends' in regional_results['Import']:
                trends_data = regional_results['Import']['trends']
                
                # Create and display plot
                fig = self.viz.plot_monthly_trends(trends_data, 'Import')
                self._update_plot(fig)
                
                # Display results in text area
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "Import Trends Analysis:\n")
                self.results_text.insert(tk.END, "-" * 30 + "\n")
                self.results_text.insert(tk.END, str(trends_data))
                
        except Exception as e:
            self._handle_error(e)

    def _check_product_selected(self):
        """
        Check if a product is selected
        
        Returns:
            bool: True if product is selected
            
        Raises:
            ValueError: If no product is selected
        """
        selected_idx = self.product_listbox.curselection()
        if not selected_idx:
            raise ValueError("Please select a product first")
        
        self.selected_product = self.product_listbox.get(selected_idx)
        if not self.selected_product:
            raise ValueError("Invalid product selection")
        
        return True

    def _handle_error(self, error):
        """Handle and display errors"""
        messagebox.showerror("Error", f"Analysis failed: {str(error)}")

    def _display_all_results(self):
        """
        Display all analysis results
        
        Raises:
            ValueError: If results display fails
        """
        if not self.selected_product:
            raise ValueError("No product selected")
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Analysis Results for {self.selected_product}:\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        
        if not self.analysis_results:
            raise ValueError("No analysis results available")
        
        # Display correlation results
        if 'correlation_data' in self.analysis_results:
            corr_data = self.analysis_results['correlation_data']
            self.results_text.insert(tk.END, "Correlation Analysis:\n")
            self.results_text.insert(tk.END, "-" * 30 + "\n")
            
            # Display correlation coefficient
            correlation = corr_data.get('correlation')
            if correlation is None:
                raise ValueError("Missing correlation coefficient")
            self.results_text.insert(tk.END, f"Correlation coefficient: {correlation:.4f}\n")
            
            # Display other statistics
            required_stats = ['sample_size', 'mean_net_total', 'std_net_total', 
                             'mean_terms_of_trade', 'std_terms_of_trade']
            for stat in required_stats:
                if stat not in corr_data:
                    raise ValueError(f"Missing required statistic: {stat}")
            
            self.results_text.insert(tk.END, f"Sample size: {corr_data['sample_size']}\n")
            self.results_text.insert(tk.END, "\nDescriptive Statistics:\n")
            self.results_text.insert(tk.END, f"Net Total Mean: {corr_data['mean_net_total']:,.2f}\n")
            self.results_text.insert(tk.END, f"Net Total Std: {corr_data['std_net_total']:,.2f}\n")
            self.results_text.insert(tk.END, f"Terms of Trade Mean: {corr_data['mean_terms_of_trade']:.2f}\n")
            self.results_text.insert(tk.END, f"Terms of Trade Std: {corr_data['std_terms_of_trade']:.2f}\n")

    def run(self):
        """
        Start the application main loop.
        
        Initializes data loading and starts the tkinter event loop.
        """
        # Start preloading data
        self._preload_data()
        # Start main loop
        self.root.mainloop()

    def _clear_previous_results(self):
        """
        Clear all display areas.
        
        Resets the results text area and plot area.
        """
        # Clear text area
        if hasattr(self, 'results_text'):
            self.results_text.delete(1.0, tk.END)
        
        # Clear plot
        if hasattr(self, 'plot_canvas') and self.plot_canvas is not None:
            self.plot_canvas.get_tk_widget().destroy()
            self.plot_canvas = None
        
        # Reset analysis results
        self.analysis_results = None

    def _preload_commodity_data(self, data_processor):
        """
        Preload and process commodity data.
        
        Parameters:
            data_processor: DataProcess object for data processing operations
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If critical data loading or processing fails
        """
        try:
            # Load commodity data
            commodity_df = data_processor.read_from_csv('data/commodity_data.csv')
            if commodity_df.empty:
                raise ValueError("Commodity data file is empty")
            
            # Process data
            cleaned_commodity_df = data_processor.clean_commodity_data(commodity_df)
            self.commodity_pivot = data_processor.pivot_table_for_terms_of_trade(cleaned_commodity_df)
            
            # Create commodity objects
            self.commodity_object = []
            for _, row in cleaned_commodity_df.iterrows():
                self.commodity_object.append(Commodity(
                    row['REF_DATE'],
                    row['Trade'],
                    row['North American Product Classification System (NAPCS)'],
                    row['VALUE'],
                    row['SCALAR_FACTOR'],
                    row['GEO']
                ))
            return True
            
        except Exception as e:
            self.results_text.insert(tk.END, f"Error processing commodity data: {str(e)}\n")
            raise ValueError(f"Failed to process commodity data: {str(e)}")

    def _preload_price_index_data(self, data_processor):
        """
        Preload and process price index data.
        
        Parameters:
            data_processor: DataProcess object for data processing operations
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If critical data loading or processing fails
        """
        try:
            # Load price index data
            price_df = data_processor.read_from_csv('data/price_index_data.csv')
            if price_df.empty:
                raise ValueError("Failed to load price index data")
            
            # Process data
            cleaned_price_df = data_processor.clean_price_index_data(price_df)
            self.price_index_pivot = data_processor.calculate_terms_of_trade(cleaned_price_df)
            
            # Create price index objects
            self.price_index_object = []
            for _, row in cleaned_price_df.iterrows():
                self.price_index_object.append(MonthlyCommodityPriceIndex(
                    row['REF_DATE'],
                    row['Trade'],
                    row['North American Product Classification System (NAPCS)'],
                    row['VALUE'],
                    row['SCALAR_FACTOR']
                ))
            return True
            
        except Exception as e:
            self.results_text.insert(tk.END, f"Error processing price index data: {str(e)}\n")
            raise ValueError(f"Failed to process price index data: {str(e)}")

    def _preload_regional_data(self, data_processor):
        """
        Preload and process regional data.
        
        Parameters:
            data_processor: DataProcess object for data processing operations
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If critical data loading or processing fails
        """
        try:
            # Load regional data
            regional_df = data_processor.read_from_csv('data/regional_data.csv')
            if regional_df.empty:
                raise ValueError("Failed to load regional data")
            
            # Process data
            self.regional_df = data_processor.clean_regional_data(regional_df)
            
            # Create regional objects
            self.regional_object = []
            for _, row in self.regional_df.iterrows():
                self.regional_object.append(Commodity(
                    row['REF_DATE'],
                    row['Trade'],
                    row['North American Product Classification System (NAPCS)'],
                    row['VALUE'],
                    row['SCALAR_FACTOR'],
                    row['GEO']
                ))
            return True
            
        except Exception as e:
            self.results_text.insert(tk.END, f"Error processing regional data: {str(e)}\n")
            raise ValueError(f"Failed to process regional data: {str(e)}")

    def _preload_data(self):
        """
        Preload raw data in background.
        
        Downloads CSV files, saves them locally, then loads and processes the data.
        Shows progress and error messages in the interface.
        
        Returns:
            None
        
        Raises:
            ValueError: If critical data loading or processing fails
        """
        # Show loading message
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Loading data, please wait...\n")
        self.root.update()
        
        # Initialize data processor
        data_processor = data_process()
        
        try:
            # First download all required data
            if not self._download_data(data_processor):
                raise ValueError("Failed to download required data")
            
            # Then load and process all data types
            self._preload_commodity_data(data_processor)
            self._preload_price_index_data(data_processor)
            self._preload_regional_data(data_processor)
            
            # Load products into listbox
            if not self._load_products():
                raise ValueError("Failed to load products into listbox")
            
            # Clear loading message and show ready status
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Data loaded successfully. Ready for analysis.\n")
            
            # Enable buttons after loading
            self._enable_analysis_buttons()
            
        except Exception as e:
            error_msg = f"Failed to process data: {str(e)}"
            self.results_text.insert(tk.END, f"Error: {error_msg}\n")
            raise ValueError(error_msg)

    def _enable_analysis_buttons(self):
        """
        Enable all analysis buttons after data is loaded.
        
        Activates interface controls once data is ready for analysis.
        """
        for child in self.button_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.configure(state='normal')

    def _download_data(self, data_processor):
        """
        Download data files from URLs and save them locally.
        
        Parameters:
            data_processor: DataProcess object for data processing operations
            
        Returns:
            bool: True if all required data downloaded successfully
            
        Raises:
            ValueError: If downloading required data fails
        """
        # Define URLs and local file paths
        data_sources = {
            'commodity': {
                'url': url_commodity,
                'local_path': 'data/commodity_data.csv',
                'required': True
            },
            'price_index': {
                'url': url_price_index,
                'local_path': 'data/price_index_data.csv',
                'required': True
            },
            'regional': {
                'url': url_regional,
                'local_path': 'data/regional_data.csv',
                'required': True
            }
        }
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Download and save all data files
        for data_type, source in data_sources.items():
            try:
                # First try to read existing local file
                if os.path.exists(source['local_path']):
                    self.results_text.insert(tk.END, f"Using cached {data_type} data\n")
                    continue
                    
                # If local file doesn't exist, download data
                self.results_text.insert(tk.END, f"Downloading {data_type} data...\n")
                raw_data = data_processor.data_extraction(source['url'])
                if raw_data is None:
                    raise ValueError(f"Received empty data for {data_type}")
                    
                # Save downloaded data
                data_processor.save_to_csv(raw_data, source['local_path'])
                self.results_text.insert(tk.END, f"Successfully downloaded {data_type} data\n")
                
            except requests.RequestException as e:
                error_msg = f"Network error while downloading {data_type} data: {str(e)}"
                self.results_text.insert(tk.END, f"Error: {error_msg}\n")
                if source['required']:
                    raise ValueError(error_msg)
                
            except (IOError, OSError) as e:
                error_msg = f"File system error for {data_type} data: {str(e)}"
                self.results_text.insert(tk.END, f"Error: {error_msg}\n")
                if source['required']:
                    raise ValueError(error_msg)
                
            except Exception as e:
                error_msg = f"Unexpected error processing {data_type} data: {str(e)}"
                self.results_text.insert(tk.END, f"Error: {error_msg}\n")
                if source['required']:
                    raise ValueError(error_msg)
                
            finally:
                self.root.update()
        
        return True
