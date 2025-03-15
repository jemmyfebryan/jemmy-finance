from typing import Callable
import pandas as pd
import numpy as np
import scipy.optimize as sco

def downside_risk(returns):
    downside = returns[returns < 0]
    return np.std(downside) * np.sqrt(252)  # Annualized downside deviation

def max_drawdown(returns):
    cumulative_returns = np.cumprod(1 + returns)
    peak = np.maximum.accumulate(cumulative_returns)
    drawdown = (peak - cumulative_returns)/peak
    return np.max(drawdown)

def risk_contribution(weights, cov_matrix):
    """
    Compute the risk contribution of each asset in the portfolio.
    """
    portfolio_risk = np.sqrt(weights.T @ cov_matrix @ weights)  # Total portfolio volatility
    marginal_risk = cov_matrix @ weights  # Marginal risk contribution
    risk_contributions = weights * marginal_risk  # Individual asset risk contributions
    return risk_contributions / portfolio_risk  # Normalize to get the fraction of risk

def omega_ratio(returns, risk_free_rate, threshold=0):
    excess_returns = returns - risk_free_rate / 252
    gain = np.sum(excess_returns[excess_returns > threshold])
    loss = -np.sum(excess_returns[excess_returns < threshold])
    return gain / loss if loss > 0 else np.inf

# Define the negative Sharpe Ratio function
def neg_sharpe(weights, mean_returns, cov_matrix, risk_free_rate):
    portfolio_return = np.dot(weights, mean_returns)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return - (portfolio_return - risk_free_rate) / portfolio_volatility  # Negative Sharpe Ratio

# Define the negative Sortino Ratio function
def neg_sortino(weights, mean_returns, returns, risk_free_rate):
    portfolio_return = np.dot(weights, mean_returns)
    portfolio_returns = np.dot(weights, returns)
    downside_volatility = downside_risk(portfolio_returns)
    return - (portfolio_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else np.inf

# Define the negative Calmar Ratio function
def neg_calmar(weights, mean_returns, returns, risk_free_rate):
    portfolio_return = np.dot(weights, mean_returns)
    portfolio_returns = np.dot(weights, returns)
    # period = 63
    # portfolio_returns = compound_returns(np.dot(weights, returns), period=period)
    drawdown = max_drawdown(portfolio_returns)
    return - (portfolio_return - risk_free_rate) / drawdown if drawdown > 0 else np.inf

def neg_mdd(weights, returns, risk_free_rate):
    portfolio_returns = np.dot(weights, returns)
    drawdown = max_drawdown(portfolio_returns)
    return drawdown

# Define the negative Omega Ratio function
def neg_omega(weights, mean_returns, returns, risk_free_rate):
    portfolio_returns = np.dot(weights, returns)
    return -omega_ratio(portfolio_returns, risk_free_rate)

def risk_parity_objective(weights, cov_matrix):
    """
    Objective function to minimize the squared deviation from equal risk contribution.
    """
    num_assets = len(weights)
    risk_contributions = risk_contribution(weights, cov_matrix)
    return np.sum((risk_contributions - 1/num_assets) ** 2)  # Squared deviation from equal risk

def kelly_objective(weights, mean_returns, cov_matrix):
    portfolio_return = np.dot(weights, mean_returns)
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    return - (portfolio_return - 0.5 * portfolio_variance)  # Negative Kelly Criterion

def mpt_optimize(returns: np.ndarray, risk_free_rate: float):
    returns = returns.T

    mean_returns = np.mean(returns, axis=1) * 252

    # Constraints: sum of weights = 1
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})

    # Bounds: each asset weight between 0% and 100%
    bounds = tuple((0, 1) for _ in range(returns.shape[0]))

    # Initial guess (equal allocation)
    initial_weights = np.ones(returns.shape[0])/returns.shape[0]

    # Covariance matrix for Sharpe Ratio
    cov_matrix = np.cov(returns) * 252  # Annualized covariance

    # Optimize for each ratio
    opt_sharpe = sco.minimize(neg_sharpe, initial_weights, args=(mean_returns, cov_matrix, risk_free_rate),
                            method='SLSQP', bounds=bounds, constraints=constraints)
    # print("sharpe finished")
    opt_sortino = sco.minimize(neg_sortino, initial_weights, args=(mean_returns, returns, risk_free_rate),
                            method='SLSQP', bounds=bounds, constraints=constraints)
    # print("sortino finished)")
    opt_calmar = sco.minimize(neg_calmar, initial_weights, args=(mean_returns, returns, risk_free_rate),
                            method='SLSQP', bounds=bounds, constraints=constraints)
    # print("calmar finished")
    opt_mdd = sco.minimize(neg_mdd, initial_weights, args=(returns, risk_free_rate),
                            method='SLSQP', bounds=bounds, constraints=constraints)
    # print("mdd finished")
    opt_omega = sco.minimize(neg_omega, initial_weights, args=(mean_returns, returns, risk_free_rate),
                            method='SLSQP', bounds=bounds, constraints=constraints)
    opt_kelly = sco.minimize(kelly_objective, initial_weights, args=(mean_returns, cov_matrix),
                             method='SLSQP', bounds=bounds, constraints=constraints)
    # opt_risk_parity = sco.minimize(risk_parity_objective, initial_weights, args=(cov_matrix,),
    #                            method='SLSQP', bounds=bounds, constraints=constraints)
    # print("omega finished")
    
    # Extract optimal weights
    optimal_weights_sharpe = np.round(opt_sharpe.x, 4)
    optimal_weights_sortino = np.round(opt_sortino.x, 4)
    optimal_weights_calmar = np.round(opt_calmar.x, 4)
    optimal_weights_mdd = np.round(opt_mdd.x, 4)
    optimal_weights_omega = np.round(opt_omega.x, 4)
    optimal_weights_kelly = np.round(opt_kelly.x, 4)
    # optimal_weights_risk_parity = np.round(opt_risk_parity.x, 4)
    optimal_weights_risk_parity_std = 1/np.std(returns, ddof=1, axis=1)
    optimal_weights_risk_parity = optimal_weights_risk_parity_std/sum(optimal_weights_risk_parity_std)

    # Extract MDDs
    MDD_sharpe = neg_mdd(optimal_weights_sharpe, returns, risk_free_rate)
    MDD_sortino = neg_mdd(optimal_weights_sortino, returns, risk_free_rate)
    MDD_calmar = neg_mdd(optimal_weights_calmar, returns, risk_free_rate)
    MDD_mdd = neg_mdd(optimal_weights_mdd, returns, risk_free_rate)
    MDD_omega = neg_mdd(optimal_weights_omega, returns, risk_free_rate)
    MDD_kelly = neg_mdd(optimal_weights_kelly, returns, risk_free_rate)
    MDD_risk_parity = neg_mdd(optimal_weights_risk_parity, returns, risk_free_rate)

    # Extract optimal ratios
    optimal_sharpe = -opt_sharpe.fun
    optimal_sortino = -opt_sortino.fun
    optimal_calmar = -opt_calmar.fun
    optimal_mdd = opt_mdd.fun
    optimal_omega = -opt_omega.fun
    optimal_kelly = -opt_kelly.fun
    # optimal_risk_parity = opt_risk_parity.fun
    optimal_risk_parity = np.mean(1/optimal_weights_risk_parity_std)

    # Price Chart
    returns_MPT_sharpe = np.dot(optimal_weights_sharpe, returns)
    returns_MPT_sortino = np.dot(optimal_weights_sortino, returns)
    returns_MPT_calmar = np.dot(optimal_weights_calmar, returns)
    returns_MPT_mdd = np.dot(optimal_weights_mdd, returns)
    returns_MPT_omega = np.dot(optimal_weights_omega, returns)
    returns_MPT_kelly = np.dot(optimal_weights_kelly, returns)
    returns_MPT_risk_parity = np.dot(optimal_weights_risk_parity, returns)
    asset_MPT_sharpe = np.cumprod(1 + returns_MPT_sharpe)
    asset_MPT_sortino = np.cumprod(1 + returns_MPT_sortino)
    asset_MPT_calmar = np.cumprod(1 + returns_MPT_calmar)
    asset_MPT_mdd = np.cumprod(1 + returns_MPT_mdd)
    asset_MPT_omega = np.cumprod(1 + returns_MPT_omega)
    asset_MPT_kelly = np.cumprod(1 + returns_MPT_kelly)
    asset_MPT_risk_parity = np.cumprod(1 + returns_MPT_risk_parity)

    optimal_ratios = {
        "sharpe": {"value": round(optimal_sharpe, 4), "weights": optimal_weights_sharpe, "price": asset_MPT_sharpe, "returns": returns_MPT_sharpe, "mdd": MDD_sharpe},
        "sortino": {"value": round(optimal_sortino, 4), "weights": optimal_weights_sortino, "price": asset_MPT_sortino, "returns": returns_MPT_sortino, "mdd": MDD_sortino},
        "calmar": {"value": round(optimal_calmar, 4), "weights": optimal_weights_calmar, "price": asset_MPT_calmar, "returns": returns_MPT_calmar, "mdd": MDD_calmar},
        "mdd": {"value": round(optimal_mdd, 4), "weights": optimal_weights_mdd, "price": asset_MPT_mdd, "returns": returns_MPT_mdd, "mdd": MDD_mdd},
        "omega": {"value": round(optimal_omega, 4), "weights": optimal_weights_omega, "price": asset_MPT_omega, "returns": returns_MPT_omega, "mdd": MDD_omega},
        "kelly": {"value": round(optimal_kelly, 4), "weights": optimal_weights_kelly, "price": asset_MPT_kelly, "returns": returns_MPT_kelly, "mdd": MDD_kelly},
        "risk_parity": {"value": round(optimal_risk_parity, 4), "weights": optimal_weights_risk_parity, "price": asset_MPT_risk_parity, "returns": returns_MPT_risk_parity, "mdd": MDD_mdd},
        "returns": returns,
    }

    return optimal_ratios