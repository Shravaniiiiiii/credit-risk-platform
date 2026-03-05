from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
import mlflow.pyfunc
import pandas as pd
import json, hashlib, os, logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='Credit Risk Scoring API',
    description='Real-time credit default probability scoring',
    version='2.0.0'
)

# Prometheus metrics
REQUESTS = Counter('api_requests_total', 'API requests', ['endpoint', 'status'])
LATENCY  = Histogram('api_latency_seconds', 'Request latency')
HIGH_RISK = Counter('high_risk_decisions_total', 'High risk decisions')

# Load model from MLflow (will fail gracefully if not found)
try:
    MODEL_URI = os.getenv('MODEL_URI', 'models:/credit-risk-lgbm/1')
    MLFLOW_URI = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
    mlflow.set_tracking_uri(MLFLOW_URI)
    model = mlflow.sklearn.load_model(MODEL_URI)
    logger.info(f'Model loaded: {MODEL_URI}')
except Exception as e:
    logger.warning(f'Model not loaded: {e}. Using mock predictions.')
    model = None

class CreditApplication(BaseModel):
    customer_id:         str
    amt_credit:          float
    amt_income_total:    float
    amt_annuity:         Optional[float] = 0.0
    age_years:           float
    employment_years:    float
    credit_income_ratio: float
    has_car:             int
    has_realty:          int

    @validator('age_years')
    def check_age(cls, v):
        if not (18 <= v <= 100): raise ValueError('Age must be 18-100')
        return v

    @validator('amt_credit','amt_income_total')
    def check_positive(cls, v):
        if v <= 0: raise ValueError('Must be positive')
        return v

@app.post('/v1/score')
def score(application: CreditApplication):
    with LATENCY.time():
        features = pd.DataFrame([{
            k: v for k, v in application.dict().items()
            if k != 'customer_id'
        }])

        if model:
            prob = float(model.predict_proba(features)[0][1])
        else:
            prob = 0.1  # Mock for testing

        if prob < 0.05:   risk, decision = 'LOW',      'APPROVE'
        elif prob < 0.15: risk, decision = 'MEDIUM',   'APPROVE'
        elif prob < 0.30: risk, decision = 'HIGH',     'MANUAL_REVIEW'
        else:             risk, decision = 'VERY_HIGH','DECLINE'

        if risk in ('HIGH','VERY_HIGH'): HIGH_RISK.inc()
        REQUESTS.labels(endpoint='/v1/score', status='200').inc()

        return {
            'customer_id':          application.customer_id,
            'default_probability':  round(prob, 4),
            'risk_band':            risk,
            'decision':             decision,
            'model_version':        'lgbm-v2.0.0'
        }

@app.get('/health')
def health(): return {'status':'healthy','version':'2.0.0'}

@app.get('/metrics')
def metrics(): return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get('/')
def root(): return {'message':'Credit Risk API', 'docs':'/docs'}
