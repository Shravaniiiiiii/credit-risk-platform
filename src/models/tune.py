import optuna
import mlflow
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
optuna.logging.set_verbosity(optuna.logging.WARNING)

def objective(trial, X, y):
    params = {
        'n_estimators':       trial.suggest_int('n_estimators', 300, 1000),
        'learning_rate':      trial.suggest_float('lr', 0.01, 0.1, log=True),
        'max_depth':          trial.suggest_int('max_depth', 4, 10),
        'num_leaves':         trial.suggest_int('num_leaves', 20, 150),
        'min_child_samples':  trial.suggest_int('min_child_samples', 20, 200),
        'subsample':          trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree':   trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'reg_alpha':          trial.suggest_float('reg_alpha', 1e-8, 10, log=True),
        'class_weight': 'balanced', 'random_state': 42, 'verbose': -1
    }
    with mlflow.start_run(nested=True):
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = []
        for train_idx, val_idx in cv.split(X, y):
            model = LGBMClassifier(**params)
            model.fit(X.iloc[train_idx], y.iloc[train_idx])
            preds = model.predict_proba(X.iloc[val_idx])[:, 1]
            scores.append(roc_auc_score(y.iloc[val_idx], preds))
        mean_auc = np.mean(scores)
        mlflow.log_metric('cv_auc', mean_auc)
        return mean_auc

def run_tuning(X, y, n_trials=50):
    mlflow.set_experiment('credit-risk-optuna-tuning')
    with mlflow.start_run(run_name='optuna-study'):
        study = optuna.create_study(direction='maximize')
        study.optimize(lambda t: objective(t, X, y),
                       n_trials=n_trials, show_progress_bar=True)
        print(f'Best AUC: {study.best_value:.4f}')
        print(f'Best params: {study.best_params}')
        mlflow.log_params(study.best_params)
        mlflow.log_metric('best_auc', study.best_value)
        return study.best_params
