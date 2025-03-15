def investment_kelly(data) -> float:
    try:
        p = float(data.get("ikc_p"))
        q = float(data.get("ikc_q"))
        g = float(data.get("ikc_g"))
        l = float(data.get("ikc_l"))
        result = p/l - q/g
        return round(100*result, 4)
    except Exception as e:
        return str(e)