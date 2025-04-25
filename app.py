import os

from flask import Flask, render_template, request, jsonify
import pandas as pd
import yfinance as yf

import random
import requests

from routes import kc, mpt, puc

app = Flask(__name__)

def calculate_rsi(close, period=7):
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

@app.route('/')
def index():
    return render_template('index.html')

# Investment & Portfolio Management
@app.route('/ipm/asset_allocation_optimizer', methods=["GET", "POST"])
def asset_allocation_optimizer():
    if request.method == "GET":
        return render_template('/ipm/asset_allocation_optimizer.html')
    elif request.method == "POST":
        return mpt(app=app)
    
@app.route('/ipm/kelly_criterion', methods=["GET", "POST"])
def kelly_criterion():
    if request.method == "GET":
        return render_template('/ipm/kelly_criterion.html')
    elif request.method == "POST":
        return kc()
    
@app.route('/pf/property_unrecoverable_cost', methods=["GET", "POST"])
def property_unrecoverable_cost():
    if request.method == "GET":
        return render_template('/pf/property_unrecoverable_cost.html')
    elif request.method == "POST":
        return puc()
    
@app.route('/get_fear_and_greed')
def get_fear_and_greed():
    # # Generate random values for each market indicator
    # fear_and_greed = random.randint(0, 100)
    # volatility = random.randint(0, 100)
    # sentiment = random.randint(0, 100)

    # Fear and Greed
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        fear_and_greed = int(data["data"][0]["value"])
    else:
        # raise Exception(f"Failed to fetch data: {response.status_code}")
        fear_and_greed = "-"

    # Market Volatility
    vix = yf.download('^VIX', period='14d', interval='1d')
    vix.columns = vix.columns.get_level_values(0)
    vix = vix[1:]
    vix.reset_index(inplace=True)
    vix['Date'] = pd.to_datetime(vix['Date'], format="%d/%m/%Y")
    vix['RSI_7'] = calculate_rsi(vix['Close'], period=7)
    volatility = round(vix['RSI_7'].tolist()[-1])

    # Consumer confidence
    conf = yf.download('XLY', period='14d', interval='1d')
    conf.columns = conf.columns.get_level_values(0)
    conf = conf[1:]
    conf.reset_index(inplace=True)
    conf['Date'] = pd.to_datetime(conf['Date'], format="%d/%m/%Y")
    conf['RSI_7'] = calculate_rsi(conf['Close'], period=7)
    consumer = round(conf['RSI_7'].tolist()[-1])
    
    # Return the values as a JSON response
    return jsonify({
        'fearAndGreed': fear_and_greed,
        'volatility': volatility,
        'consumer': consumer
    })

# @app.route('/corporate-finance/financial-statements-analysis')
# def financial_statements_analysis():
#     # Example Python-based application (simple financial ratio calculator)
#     data = {
#         "Revenue": 500000,
#         "Net Income": 80000,
#         "Total Assets": 1200000,
#         "Total Liabilities": 500000
#     }
    
#     data["Return on Assets (ROA)"] = round((data["Net Income"] / data["Total Assets"]) * 100, 2)
#     data["Debt to Equity Ratio"] = round((data["Total Liabilities"] / (data["Total Assets"] - data["Total Liabilities"])), 2)
    
#     return render_template('financial-statements-analysis.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)