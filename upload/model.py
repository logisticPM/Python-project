'''
   CS5001
   Final Project
   Fall 2024
   Tong Wu
''' 

import pandas as pd
class Model:
    """
    Model class for data analysis
    
    This class handles all data analysis operations including:
    - Correlation analysis between trade data
    - Regional trade share analysis
    - Statistical computations
    """

    def __init__(self):
        pass

    def prepare_correlation_analysis_data(self, commodity_df, price_index_df):
        """
        Prepare data for correlation analysis
        
        Parameters:
            commodity_df (pandas.DataFrame): DataFrame from commodity pivot table
            price_index_df (pandas.DataFrame): DataFrame from monthly price index pivot table
            
        Returns:
            pandas.DataFrame: Merged and prepared data for analysis
        """
        if not isinstance(commodity_df, pd.DataFrame) or not isinstance(price_index_df, pd.DataFrame):
            raise ValueError("Invalid input data types")
        
        if commodity_df.empty or price_index_df.empty:
            raise ValueError("Input data is empty")
        

        commodity_data = commodity_df.reset_index()
        price_index_data = price_index_df.reset_index()
            
        merged_data = pd.merge(
            commodity_data,
            price_index_data[['REF_DATE', 'Terms_of_Trade']],
            on='REF_DATE',
            how='inner'
        )
            
        return merged_data
            

    def calculate_regression(self, x, y):
        """
        Calculate linear regression coefficients using basic math
        
        Parameters:
            x (list): Independent variable values
            y (list): Dependent variable values
            
        Returns:
            tuple: (slope, intercept) of regression line
        """
        if not isinstance(x, list) or not isinstance(y, list):
            raise ValueError("Invalid input data types")
        if len(x) != len(y):
            raise ValueError("Input lists must have the same length")
        
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        # Calculate slope
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0
        
        # Calculate intercept
        intercept = mean_y - slope * mean_x
        
        return slope, intercept

    def correlation_analysis(self, commodity_df, price_index_df):
        """
        Perform correlation analysis between commodity data and price index
        
        Parameters:
            commodity_df (pandas.DataFrame): Commodity data
            price_index_df (pandas.DataFrame): Price index data
            
        Returns:
            dict: Dictionary containing correlation analysis results and scatter plot data
        """
        if not isinstance(commodity_df, pd.DataFrame) or not isinstance(price_index_df, pd.DataFrame):
            raise ValueError("Invalid input data types")
        if commodity_df.empty or price_index_df.empty:
            raise ValueError("Input data is empty")
        
        analysis_data = self.prepare_correlation_analysis_data(commodity_df, price_index_df)
        
        # Calculate correlation coefficient
        correlation = float(analysis_data['Net_Total'].corr(analysis_data['Terms_of_Trade']))
            
        # Prepare monthly data for scatter plot
        scatter_data = pd.DataFrame({
            'Date': analysis_data['REF_DATE'],
            'Net_Total': analysis_data['Net_Total'].astype(float),
            'Terms_of_Trade': analysis_data['Terms_of_Trade'].astype(float)
        }).sort_values('Date')
            
        # Calculate regression line using our custom function
        x = scatter_data['Terms_of_Trade'].values.tolist()
        y = scatter_data['Net_Total'].values.tolist()
        slope, intercept = self.calculate_regression(x, y)
            
        # Calculate regression line points
        scatter_data['Regression_Line'] = [slope * x_val + intercept for x_val in x]
            
        # Add regression equation details
        regression_eq = f"y = {slope:,.2f}x {'+' if intercept >= 0 else '-'} {abs(intercept):,.2f}"
            
        return {
            'correlation': correlation,
            'sample_size': int(len(analysis_data)),
            'mean_net_total': float(analysis_data['Net_Total'].mean()),
            'std_net_total': float(analysis_data['Net_Total'].std()),
                'mean_terms_of_trade': float(analysis_data['Terms_of_Trade'].mean()),
                'std_terms_of_trade': float(analysis_data['Terms_of_Trade'].std()),
                'scatter_data': scatter_data,
                'regression_equation': regression_eq,
                'regression_coefficients': {
                    'slope': slope,
                'intercept': intercept
            }
        }
            

    def analyze_regional_trade_share(self, df):
        """
        Analyze regional trade share and trends
        
        Parameters:
            df (pandas.DataFrame): DataFrame containing regional trade data
        
        Returns:
            dict: Dictionary containing analysis results
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Invalid input data type")
        if df.empty:
            raise ValueError("Input data is empty")
        
        results = {'Export': {}, 'Import': {}}
            
            # Process Export data
        export_df = df[df['Trade'] == 'Export'].copy()
        if not export_df.empty:
            # Filter out Canada from GEO column
            export_df = export_df[export_df['GEO'] != 'Canada']
            
            # Calculate total export value
            total_export = export_df['VALUE'].sum()
            
            # Calculate regional shares
            export_shares = (export_df.groupby('GEO')['VALUE'].sum() / total_export * 100)
            export_shares = export_shares.sort_values(ascending=False)
            
            # Store top regions and their shares
            results['Export']['top_regions'] = [(region, share) 
                                              for region, share in export_shares.items()]
            
            # Create trends data
            export_trends = export_df.pivot_table(
                index='REF_DATE',
                columns='GEO',
                values='VALUE',
                aggfunc='sum'
            ).reset_index()
                
            # Melt the trends data for easier plotting
            export_trends_melted = export_trends.melt(
                id_vars=['REF_DATE'],
                var_name='Region',
                value_name='Value'
            )
                
            results['Export']['trends'] = export_trends_melted
            results['Export']['total_value'] = total_export
            
            # Process Import data
            import_df = df[df['Trade'] == 'Import'].copy()
            if not import_df.empty:
                # Filter out Canada from GEO column
                import_df = import_df[import_df['GEO'] != 'Canada']
                
                # Calculate total import value
                total_import = import_df['VALUE'].sum()
                
                # Calculate regional shares
                import_shares = (import_df.groupby('GEO')['VALUE'].sum() / total_import * 100)
                import_shares = import_shares.sort_values(ascending=False)
                
                # Store top regions and their shares
                results['Import']['top_regions'] = [(region, share) 
                                                  for region, share in import_shares.items()]
                
            # Create trends data
            import_trends = import_df.pivot_table(
                index='REF_DATE',
                columns='GEO',
                values='VALUE',
                aggfunc='sum'
            ).reset_index()
                
                # Melt the trends data for easier plotting
            import_trends_melted = import_trends.melt(
                id_vars=['REF_DATE'],
                var_name='Region',
                value_name='Value'
            )
                
            results['Import']['trends'] = import_trends_melted
            results['Import']['total_value'] = total_import
            
        return results
