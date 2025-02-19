'''
   CS5001
   Final Project
   Fall 2024
   Tong Wu
'''
import pytest
import pandas as pd
from commodity import Commodity

class TestCommodity:
    """Test suite for Commodity class"""
    
    @pytest.fixture
    def sample_data(self):
        """
        Create sample data for testing
        
        Returns:
            tuple: (ref_date, trade, NAPCS, value, scalar_factor) as individual values
        """
        # Create test data as individual values instead of Series
        ref_date = "2023-01"
        trade = "Export"
        NAPCS = "Product A"
        value = 100.0
        scalar_factor = "millions"
        
        return ref_date, trade, NAPCS, value, scalar_factor

    def test_init_valid_data(self, sample_data):
        """Test initialization with valid data"""
        ref_date, trade, NAPCS, value, scalar_factor = sample_data
        
        commodity = Commodity(
            ref_date=ref_date,
            trade=trade,
            NAPCS=NAPCS,
            value=value,
            scalar_factor=scalar_factor
        )
        
        assert commodity.ref_date == ref_date
        assert commodity.trade == trade
        assert commodity.NAPCS == NAPCS
        assert commodity.value == value
        assert commodity.scalar_factor == scalar_factor

    def test_init_invalid_value_type(self, sample_data):
        """Test initialization with invalid value type"""
        ref_date, trade, NAPCS, _, scalar_factor = sample_data
        invalid_value = "not_a_number"
        
        with pytest.raises(ValueError, match="Data type is invalid"):
            Commodity(
                ref_date=ref_date,
                trade=trade,
                NAPCS=NAPCS,
                value=invalid_value,
                scalar_factor=scalar_factor
            )

    def test_init_with_custom_geo(self, sample_data):
        """Test initialization with custom GEO value"""
        ref_date, trade, NAPCS, value, scalar_factor = sample_data
        custom_geo = "USA"
        
        commodity = Commodity(
            ref_date=ref_date,
            trade=trade,
            NAPCS=NAPCS,
            value=value,
            scalar_factor=scalar_factor,
            GEO=custom_geo
        )
        
        assert commodity.GEO == custom_geo
