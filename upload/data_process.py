'''
   CS5001
   Final Project
   Fall 2024
   Tong Wu
''' 

import requests
import pandas as pd
from io import BytesIO
import os

class data_process:
    """
    A class to handle data processing operations.
    
    This class provides utility functions for data extraction, processing,
    and manipulation of DataFrames, including data fetching from URLs,
    column operations, and value transformations.
    """

    def __init__(self):
        """Initialize data_process class."""
        self.DATE_COLUMN = 'REF_DATE'
        self.TRADE_COLUMN = 'Trade'
        self.VALUE_COLUMN = 'VALUE'
        self.TERMS_OF_TRADE_COLUMN = 'Terms_of_Trade'
        self.TERMS_OF_TRADE_MULTIPLIER = 100

    def data_extraction(self, url):
        """
        Extract data from a given URL.
        
        Parameters:
            url (str): URL to extract data from
            
        Returns:
            bytes: Raw data content from URL
            
        Raises:
            ValueError: If URL is empty or invalid
            requests.exceptions.ConnectionError: If connection to URL fails
            requests.exceptions.HTTPError: If HTTP error occurs (e.g., 404, 500)
            requests.exceptions.Timeout: If request times out
            requests.exceptions.RequestException: For other request-related errors
        """
        if not url:
            raise ValueError("URL cannot be empty")
        
        try:
            response = requests.get(url, timeout=10)  # Add timeout parameter
            response.raise_for_status()  # This will raise HTTPError for 4XX and 5XX status codes
            return response.content
        
        except requests.exceptions.ConnectionError as e:
            raise requests.exceptions.ConnectionError(f"Failed to connect to URL: {url}. Error: {str(e)}")
        
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(f"HTTP error occurred: {str(e)}")
        
        except requests.exceptions.Timeout as e:
            raise requests.exceptions.Timeout(f"Request timed out after 10 seconds: {str(e)}")
        
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"An error occurred while fetching the URL: {str(e)}")

    def clean_commodity_data(self, df):
        """
        Clean commodity data
        
        Parameters:
            df (pd.DataFrame): Raw commodity data
            
        Returns:
            pd.DataFrame: Cleaned commodity data
            
        Raises:
            ValueError: If DataFrame is empty or missing required columns
        """
        if df is None or df.empty:
            raise ValueError("Input DataFrame cannot be empty")
            
        if 'VALUE' not in df.columns:
            raise ValueError("DataFrame missing required 'VALUE' column")
            
        # Create a copy of the dataframe
        df = df.copy()
        
        # Convert VALUE column to numeric, replacing non-numeric values with NaN
        df.loc[:, 'VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce')
        
        # Drop rows with NaN values
        df = df.dropna(subset=['VALUE'])
        
        if df.empty:
            raise ValueError("No valid data remains after cleaning")
            
        return df

    def clean_price_index_data(self, df):
        """
        Clean price index data
        
        Parameters:
            df (pd.DataFrame): Raw price index data
            
        Returns:
            pd.DataFrame: Cleaned price index data
            
        Raises:
            ValueError: If DataFrame is empty or missing required columns
        """
        if df is None or df.empty:
            raise ValueError("Input DataFrame cannot be empty")
            
        if 'VALUE' not in df.columns:
            raise ValueError("DataFrame missing required 'VALUE' column")
            
        # Create a copy of the dataframe
        df = df.copy()
        
        # Convert VALUE column to numeric, replacing non-numeric values with NaN
        df.loc[:, 'VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce')
        
        # Drop rows with NaN values
        df = df.dropna(subset=['VALUE'])
        
        if df.empty:
            raise ValueError("No valid data remains after cleaning")
            
        return df

    def clean_regional_data(self, df):
        """
        Clean regional data
        
        Parameters:
            df (pd.DataFrame): Raw regional data
            
        Returns:
            pd.DataFrame: Cleaned regional data
            
        Raises:
            ValueError: If DataFrame is empty or missing required columns
        """
        if df is None or df.empty:
            raise ValueError("Input DataFrame cannot be empty")
            
        if 'VALUE' not in df.columns:
            raise ValueError("DataFrame missing required 'VALUE' column")
            
        # Create a copy of the dataframe
        df = df.copy()
        
        # Convert VALUE column to numeric, replacing non-numeric values with NaN
        df.loc[:, 'VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce')
        
        # Drop rows with NaN values
        df = df.dropna(subset=['VALUE'])
        
        if df.empty:
            raise ValueError("No valid data remains after cleaning")
        
        # Replace 'Domestic export' and 'Re-export' with 'Export'
        old_values = ['Domestic export', 'Re-export']
        df = self.dataframe_value_replace(
            df, 'Trade', old_values, 'Export'
        )
            
        # Group and sum values
        group_keys = ['REF_DATE', 'GEO', 'Trade', 
                     'North American Product Classification System (NAPCS)',
                     'UOM', 'SCALAR_FACTOR']
        grouped_df = self.column_combination(df, group_keys)
        return grouped_df

    def data_processing_into_dataframe(self, data):
        """
        Convert raw data into pandas DataFrame
        
        Parameters:
            data (bytes): Raw data content
            
        Returns:
            pd.DataFrame: Processed DataFrame
        """
        return pd.read_csv(BytesIO(data), encoding='utf-8')

    def dataframe_column_drop(self, df, columns):
        """
        Remove specified columns from DataFrame
        
        Parameters:
            df (pd.DataFrame): Input DataFrame
            columns (list): List of columns to drop
            
        Returns:
            pd.DataFrame: DataFrame with specified columns removed
        """
        return df.drop(columns=columns)
    
    def dataframe_value_replace(self, df, column, old_value, new_value):
        """
        Replace values in specified column
        
        Parameters:
            df (pd.DataFrame): Input DataFrame
            column (str): Column name to perform replacement
            old_value (list): List of values to replace
            new_value (str): New value to use as replacement
            
        Returns:
            pd.DataFrame: DataFrame with replaced values
        """
        df.loc[df[column].isin(old_value), column] = new_value
        return df

    def column_combination(self, df, group_keys):
        """
        Combine data based on group keys
        
        Parameters:
            df (pd.DataFrame): Input DataFrame
            group_keys (list): Keys to group by
            
        Returns:
            pd.DataFrame: Grouped and summed DataFrame
        """
        return df.groupby(group_keys)['VALUE'].sum().reset_index()

    def save_to_csv(self, data, filepath):
        """
        Save data to a CSV file
        
        Parameters:
            data: Raw data to save
            filepath (str): Path where to save the CSV file
            
        Raises:
            ValueError: If filepath is invalid or empty
        """
        if not filepath:
            raise ValueError("Filepath cannot be empty")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save data to CSV
        with open(filepath, 'wb') as f:
            f.write(data)

    def read_from_csv(self, filepath):
        """
        Read data from a CSV file
        
        Parameters:
            filepath (str): Path to the CSV file
            
        Returns:
            pandas.DataFrame: DataFrame containing the CSV data
            
        Raises:
            ValueError: If filepath is invalid or empty
            FileNotFoundError: If CSV file does not exist
            pd.errors.EmptyDataError: If CSV file is empty
        """
        if not filepath:
            raise ValueError("Filepath cannot be empty")
            
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")
            
        df = pd.read_csv(filepath)
        if df.empty:
            raise pd.errors.EmptyDataError("CSV file is empty")
            
        return df

    def pivot_table_for_terms_of_trade(self, df):
        """
        Create pivot table for different products and their trade values.
        
        Creates a pivot table that shows export and import values for each product,
        and calculates the net total trade value.
        
        Parameters:
            df (pandas.DataFrame): Input dataframe containing trade data
            
        Returns:
            pandas.DataFrame: Pivot table with products and trade values, including net total
        """
        pivot_df = df.pivot_table(
            index=['REF_DATE', 'North American Product Classification System (NAPCS)'], 
            columns='Trade',
            values='VALUE',
            aggfunc='first'
        )
        
        # Add Net Total column (Exports - Imports)
        pivot_df['Net_Total'] = pivot_df['Export'] - pivot_df['Import']

        return pivot_df

    def calculate_terms_of_trade(self, df):
        """
        Calculate monthly terms of trade as (export price index / import price index) * 100
        
        Returns:
            pandas.DataFrame: DataFrame with monthly terms of trade calculations
                            or empty DataFrame if calculation fails
        """
        try:
            # Pivot the data to get export and import values for each month
            pivot_df = df.pivot_table(
                index='REF_DATE',
                columns='Trade',
                values='VALUE',
                aggfunc='first'
            )
            
            # Check required columns
            if 'Export' not in pivot_df.columns or 'Import' not in pivot_df.columns:
                print("Missing required trade data for calculation")
                return pd.DataFrame()
            
            # Calculate terms of trade
            pivot_df[self.TERMS_OF_TRADE_COLUMN] = (
                pivot_df['Export'] / pivot_df['Import']
            ) * self.TERMS_OF_TRADE_MULTIPLIER
            
            return pivot_df
            
        except Exception as e:
            print(f"Error calculating terms of trade: {str(e)}")
            return pd.DataFrame()
