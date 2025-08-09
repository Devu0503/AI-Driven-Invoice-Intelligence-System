# src/ml_models.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "high_value_invoice.pkl")

NUMERIC_FEATS = ["Qty","Rate","Amount","CGST","SGST","Total"]

def add_target(df: pd.DataFrame, threshold: float = None):
    if threshold is None:
        threshold = df["Total"].quantile(0.75) if "Total" in df.columns else df["Amount"].quantile(0.75)
    df = df.copy()
    base = "Total" if "Total" in df.columns else "Amount"
    df["HighValueInvoice"] = (df[base] >= threshold).astype(int)
    return df, threshold

def train_model(df: pd.DataFrame):
    df = df.copy()
    df = df.dropna(subset=[c for c in NUMERIC_FEATS if c in df.columns])
    feats = [c for c in NUMERIC_FEATS if c in df.columns]
    df, threshold = add_target(df)

    X = df[feats]
    y = df["HighValueInvoice"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.25, random_state=42)

    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=200))
    ])
    pipe.fit(X_train, y_train)

    preds = pipe.predict(X_test)
    acc = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds, output_dict=False)

    joblib.dump({"model": pipe, "threshold": threshold, "features": feats}, MODEL_PATH)
    return acc, report, threshold

def predict(df: pd.DataFrame):
    bundle = joblib.load(MODEL_PATH)
    model, feats = bundle["model"], bundle["features"]
    X = df[feats].copy()
    return model.predict(X), model.predict_proba(X)[:,1]
