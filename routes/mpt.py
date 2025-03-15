import base64
import io
import random
from datetime import datetime, timedelta

from flask import request, jsonify
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utils.mpt.optimize import mpt_optimize
from utils.data import load_asset, load_yfinance_asset

def calculate_year_difference(df, date_column='Date'):
    df[date_column] = pd.to_datetime(df[date_column])  # Ensure the column is datetime
    min_date = df[date_column].min()
    max_date = df[date_column].max()
    return (max_date - min_date).days / 365.25  # Convert days to years

def endpoint(app):
    data = request.json

    chosen_assets = data.get("assets", [])

    currency = data.get("currency")
    if currency == "IDR-wUSD":
        currency = "IDR"
        chosen_assets += ["usd"]
    metric = data.get("metric")
    risk_free_rate = float(data.get("risk_free_rate"))
    data_range = data.get("data_range")

    # range_fraction = {
    #     "1m": 1/(5*12),
    #     "3m": 1/(5*4),
    #     "6m": 1/(5*2),
    #     "1y": 1/5,
    #     "3y": 3/5,
    #     "5y": 1
    # }[data_range]

    date_deltas = {
        "1m": timedelta(days=30),
        "3m": timedelta(days=90),
        "6m": timedelta(days=180),
        "1y": timedelta(days=365),
        "3y": timedelta(days=3*365),
        "5y": timedelta(days=5*365),
    }

    # print(chosen_assets)

    # Obtain Asset Prices Data
    assets = ["usd-idr", "btc-usd", "gold-usd", "spx-usd", "lq45-idr"]
    dataframes = {key: value for key, value in zip(assets, [load_asset(app, val) for val in assets])}

    custom_assets = [val for val in chosen_assets if val[:6] == "custom"]
    # chosen_assets = [val for val in chosen_assets if val[:6] != "custom"]
    for asset in custom_assets:
        # chosen_assets += [f"{asset}-usd", f"{asset}-idr"]
        dataframes[f"{asset}-usd"] = load_yfinance_asset(asset[7:])
        dataframes[f"{asset}-idr"] = dataframes[f"{asset}-usd"].copy()
        dataframes[f"{asset}-idr"]['Close'] *= (dataframes['usd-idr']['Close']/1000)

    # Initialize the merged DataFrame with the first DataFrame (renaming 'Close' column)
    df_assets = list(dataframes.values())[0][["Date", "Close"]].rename(columns={"Close": list(dataframes.keys())[0]})

    # Iteratively merge the rest using inner join
    for name, df in list(dataframes.items())[1:]:
        df_assets = df_assets.merge(df[["Date", "Close"]].rename(columns={"Close": name}), on="Date", how="inner")

    # Sort by date if necessary
    df_assets = df_assets.sort_values(by="Date").reset_index(drop=True)

    #lq45-usd
    df_assets['lq45-usd'] = df_assets['lq45-idr']/df_assets['usd-idr']
    #btc-idr
    df_assets['btc-idr'] = df_assets['btc-usd']*df_assets['usd-idr']/1000
    #gold-idr
    df_assets['gold-idr'] = df_assets['gold-usd']*df_assets['usd-idr']/1000
    #spx-idr
    df_assets['spx-idr'] = df_assets['spx-usd']*df_assets['usd-idr']/1000

    newest_date = df_assets['Date'].max()
    start_date = newest_date - date_deltas[data_range]
    df_assets = df_assets[(df_assets['Date'] >= start_date) & (df_assets['Date'] <= newest_date)]

    years_count = calculate_year_difference(df_assets)

    df_assets.drop(columns="Date", inplace=True)
    # df_assets = df_assets[-round(len(df_assets)*range_fraction):]

    # assets_raw = ["btc", "gold", "spx", "lq45"]

    if currency == "IDR":
        idr_assets = [f"{val}-idr" for val in chosen_assets]
        # print(idr_assets)
        mpt_returns = df_assets[idr_assets].pct_change().dropna()
    else:
        usd_assets = [f"{val}-usd" for val in chosen_assets]
        mpt_returns = df_assets[usd_assets].pct_change().dropna()
    # print(mpt_returns)
    # print("optimizing")
    mpt_result = mpt_optimize(mpt_returns.values, risk_free_rate=risk_free_rate)
    
    mpt_result_metrics = mpt_result[metric]
    mpt_result_returns = mpt_result["returns"]

    ## CAGR
    result_cagr = mpt_result_metrics["price"][-1] / mpt_result_metrics["price"][0]
    result_cagr = ((result_cagr)**(1/years_count)) - 1
    result_cagr = round(100*result_cagr, 4)

    ## MDD
    result_mdd = round(100*mpt_result_metrics["mdd"], 4)

    asset_prices = {k: np.cumprod(1 + v) for k, v in zip(chosen_assets, mpt_result_returns)}

    # print(mpt_result)

    if not chosen_assets:
        return jsonify({"error": "No assets selected"}), 400

    # Generate mock allocation percentages (should be replaced with real calculations)
    allocations = {asset: round(random.uniform(10, 50), 2) for asset in chosen_assets}
    total = sum(allocations.values())
    # allocations = {k: round(v / total * 100, 2) for k, v in allocations.items()}
    # print(allocations)
    allocations = {k: round(100*v, 2) for k, v in zip(chosen_assets, mpt_result_metrics["weights"]) if v != 0}
    # print(allocations)
    allocations_text = "<br>".join(f"{k}: {v}%" for k, v in allocations.items())

    # Generate a pie chart
    img = io.BytesIO()
    plt.figure(figsize=(5, 5))
    plt.pie(allocations.values(), labels=allocations.keys(), autopct='%1.1f%%')
    plt.title("Portfolio Allocation")
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Generate a price chart
    img_price = io.BytesIO()
    plt.plot(mpt_result_metrics["price"], label=metric, color="red")
    for k, v in asset_prices.items():
        plt.plot(v, label=k, linestyle=(0, (1, 1)))
    plt.title("Portfolio Chart")
    plt.xlabel("Days")
    plt.ylabel("Portfolio Growth")
    plt.legend()
    plt.savefig(img_price, format='png')
    plt.close()
    img_price.seek(0)
    img_price_base64 = base64.b64encode(img_price.getvalue()).decode('utf-8')

    return jsonify({
        "allocation": allocations,
        "allocation_text": allocations_text,
        "chart": f"data:image/png;base64,{img_base64}",
        "price_chart": f"data:image/png;base64,{img_price_base64}",
        "metric": metric,
        "metric_value": mpt_result_metrics['value'],
        "cagr": result_cagr,
        "mdd": result_mdd
    })
