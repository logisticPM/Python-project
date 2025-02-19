'''
   CS5001
   Final Project
   Fall 2024
   Tong Wu
''' 

import pandas as pd
from data_process import data_process

class MonthlyCommodityPriceIndex:
    """
    A class to handle monthly commodity price index data processing and analysis.
    
    This class processes and analyzes monthly commodity price index data,
    including calculation of terms of trade.
    """

    def __init__(self, ref_date, trade, NAPCS, value, scalar_factor):
        """
        Initialize MonthlyCommodityPriceIndex class with cleaned data
        
        Parameters:
            ref_date (pd.Series): Reference date for the commodity data
            trade (pd.Series): Trade type for the commodity data
            NAPCS (pd.Series): North American Product Classification System (NAPCS) for the commodity data
            value (pd.Series): Value for the commodity data
            scalar_factor (pd.Series): Scalar factor for the commodity data
        """
        if (not isinstance(ref_date, str) or 
            not isinstance(trade, str) or 
            not isinstance(NAPCS, str) or 
            not isinstance(value, (int, float)) or 
            not isinstance(scalar_factor, str)):
            raise ValueError("Data type is invalid")
        
        self.ref_date = ref_date
        self.trade = trade
        self.NAPCS = NAPCS
        self.value = value
        self.scalar_factor = scalar_factor
    
    def __str__(self):
        """
        Returns a string representation of the MonthlyCommodityPriceIndex object.
        
        Returns:
            str: Formatted string containing all attributes of the object
        """
        return f"MonthlyCommodityPriceIndex(ref_date={self.ref_date}, trade={self.trade}, NAPCS={self.NAPCS}, value={self.value}, scalar_factor={self.scalar_factor})"
    
    def __eq__(self, other):
        """
        Compare if two MonthlyCommodityPriceIndex objects are equal.

        Parameters:
            other: Another MonthlyCommodityPriceIndex object to compare with

        Returns:
            bool: True if all attributes are equal, False otherwise
        """
        return (
            self.ref_date == other.ref_date and 
            self.trade == other.trade and 
            self.NAPCS == other.NAPCS and 
            self.value == other.value and 
            self.scalar_factor == other.scalar_factor
        )
