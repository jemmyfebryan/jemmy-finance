from flask import request, jsonify

from utils.kelly_criterion import basic_kelly, investment_kelly, multiple_outcomes_kelly, multiple_conditions_kelly

def endpoint():
    data = request.json

    form_type = data.get("form_type")

    if form_type == "bkc":
        result = basic_kelly(data)
        result = f"Bankroll Fraction: {result}%"
    elif form_type == "ikc":
        result = investment_kelly(data)
        result = f"Bankroll Fraction: {result}%"
    elif form_type == "mokc":
        kelly_result = multiple_outcomes_kelly(data)
        outcomes = data.get("outcomes")
        result = "<br>"
        for i in range(len(kelly_result)):
            result = result + f"For Outcome-{i+1} (p={outcomes[i]['p']};b={outcomes[i]['b']}), Bet {kelly_result[i]}%<br>"
        # result = [f"{val}%" for val in result]
        result = f"Bankroll Fraction: {result}"
    elif form_type == "mckc":
        result = multiple_conditions_kelly(data)
        result = f"Bankroll Fraction: {result}%"
    else:
        result = "undefined"

    return jsonify({
        "result": result
    })