import os

from flask import Flask, render_template, request
import pandas as pd
import yfinance as yf

from routes import kc, mpt

app = Flask(__name__)

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