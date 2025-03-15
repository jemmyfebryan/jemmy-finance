import os

import pandas as pd
import yfinance as yf
import pickle

cache = {}

def load_asset(app, code: str) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(app.root_path, "static", "asset_prices", f"{code}.csv"))
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
    return df

def load_yfinance_asset(code: str) -> pd.DataFrame:
    if code in cache:
        return pickle.loads(cache[code])  # Load from cache
    
    df = yf.download(code, interval='1d')
    df.columns = df.columns.get_level_values(0)
    df = df[1:]
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
    
    cache[code] = pickle.dumps(df)  # Save to cache
    return df