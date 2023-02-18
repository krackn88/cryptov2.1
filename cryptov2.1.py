import requests
import pandas as pd
import numpy as np

# User input for cryptocurrency symbols
symbols = input("Enter cryptocurrency symbols separated by commas (e.g. BTC,ETH): ").upper().split(",")

# API endpoint
url = 'https://min-api.cryptocompare.com/data/v2/histoday'

# Empty list to store symbols with buy signals
buy_list = []

try:
    for symbol in symbols:
        print(f"Analyzing {symbol}...")

        # Set parameters for the API request
        parameters = {
            'fsym': symbol,
            'tsym': 'USD',
            'limit': 365
        }

        print("Making request to CryptoCompare API...")
        # Make GET request to the API
        response = requests.get(url, params=parameters)

        # Check if the response status code is OK
        if response.status_code == 200:
            print("API request successful. Parsing response data...")
            # Parse the JSON data
            data = response.json()
            if 'Data' in data:
                # Extract the historical prices and volumes
                prices = data['Data']['Data']
                prices_df = pd.DataFrame(prices)[['time', 'close', 'volumeto']]
                prices_df['time'] = pd.to_datetime(prices_df['time'], unit='s')
                prices_df = prices_df.set_index('time')

                print("Calculating technical indicators...")
                # Calculate the moving averages
                prices_df['SMA_14'] = prices_df['close'].rolling(window=14).mean()
                prices_df['SMA_30'] = prices_df['close'].rolling(window=30).mean()
                prices_df['SMA_50'] = prices_df['close'].rolling(window=50).mean()

                # Calculate the RSI indicator
                delta = prices_df['close'].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                avg_gain = gain.rolling(window=14).mean()
                avg_loss = loss.rolling(window=14).mean()
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                prices_df['RSI_14'] = rsi

                # Calculate the MACD indicator
                ema_12 = prices_df['close'].ewm(span=12, adjust=False).mean()
                ema_26 = prices_df['close'].ewm(span=26, adjust=False).mean()
                macd = ema_12 - ema_26
                signal = macd.rolling(window=9).mean()
                prices_df['MACD'] = macd
                prices_df['MACD_signal'] = signal

                # Calculate the Bollinger Bands
                prices_df['MA_20'] = prices_df['close'].rolling(window=20).mean()
                prices_df['SD_20'] = prices_df['close'].rolling(window=20).std()
                prices_df['UpperBand'] = prices_df['MA_20'] + (2 * prices_df['SD_20'])
                prices_df['LowerBand'] = prices_df['MA_20'] - (2 * prices_df['SD_20'])

                # Determine whether to buy or sell
                print("Analyzing data...")
                last_price = prices_df['close'].iloc[-1]
                last_rsi_14 = prices_df['RSI_14'].iloc[-1]
                last_sma_14 = prices_df['SMA_14'].iloc[-1]
                last_sma_30 = prices_df['SMA_30'].iloc[-1]
                last_sma_50 = prices_df['SMA_50'].iloc[-1]
                last_macd = prices_df['MACD'].iloc[-1]
                last_macd_signal = prices_df['MACD_signal'].iloc[-1]
                last_upperband = prices_df['UpperBand'].iloc[-1]
                last_lowerband = prices_df['LowerBand'].iloc[-1]

                if last_price < last_sma_14 and last_price < last_sma_30 and last_price < last_sma_50 and last_macd < last_macd_signal and last_price < last_lowerband:
                    buy_signal = "Buy"
                    buy_list.append(symbol)
                elif last_price < last_sma_14 and last_price < last_sma_30 and last_macd < last_macd_signal and last_price < last_lowerband:
                    buy_signal = "Buy"
                    buy_list.append(symbol)
                elif last_rsi_14 <= 30 and last_macd > last_macd_signal:
                    buy_signal = "Sell"
                elif last_rsi_14 >= 70 and last_macd < last_macd_signal:
                    buy_signal = "Sell"
                elif last_price > last_sma_14 and last_price > last_sma_30 and last_price > last_sma_50 and last_macd > last_macd_signal and last_price > last_upperband:
                    buy_signal = "Sell"
                elif last_price > last_sma_14 and last_price > last_sma_30 and last_macd > last_macd_signal and last_price > last_upperband:
                    buy_signal = "Sell"
                else:
                    buy_signal = "Hold"

                # Create a table of technical indicators and buy/sell signals
                table = pd.DataFrame({
                    'Price': [last_price],
                    'SMA_14': [last_sma_14],
                    'SMA_30': [last_sma_30],
                    'SMA_50': [last_sma_50],
                    'RSI_14': [last_rsi_14],
                    'MACD': [last_macd],
                    'MACD_signal': [last_macd_signal],
                    'UpperBand': [last_upperband],
                    'LowerBand': [last_lowerband],
                    'Signal': [buy_signal]
                })
                table.columns = ['Price', 'SMA_14', 'SMA_30', 'SMA_50', 'RSI_14', 'MACD', 'MACD_signal', 'UpperBand', 'LowerBand', 'Signal']
                table.index = [symbol]

                print(table)
                print("\n")

        print("Cryptocurrencies with buy signals:", buy_list)

except Exception as e:
    print(f'An error occurred: {e}')

