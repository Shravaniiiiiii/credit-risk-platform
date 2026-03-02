import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder

class CreditRiskFeatures(BaseEstimator, TransformerMixin):
    """Sklearn-compatible feature engineering pipeline"""

    def __init__(self):
        self.label_encoders = {}
        self.cat_cols = []

    def fit(self, X, y=None):
        df = X.copy()
        self.cat_cols = df.select_dtypes(include='object').columns.tolist()
        for col in self.cat_cols:
            le = LabelEncoder()
            le.fit(df[col].fillna('MISSING'))
            self.label_encoders[col] = le
        return self

    def transform(self, X):
        df = X.copy()

        # ── Ratio features ──────────────────────────────
        df['CREDIT_INCOME_RATIO']   = df['AMT_CREDIT'] / (df['AMT_INCOME_TOTAL'] + 1)
        df['ANNUITY_INCOME_RATIO']  = df['AMT_ANNUITY'] / (df['AMT_INCOME_TOTAL'] + 1)
        df['CREDIT_TERM']           = df['AMT_ANNUITY'] / (df['AMT_CREDIT'] + 1)
        df['GOODS_CREDIT_RATIO']    = df['AMT_GOODS_PRICE'] / (df['AMT_CREDIT'] + 1)

        # ── Age & Employment ─────────────────────────────
        df['AGE_YEARS']             = -df['DAYS_BIRTH'] / 365
        df['EMPLOYED_YEARS']        = (-df['DAYS_EMPLOYED']).clip(lower=0) / 365
        df['EMPLOYED_RATIO']        = df['EMPLOYED_YEARS'] / (df['AGE_YEARS'] + 1)
        df['IS_EMPLOYED']           = (df['DAYS_EMPLOYED'] < 0).astype(int)

        # ── Flag features ────────────────────────────────
        df['HAS_CAR']               = (df['FLAG_OWN_CAR'] == 'Y').astype(int)
        df['HAS_REALTY']            = (df['FLAG_OWN_REALTY'] == 'Y').astype(int)

        # ── Document count ───────────────────────────────
        doc_cols = [c for c in df.columns if 'FLAG_DOCUMENT' in c]
        df['DOCUMENT_COUNT']        = df[doc_cols].sum(axis=1)

        # ── Encode categoricals ──────────────────────────
        for col in self.cat_cols:
            if col in df.columns:
                df[col] = self.label_encoders[col].transform(
                    df[col].fillna('MISSING')
                )

        # ── Fill remaining NAs ───────────────────────────
        df = df.fillna(-999)
        return df
