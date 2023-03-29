import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
import json
from api_key import IEX_CLOUD_API_TOKEN

stocks = pd.read_csv("D:\\Sandbox\\algorithmic-trading-python-master\\starter_files\\stonks.csv", on_bad_lines='skip')
print(stocks.head())
print(stocks.columns.tolist())
api_url = f'https://api.iex.cloud/v1/data/core/quote/{symbol}?token={IEX_CLOUD_API_TOKEN}'
my_columns = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy']
final_dataframe = pd.DataFrame([[0, 0, 0, 0]], columns = my_columns)
final_dataframe = pd.DataFrame(columns = my_columns)
for stock in stocks['Ticker'][:3]:
    api_url = f'https://api.iex.cloud/v1/data/core/quote/{stock}?token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(api_url).json()
    final_dataframe = final_dataframe.append(
                                        pd.Series([stock, 
                                                   data[0]['latestPrice'], 
                                                   data[0]['marketCap'], 
                                                   'N/A'], 
                                                  index = my_columns), 
                                        ignore_index = True)
    
print(final_dataframe)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
#     print(symbol_strings)
    batch_api_call_url = f'https://api.iex.cloud/v1/data/core/quote/{symbol_string}?token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    print(data)
    for stock in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
                                        pd.Series([stock, 
                                                   data[0]['symbol']['quote']['latestPrice'], 
                                                   data[0]['symbol']['quote']['marketCap'], 
                                                   'N/A'], 
                                                  index = my_columns), 
                                        ignore_index = True)
        
print(final_dataframe)
        
portfolio_size = input("Enter the value of your portfolio:")

try:
    val = float(portfolio_size)
except ValueError:
    print("That's not a number! \n Try again:")
    portfolio_size = input("Enter the value of your portfolio:")

position_size = float(portfolio_size) / len(final_dataframe.index)
for i in range(0, len(final_dataframe['Ticker'])-1):
    final_dataframe.loc[i, 'Number Of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])
print(final_dataframe)

writer = pd.ExcelWriter('recommended_trades.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(writer, sheet_name='Recommended Trades', index = False)

background_color = '#0a0a23'
font_color = '#ffffff'

string_format = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

dollar_format = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

integer_format = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

column_formats = { 
                    'A': ['Ticker', string_format],
                    'B': ['Price', dollar_format],
                    'C': ['Market Capitalization', dollar_format],
                    'D': ['Number of Shares to Buy', integer_format]
                    }

for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)

writer.save()
