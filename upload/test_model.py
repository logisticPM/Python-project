'''
   CS5001
   Final Project
   Fall 2024
   Tong Wu
'''
import pytest
import pandas as pd
from model import Model

class TestModel:
    """Test suite for Model class"""
    
    @pytest.fixture
    def model(self):
        """Create a Model instance for testing"""
        return Model()
        
    @pytest.fixture
    def sample_data(self):
        """
        Create sample data for testing
        
        Returns:
            tuple: (commodity_df, price_index_df) DataFrames
        """
        # Create commodity data
        commodity_df = pd.DataFrame({
            'REF_DATE': pd.date_range(start='2023-01-01', periods=3, freq='M'),
            'Net_Total': [48034.8, 46335.4, 53602.3],
            'GEO': ['Canada', 'Canada', 'Canada'],
            'Trade': ['Export', 'Export', 'Export'],
            'VALUE': [1000, 2000, 3000]
        })
        
        # Create price index data
        price_index_df = pd.DataFrame({
            'REF_DATE': pd.date_range(start='2023-01-01', periods=3, freq='M'),
            'Terms_of_Trade': [105.1, 103.9, 105.1]
        })
        
        return commodity_df, price_index_df

    def test_prepare_correlation_analysis_data(self, model, sample_data):
        """
        Test prepare_correlation_analysis_data method
        
        Parameters:
            model: Model instance
            sample_data: Tuple of test DataFrames
        """
        commodity_df, price_index_df = sample_data
        result = model.prepare_correlation_analysis_data(commodity_df, price_index_df)
        
        assert isinstance(result, pd.DataFrame)
        assert 'REF_DATE' in result.columns
        assert 'Net_Total' in result.columns
        assert 'Terms_of_Trade' in result.columns

    def test_prepare_correlation_analysis_data_invalid_input(self, model):
        """Test prepare_correlation_analysis_data with invalid input types"""
        with pytest.raises(ValueError, match="Invalid input data types"):
            model.prepare_correlation_analysis_data("invalid", "invalid")

    def test_prepare_correlation_analysis_data_empty(self, model):
        """Test prepare_correlation_analysis_data with empty DataFrames"""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="Input data is empty"):
            model.prepare_correlation_analysis_data(empty_df, empty_df)

    def test_calculate_regression(self, model):
        """Test regression calculation with perfect linear relationship"""
        x = [1.0, 2.0, 3.0]
        y = [2.0, 4.0, 6.0]
        
        slope, intercept = model.calculate_regression(x, y)
        
        assert isinstance(slope, float)
        assert isinstance(intercept, float)
        assert abs(slope - 2.0) < 0.0001
        assert abs(intercept) < 0.0001

    def test_calculate_regression_invalid_input(self, model):
        """Test regression calculation with invalid input types"""
        with pytest.raises(ValueError, match="Invalid input data types"):
            model.calculate_regression("invalid", [1, 2, 3])

    def test_calculate_regression_mismatched_lengths(self, model):
        """Test regression calculation with mismatched input lengths"""
        with pytest.raises(ValueError, match="Input lists must have the same length"):
            model.calculate_regression([1, 2, 3], [1, 2])

    def test_correlation_analysis(self, model, sample_data):
        """Test correlation analysis with valid input data"""
        commodity_df, price_index_df = sample_data
        result = model.correlation_analysis(commodity_df, price_index_df)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'correlation' in result
        assert 'sample_size' in result
        assert 'regression_equation' in result
        assert 'regression_coefficients' in result
        
        # Verify data types
        assert isinstance(result['correlation'], float)
        assert isinstance(result['sample_size'], int)
        assert isinstance(result['regression_equation'], str)
        assert isinstance(result['regression_coefficients'], dict)

    def test_correlation_analysis_invalid_input(self, model):
        """Test correlation analysis with invalid input types"""
        with pytest.raises(ValueError, match="Invalid input data types"):
            model.correlation_analysis("invalid", "invalid")

    def test_analyze_regional_trade_share(self, model):
        """Test regional trade share analysis with valid input"""
        df = pd.DataFrame({
            'REF_DATE': pd.date_range(start='2023-01-01', periods=4),
            'GEO': ['USA', 'China', 'USA', 'China'],
            'Trade': ['Export', 'Export', 'Import', 'Import'],
            'VALUE': [1000, 2000, 1500, 2500]
        })
        
        result = model.analyze_regional_trade_share(df)
        
        assert isinstance(result, dict)
        assert 'Export' in result
        assert 'Import' in result
        assert 'top_regions' in result['Export']
        assert 'trends' in result['Export']

    def test_analyze_regional_trade_share_empty(self, model):
        """Test regional trade share analysis with empty DataFrame"""
        with pytest.raises(ValueError, match="Input data is empty"):
            model.analyze_regional_trade_share(pd.DataFrame())

    def test_analyze_regional_trade_share_invalid_input(self, model):
        """Test regional trade share analysis with invalid input type"""
        with pytest.raises(ValueError, match="Invalid input data type"):
            model.analyze_regional_trade_share("invalid")
