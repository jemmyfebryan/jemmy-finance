import numpy as np
from scipy.optimize import minimize
from typing import List

def kelly(returns, probabilities: List | bool):
    if isinstance(probabilities, bool):
        if probabilities == False: probabilities = [1/len(returns) for val in range(len(returns))]
    def fun(x):
        after = 1.0 + x * returns
        if np.any(after <= 0.0):
            return np.inf
        return -np.sum(probabilities * np.log(after))
    result = minimize(fun, 0.0)
    return result

def multiple_conditions_kelly(data):
    try:
        conditions = data.get("conditions")
        probabilities = [float(val['p']) for val in conditions]
        returns = [float(val['r']) for val in conditions]
        result = kelly(returns, probabilities).x[0]
        return np.round(result*100, 4)
    except Exception as e:
        return str(e)
    # try:
    #     outcomes = data.get("outcomes")

    #     probabilities = [float(val['p']) for val in outcomes]
    #     odds = [float(val['b']) for val in outcomes]

    #     probabilities = np.array(probabilities)
    #     odds = np.array(odds)

    #     # print(probabilities)
    #     # print(odds)# Constraint: sum of fractions must be <= 1 (not betting more than 100% of capital)
    #     constraints = ({'type': 'ineq', 'fun': lambda f: 1 - np.sum(f)})  # sum(f) <= 1

    #     # Bounds: Each bet fraction must be between 0 and 1
    #     bounds = [(0, 1) for _ in range(len(probabilities))]

    #     # Objective function: Negative expected log return (we minimize this)
    #     def kelly_objective(f):
    #         return -np.sum(probabilities * np.log(1 + f * (odds - 1)))

    #     # Initial guess (equal fractions)
    #     initial_guess = np.array([1/len(probabilities)] * len(probabilities))

    #     # Solve optimization
    #     result = minimize(kelly_objective, initial_guess, bounds=bounds, constraints=constraints)

    #     # Output
    #     optimal_fractions = result.x

    #     return np.round(optimal_fractions*100, 4)
    # except Exception as e:
    #     return str(e)