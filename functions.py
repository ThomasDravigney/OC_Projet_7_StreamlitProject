def match_proba_result(x, results):
    for key, value in results.items():
        if value['range'][0] < x < value['range'][1]:
            return key
