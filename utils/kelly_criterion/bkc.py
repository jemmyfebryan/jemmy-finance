def basic_kelly(data) -> float:
    try:
        p = float(data.get("bkc_p"))
        q = float(data.get("bkc_q"))
        b = float(data.get("bkc_b"))
        result = p - q/b
        return round(100*result, 4)
    except Exception as e:
        return str(e)