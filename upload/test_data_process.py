'''
   CS5001
   Final Project
   Fall 2024
   Tong Wu
'''
import pytest
import pandas as pd
import numpy as np
from data_process import data_process
from unittest.mock import patch, MagicMock
import os
import requests

class TestDataProcess:
    """Test suite for data_process class"""
    
    @pytest.fixture
    def data_processor(self):
        """Create a data_process instance for testing"""
        return data_process()

    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing"""
        return pd.DataFrame({
            'REF_DATE': ['2023-01-01', '2023-02-01'],
            'Trade': ['Export', 'Import'],
            'VALUE': [100, 200],
            'GEO': ['Ontario', 'Quebec'],
            'North American Product Classification System (NAPCS)': ['Product A', 'Product B'],
            'UOM': ['units', 'units'],
            'SCALAR_FACTOR': ['units', 'units']
        })

    def test_data_extraction(self, data_processor):
        """Test data extraction from URL"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b'test,data\n1,2'
            mock_get.return_value = mock_response
            
            result = data_processor.data_extraction('http://test.url')
            assert result == b'test,data\n1,2'
            mock_get.assert_called_once_with('http://test.url', timeout=10)

    def test_data_extraction_empty_url(self, data_processor):
        """Test data extraction with empty URL"""
        with pytest.raises(ValueError, match="URL cannot be empty"):
            data_processor.data_extraction('')

    def test_data_extraction_connection_error(self, data_processor):
        """Test data extraction with connection error"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            with pytest.raises(requests.exceptions.ConnectionError, match="Failed to connect to URL"):
                data_processor.data_extraction('http://test.url')

    def test_data_extraction_http_error(self, data_processor):
        """Test data extraction with HTTP error"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
            mock_get.return_value = mock_response
            
            with pytest.raises(requests.exceptions.HTTPError, match="HTTP error occurred"):
                data_processor.data_extraction('http://test.url')

    def test_data_extraction_timeout(self, data_processor):
        """Test data extraction with timeout"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
            with pytest.raises(requests.exceptions.Timeout, match="Request timed out after 10 seconds"):
                data_processor.data_extraction('http://test.url')

    def test_data_extraction_general_error(self, data_processor):
        """Test data extraction with general request exception"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("General error")
            with pytest.raises(requests.exceptions.RequestException, match="An error occurred while fetching the URL"):
                data_processor.data_extraction('http://test.url')

    def test_clean_commodity_data(self, data_processor, sample_df):
        """Test commodity data cleaning"""
        result = data_processor.clean_commodity_data(sample_df)
        assert isinstance(result, pd.DataFrame)
        assert 'VALUE' in result.columns
        assert result['VALUE'].dtype in [np.float64, np.int64]

    def test_clean_commodity_data_empty(self, data_processor):
        """Test commodity data cleaning with empty DataFrame"""
        with pytest.raises(ValueError, match="Input DataFrame cannot be empty"):
            data_processor.clean_commodity_data(pd.DataFrame())

    def test_clean_price_index_data(self, data_processor, sample_df):
        """Test price index data cleaning"""
        result = data_processor.clean_price_index_data(sample_df)
        assert isinstance(result, pd.DataFrame)
        assert 'VALUE' in result.columns
        assert result['VALUE'].dtype in [np.float64, np.int64]

    def test_clean_regional_data(self, data_processor, sample_df):
        """Test regional data cleaning"""
        df = sample_df.copy()
        df['Trade'] = ['Domestic export', 'Import']
        result = data_processor.clean_regional_data(df)
        
        assert isinstance(result, pd.DataFrame)
        assert 'Export' in result['Trade'].values
        assert 'Domestic export' not in result['Trade'].values

    def test_data_processing_into_dataframe(self, data_processor):
        """Test conversion of raw data to DataFrame"""
        test_data = b'col1,col2\n1,2\n3,4'
        result = data_processor.data_processing_into_dataframe(test_data)
        
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ['col1', 'col2']
        assert len(result) == 2

    def test_dataframe_column_drop(self, data_processor, sample_df):
        """Test column dropping functionality"""
        columns_to_drop = ['Trade']
        result = data_processor.dataframe_column_drop(sample_df, columns_to_drop)
        
        assert 'Trade' not in result.columns
        assert len(result.columns) == len(sample_df.columns) - 1

    def test_dataframe_value_replace(self, data_processor, sample_df):
        """Test value replacement in DataFrame"""
        result = data_processor.dataframe_value_replace(
            sample_df,
            'Trade',
            ['Export'],
            'Exported'
        )
        
        assert 'Exported' in result['Trade'].values
        assert 'Export' not in result['Trade'].values

    def test_column_combination(self, data_processor, sample_df):
        """Test column combination functionality"""
        group_keys = ['REF_DATE', 'Trade']
        result = data_processor.column_combination(sample_df, group_keys)
        
        assert isinstance(result, pd.DataFrame)
        assert all(key in result.columns for key in group_keys)
        assert 'VALUE' in result.columns

    def test_save_and_read_csv(self, data_processor, tmp_path):
        """Test saving and reading CSV files"""
        test_data = b'col1,col2\n1,2'
        filepath = os.path.join(tmp_path, 'test.csv')
        
        # Test save
        data_processor.save_to_csv(test_data, filepath)
        assert os.path.exists(filepath)
        
        # Test read
        result = data_processor.read_from_csv(filepath)
        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    def test_pivot_table_for_terms_of_trade(self, data_processor, sample_df):
        """Test creation of pivot table for terms of trade"""
        result = data_processor.pivot_table_for_terms_of_trade(sample_df)
        
        assert isinstance(result, pd.DataFrame)
        assert 'Net_Total' in result.columns
        assert 'Export' in result.columns
        assert 'Import' in result.columns

    def test_calculate_terms_of_trade(self, data_processor, sample_df):
        """Test terms of trade calculation"""
        result = data_processor.calculate_terms_of_trade(sample_df)
        
        assert isinstance(result, pd.DataFrame)
        assert data_processor.TERMS_OF_TRADE_COLUMN in result.columns
        assert not result.empty

    def test_read_csv_empty_filepath(self, data_processor):
        """Test reading CSV with empty filepath"""
        with pytest.raises(ValueError, match="Filepath cannot be empty"):
            data_processor.read_from_csv('')

    def test_read_csv_nonexistent_file(self, data_processor):
        """Test reading non-existent CSV file"""
        with pytest.raises(FileNotFoundError):
            data_processor.read_from_csv('nonexistent.csv')

    def test_save_csv_empty_filepath(self, data_processor):
        """Test saving CSV with empty filepath"""
        with pytest.raises(ValueError, match="Filepath cannot be empty"):
            data_processor.save_to_csv(b'test', '')