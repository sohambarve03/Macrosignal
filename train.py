# ══════════════════════════════════════════════════════════════
# ml_model/train.py
#
# 📖 WHAT THIS FILE DOES:
#   Trains an XGBoost model to predict ETF direction (UP/DOWN/NEUTRAL)
#   based on features from geopolitical events.
#
# 📖 WHAT IS XGBOOST?
#   XGBoost = Extreme Gradient Boosting. It builds many small
#   "decision trees" and combines them. Think of it like asking
#   100 different analysts to vote on a trade — the majority wins.
#   It's the most commonly used ML model in finance because:
#   - Handles small datasets well
#   - Doesn't need tons of preprocessing
#   - Very interpretable (feature importance)
#
# 📖 KEY CONCEPT — DIRECTIONAL ACCURACY
#   We don't predict exact prices. We predict DIRECTION.
#   If we predict XLE goes UP, and it actually goes UP — correct!
#   55-65% directional accuracy is genuinely good. Real quant
#   funds celebrate 55% because markets are very noisy.
# ══════════════════════════════════════════════════════════════

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("⚠️  XGBoost not installed. Run: pip install xgboost")

from data_pipeline.event_mapper import IMPACT_MATRIX, get_expected_impact, ETF_DESCRIPTIONS
from data_pipeline.news_fetcher import HISTORICAL_EVENTS
from config import DATA_PROCESSED


# ── FEATURE ENGINEERING ────────────────────────────────────────
# Features = the inputs to our ML model
# We convert event properties into numbers the model can use

def build_features_from_event(event_type, region, severity):
    """
    Convert an event into a feature vector (list of numbers).

    ML models need numbers — not strings. So we convert:
    - event_type → one-hot encoded (10 binary columns)
    - region     → one-hot encoded (5 binary columns)
    - severity   → raw number (1-4)
    - impact scores → 8 numbers from our impact matrix
    """
    features = {}

    # Severity as a raw number
    features["severity"] = severity

    # One-hot encode event type
    # "one-hot" means: 1 column per possible value, exactly one is 1, rest are 0
    all_event_types = list(IMPACT_MATRIX.keys())
    for et in all_event_types:
        features[f"event_{et}"] = 1 if event_type == et else 0

    # One-hot encode region
    all_regions = ["middle_east", "europe", "asia", "north_america", "global"]
    for r in all_regions:
        features[f"region_{r}"] = 1 if region == r else 0

    # Add the raw impact scores from our matrix as features
    impact_scores = get_expected_impact(event_type, region, severity)
    for etf, score in impact_scores.items():
        features[f"impact_{etf}"] = score

    return features


def build_training_dataset():
    """
    Build training data from our historical events.

    For each historical event, we:
    1. Extract features (event type, region, severity, impact scores)
    2. Use actual market outcomes as labels (did XLE go up or down?)

    Returns:
        pd.DataFrame: Features + labels for ML training
    """
    rows = []

    for event in HISTORICAL_EVENTS:
        features = build_features_from_event(
            event["event_type"],
            event["region"],
            event["severity"]
        )

        # Add labels: did each ETF we track go up (+1), down (-1)?
        # We look at the actual_xxx_change fields in our historical data
        for etf in ETF_DESCRIPTIONS.keys():
            change_key = f"actual_{etf.lower()}_change"
            if change_key in event:
                actual_change = event[change_key]
                # Convert to direction label
                if actual_change > 0.5:
                    direction = "UP"
                elif actual_change < -0.5:
                    direction = "DOWN"
                else:
                    direction = "NEUTRAL"

                row = features.copy()
                row["target_etf"]       = etf
                row["actual_change_pct"] = actual_change
                row["direction"]        = direction
                row["event_date"]       = event.get("date", "")
                rows.append(row)

    if not rows:
        print("⚠️  No training data found!")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    print(f"✅ Built training dataset: {len(df)} samples")
    return df


def train_direction_model(df):
    """
    Train XGBoost to predict direction (UP/DOWN/NEUTRAL).

    Args:
        df (pd.DataFrame): Training data from build_training_dataset()

    Returns:
        tuple: (trained model, label encoder, feature columns, accuracy)
    """
    if not XGB_AVAILABLE:
        print("⚠️  XGBoost not available. Install it: pip install xgboost")
        return None, None, None, 0

    # Separate features (X) from target (y)
    # Drop non-feature columns
    feature_cols = [c for c in df.columns if c not in
                    ["direction", "actual_change_pct", "event_date", "target_etf"]]
    X = df[feature_cols]
    y = df["direction"]

    # Encode string labels to numbers: UP=2, NEUTRAL=1, DOWN=0
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Split: 80% training, 20% testing
    # random_state=42 means results are reproducible (same split every time)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    print(f"\n📊 Training split: {len(X_train)} train, {len(X_test)} test samples")

    # Train XGBoost
    model = xgb.XGBClassifier(
        n_estimators     = 100,      # 100 decision trees
        max_depth        = 4,        # each tree max 4 levels deep
        learning_rate    = 0.1,      # how fast the model learns (lower = safer)
        random_state     = 42,
        eval_metric      = "mlogloss",
        use_label_encoder = False
    )

    model.fit(X_train, y_train)

    # Evaluate on test set
    y_pred   = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n🎯 Directional Accuracy: {accuracy:.1%}")
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    return model, le, feature_cols, accuracy


def get_feature_importance(model, feature_cols, top_n=10):
    """Show which features the model relies on most."""
    if model is None:
        return

    importance = pd.DataFrame({
        "feature":   feature_cols,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False).head(top_n)

    print(f"\n🔍 Top {top_n} Most Important Features:")
    for _, row in importance.iterrows():
        bar = "█" * int(row["importance"] * 50)
        print(f"  {row['feature']:<30} {row['importance']:.4f}  {bar}")

    return importance


def save_model(model, le, feature_cols):
    """Save trained model to disk."""
    model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "direction_model.pkl")
    meta_path  = os.path.join(model_dir, "model_meta.json")

    with open(model_path, "wb") as f:
        pickle.dump({"model": model, "label_encoder": le}, f)

    with open(meta_path, "w") as f:
        json.dump({"feature_cols": feature_cols}, f)

    print(f"\n💾 Model saved to {model_path}")


def predict_direction(model, le, feature_cols, event_type, region, severity):
    """
    Predict direction for a new event using the trained model.

    Returns:
        dict: {ETF: predicted_direction} for all ETFs
    """
    if model is None:
        return {}

    features = build_features_from_event(event_type, region, severity)
    X = pd.DataFrame([features])[feature_cols]

    pred_encoded  = model.predict(X)[0]
    pred_proba    = model.predict_proba(X)[0]
    direction     = le.inverse_transform([pred_encoded])[0]
    confidence    = max(pred_proba)

    return {
        "direction":  direction,
        "confidence": round(confidence, 3),
        "probabilities": dict(zip(le.classes_, [round(p, 3) for p in pred_proba]))
    }


# ── TEST / RUN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("🤖 GeoFinance ML Model Trainer\n")

    # Build dataset
    df = build_training_dataset()

    if df.empty:
        print("No data to train on. Add more historical events in news_fetcher.py")
    else:
        print(f"\n📊 Dataset preview:")
        print(df[["target_etf", "direction", "actual_change_pct", "severity"]].head(10))

        # Train model
        print("\n🏋️  Training XGBoost model...")
        model, le, feature_cols, accuracy = train_direction_model(df)

        if model:
            # Show feature importance
            get_feature_importance(model, feature_cols)

            # Save model
            save_model(model, le, feature_cols)

            # Test on new event
            print("\n\n🧪 Testing prediction on new event:")
            print("   Event: US-China trade war escalation, Asia, Severity 3")
            result = predict_direction(model, le, feature_cols, "trade_war", "asia", 3)
            print(f"   Predicted: {result['direction']} (confidence: {result['confidence']:.0%})")
            print(f"   Probabilities: {result['probabilities']}")

        print(f"\n✅ Training complete! Accuracy: {accuracy:.1%}")
        print("   Note: Small dataset = lower accuracy. Accuracy improves with more historical events.")
