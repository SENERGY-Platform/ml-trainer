from darts.metrics import mae, coefficient_of_variation, mse, r2_score, mape

def calc_scores(pred, truth):
    scores = {
        'mae': mae(truth, pred),
        'coefficient_of_variation': coefficient_of_variation(truth, pred),
        'mse': mse(truth, pred),
        'r2_score': r2_score(truth, pred)
    }
    return scores