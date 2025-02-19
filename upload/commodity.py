'''
   CS5001
   Final Project
   Fall 2024
   Tong Wu
''' 

import data_process
import requests
import pandas as pd
from io import BytesIO
from IPython.display import display

class Commodity:
    """
    A class to handle commodity data processing and analysis.
    
    This class provides functionality to process and analyze commodity trade data,
    including data extraction, transformation, and visualization.
    
    Attributes:
        ref_date (pd.Series): Reference date for the commodity data
        trade (pd.Series): Trade type for the commodity data
        NAPCS (pd.Series): North American Product Classification System (NAPCS) for the commodity data
        value (pd.Series): Value for the commodity data
        scalar_factor (pd.Series): Scalar factor for the commodity data
        GEO (str): Geographic region for the commodity data
        net_total (float): Net total for the commodity data
    """
    
    def __init__(self, ref_date, trade, NAPCS, value, scalar_factor, GEO='Canada', net_total=0):
        """
        Initialize Commodity class with cleaned data
        
        Parameters:
            ref_date (pd.Series): Reference date for the commodity data
            trade (pd.Series): Trade type for the commodity data
            NAPCS (pd.Series): North American Product Classification System (NAPCS) for the commodity data
            value (pd.Series): Value for the commodity data
            scalar_factor (pd.Series): Scalar factor for the commodity data
            GEO (str or pd.Series): Geographic region for the commodity data
            net_total (float): Net total for the commodity data
            
        Raises:
            ValueError: If input data is invalid
        """
        if (not isinstance(ref_date, str) or 
            not isinstance(trade, str) or 
            not isinstance(NAPCS, str) or 
            not isinstance(value, (int, float)) or 
            not isinstance(scalar_factor, str)):
            raise ValueError("Data type is invalid")

        # Validate series lengths
        if any((x) == None for x in [ref_date, trade, NAPCS, value, scalar_factor]):
            raise ValueError("Input series must have the same length")
        
        # Validate value types
        try:
            pd.to_numeric(value, errors='raise')
        except ValueError:
            raise ValueError("Value series must contain numeric data")
        
        # Handle GEO parameter
        if isinstance(GEO, pd.Series):
            if len(GEO) != len(ref_date):
                raise ValueError("GEO series length must match other series")
            self.GEO = GEO.iloc[0] if len(GEO) > 0 else 'Canada'
        else:
            self.GEO = str(GEO)
        
        self.ref_date = ref_date
        self.trade = trade
        self.NAPCS = NAPCS
        self.value = pd.to_numeric(value)
        self.scalar_factor = scalar_factor
        self.net_total = float(net_total)
    
    def __str__(self):
        """Return string representation of the object"""
        return (f"Commodity(ref_date={self.ref_date.iloc[0]}, "
                f"trade={self.trade.iloc[0]}, "
                f"NAPCS={self.NAPCS.iloc[0]}, "
                f"value={self.value.iloc[0]}, "
                f"scalar_factor={self.scalar_factor.iloc[0]})")

    def __eq__(self, other):
        """Compare two Commodity objects for equality"""
        if not isinstance(other, Commodity):
            return False
        return (self.ref_date.equals(other.ref_date) and
                self.trade.equals(other.trade) and
                self.NAPCS.equals(other.NAPCS) and
                self.value.equals(other.value) and
                self.scalar_factor.equals(other.scalar_factor) and
                self.GEO == other.GEO and
                self.net_total == other.net_total)

    



