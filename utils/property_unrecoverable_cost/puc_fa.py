def fixed_assumptions(data):
    property_value = float(data["puc_fa_pv"])
    property_tax = float(data["puc_fa_pt"])
    property_maintenance_cost = float(data["puc_fa_mc"])
    property_cost_of_capital = float(data["puc_fa_coc"])
    property_rental_cost = float(data["puc_fa_rc"])

    puc = property_tax + property_maintenance_cost + property_cost_of_capital
    puc_value = puc*property_value/100
    puc_value_monthly = puc_value/12

    if puc_value_monthly < property_rental_cost:
        better = "greater"
        result = "rent"
    else:
        better = "less"
        result = "own"

    return puc, puc_value, property_rental_cost, better, result