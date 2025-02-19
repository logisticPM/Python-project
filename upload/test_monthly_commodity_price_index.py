'''
   CS5001
   Final Project
   Fall 2024
   Tong Wu
'''
import pytest
from monthly_commodity_price_index import MonthlyCommodityPriceIndex

class TestMonthlyCommodityPriceIndex:
    """Test suite for MonthlyCommodityPriceIndex class"""
    
    @pytest.fixture
    def sample_data(self):
        """
        Create sample data for testing
        
        Returns:
            tuple: (ref_date, trade, NAPCS, value, scalar_factor) as individual values
        """
        ref_date = "2023-01"
        trade = "Export"
        NAPCS = "Product A"
        value = 100.0
        scalar_factor = "units"
        
        return ref_date, trade, NAPCS, value, scalar_factor

    def test_init_valid_data(self, sample_data):
        """Test initialization with valid data"""
        ref_date, trade, NAPCS, value, scalar_factor = sample_data
        
        price_index = MonthlyCommodityPriceIndex(
            ref_date=ref_date,
            trade=trade,
            NAPCS=NAPCS,
            value=value,
            scalar_factor=scalar_factor
        )
        
        assert price_index.ref_date == ref_date
        assert price_index.trade == trade
        assert price_index.NAPCS == NAPCS
        assert price_index.value == value
        assert price_index.scalar_factor == scalar_factor

    def test_init_invalid_data_types(self, sample_data):
        """Test initialization with invalid data types"""
        ref_date, trade, NAPCS, value, scalar_factor = sample_data
        
        with pytest.raises(ValueError, match="Data type is invalid"):
            MonthlyCommodityPriceIndex(
                ref_date=123,  # Invalid type (should be str)
                trade=trade,
                NAPCS=NAPCS,
                value=value,
                scalar_factor=scalar_factor
            )

    def test_str_and_repr(self, sample_data):
        """Test string and representation methods"""
        ref_date, trade, NAPCS, value, scalar_factor = sample_data
        price_index = MonthlyCommodityPriceIndex(
            ref_date=ref_date,
            trade=trade,
            NAPCS=NAPCS,
            value=value,
            scalar_factor=scalar_factor
        )
        
        # Test __str__
        str_repr = price_index.__str__()
        assert isinstance(str_repr, str)
        assert "MonthlyCommodityPriceIndex" in str_repr
        
    def test_eq(self, sample_data):
        """Test equality comparison"""
        ref_date, trade, NAPCS, value, scalar_factor = sample_data
        
        price_index1 = MonthlyCommodityPriceIndex(
            ref_date=ref_date,
            trade=trade,
            NAPCS=NAPCS,
            value=value,
            scalar_factor=scalar_factor
        )
        
        price_index2 = MonthlyCommodityPriceIndex(
            ref_date=ref_date,
            trade=trade,
            NAPCS=NAPCS,
            value=value,
            scalar_factor=scalar_factor
        )
        
        # Test equality
        assert price_index1.__eq__(price_index2)
        
        # Test inequality with modified data
        price_index2.value = 200.0
        assert not price_index1.__eq__(price_index2)

    def test_init_invalid_value(self, sample_data):
        """Test initialization with invalid value"""
        ref_date, trade, NAPCS, _, scalar_factor = sample_data
        
        with pytest.raises(ValueError, match="Data type is invalid"):
            MonthlyCommodityPriceIndex(
                ref_date=ref_date,
                trade=trade,
                NAPCS=NAPCS,
                value="not_a_number",  # Invalid value type
                scalar_factor=scalar_factor
            )