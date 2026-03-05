from fastapi.testclient import TestClient
import sys; sys.path.insert(0, 'app')
from main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "customer_id": "TEST001",
    "amt_credit": 250000,
    "amt_income_total": 80000,
    "amt_annuity": 12000,
    "age_years": 35,
    "employment_years": 8,
    "credit_income_ratio": 3.1,
    "has_car": 1,
    "has_realty": 0
}

def test_health_endpoint():
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'healthy'

def test_score_valid_request():
    res = client.post('/v1/score', json=VALID_PAYLOAD)
    assert res.status_code == 200
    data = res.json()
    assert 'default_probability' in data
    assert 0 <= data['default_probability'] <= 1
    assert data['risk_band'] in ['LOW','MEDIUM','HIGH','VERY_HIGH']
    assert data['decision'] in ['APPROVE','MANUAL_REVIEW','DECLINE']

def test_invalid_age_rejected():
    payload = VALID_PAYLOAD.copy()
    payload['age_years'] = 10  # Too young
    res = client.post('/v1/score', json=payload)
    assert res.status_code == 422

def test_negative_credit_rejected():
    payload = VALID_PAYLOAD.copy()
    payload['amt_credit'] = -1000
    res = client.post('/v1/score', json=payload)
    assert res.status_code == 422

def test_metrics_endpoint():
    res = client.get('/metrics')
    assert res.status_code == 200
