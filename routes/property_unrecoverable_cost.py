from flask import request, jsonify

from utils.property_unrecoverable_cost import puc_fa

def endpoint():
    data = request.json

    form_type = data.get("form_type")

    if form_type == "puc-fa":
        puc, puc_value, rc, better, result = puc_fa(data)
        result = f"Annual Unrecoverable Cost: {puc}%<br>Annual Unrecoverable Cost Value: {puc_value}<br>The property annual unrecoverable cost is at {puc_value} per month and {better} than rental cost at {rc} per month. So {result} the property is the better option."
    else:
        result = "undefined"

    return jsonify({
        "result": result
    })