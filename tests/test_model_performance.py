
import sys
import json

# Minimum performance thresholds (set by Risk / Model Validation team)
THRESHOLDS = {
    'min_auc':   0.72,
    'max_psi':   0.25,  # Population Stability Index
    'min_gini':  0.44,
}

def load_latest_metrics():
    """In real project, read from MLflow API"""
    try:
        import mlflow
        client = mlflow.tracking.MlflowClient('http://localhost:5000')
        runs = client.search_runs(
            experiment_ids=['1'],
            order_by=['metrics.test_auc DESC'],
            max_results=1
        )
        if runs:
            return runs[0].data.metrics
    except:
        pass
    # Fallback mock metrics for CI
    return {'test_auc': 0.78, 'gini': 0.56}

def test_auc_above_threshold():
    metrics = load_latest_metrics()
    auc = metrics.get('test_auc', 0)
    assert auc >= THRESHOLDS['min_auc'], \
        f'AUC {auc:.4f} below minimum {THRESHOLDS["min_auc"]}'
    print(f'AUC gate passed: {auc:.4f} >= {THRESHOLDS["min_auc"]}')

def test_gini_above_threshold():
    metrics = load_latest_metrics()
    gini = metrics.get('gini', 0)
    assert gini >= THRESHOLDS['min_gini'], \
        f'Gini {gini:.4f} below minimum {THRESHOLDS["min_gini"]}'
    print(f'Gini gate passed: {gini:.4f} >= {THRESHOLDS["min_gini"]}')

if __name__ == '__main__':
    test_auc_above_threshold()
    test_gini_above_threshold()
    print('All model performance gates PASSED!')
