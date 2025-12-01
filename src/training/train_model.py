# src/training/train_model.py
"""Train the keylogger detection model with SMOTE"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE
import json
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
MODEL_DIR = BASE_DIR / "model"
DATA_FILE = BASE_DIR / "data" / "Keylogger_Detection.csv"

MODEL_FILE = MODEL_DIR / "keylogger_model.pkl"
FEATURES_FILE = MODEL_DIR / "features.pkl"
METRICS_FILE = MODEL_DIR / "training_metrics.json"

# Network-collectible features
FEATURES = [
    'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
    'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
    'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std',
    'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std',
    'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
    'Fwd IAT Mean', 'Fwd IAT Std', 'Bwd IAT Mean', 'Bwd IAT Std',
    'SYN Flag Count', 'ACK Flag Count', 'RST Flag Count', 'PSH Flag Count', 'URG Flag Count', 'FIN Flag Count',
    'Subflow Fwd Packets', 'Subflow Bwd Packets'
]

print("="*70)
print("  TRAINING KEYLOGGER DETECTION MODEL")
print("="*70)

# Load data
print(f"\nLoading dataset from: {DATA_FILE}")
df = pd.read_csv(DATA_FILE, low_memory=False)
df.columns = [c.strip() for c in df.columns]
print(f"✓ Loaded {len(df):,} samples")

# Get label
label_col = [c for c in df.columns if c.lower() in ['class', 'label']][0]
X = df[[f for f in FEATURES if f in df.columns]].copy()
y = df[label_col].astype(str).str.lower().map(lambda v: 1 if any(k in v for k in ['key','mal','1']) else 0)

# Preprocess
for col in X.columns:
    X[col] = pd.to_numeric(X[col], errors='coerce')
X = X.fillna(0.0)

print(f"\nClass distribution:")
print(f"  Benign:    {(y==0).sum():,} ({(y==0).sum()/len(y)*100:.1f}%)")
print(f"  Keylogger: {(y==1).sum():,} ({(y==1).sum()/len(y)*100:.1f}%)")

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# SMOTE
print("\nApplying SMOTE...")
smote = SMOTE(random_state=42)
X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
print(f"✓ Balanced to {len(X_train_sm):,} samples")

# Train
print("\nTraining Random Forest...")
rf = RandomForestClassifier(n_estimators=300, max_depth=20, class_weight='balanced', random_state=42, n_jobs=-1)
rf.fit(X_train_sm, y_train_sm)

# Evaluate
y_pred = rf.predict(X_test)
y_prob = rf.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)

print(f"\n{'='*70}")
print("  RESULTS")
print(f"{'='*70}")
print(f"Accuracy:  {acc:.4f}")
print(f"F1-Score:  {f1:.4f}")
print(f"ROC-AUC:   {auc:.4f}")
print(f"\n{classification_report(y_test, y_pred, target_names=['Benign','Keylogger'])}")

# Save
MODEL_DIR.mkdir(exist_ok=True)
joblib.dump({"model": rf}, MODEL_FILE)
joblib.dump(list(X.columns), FEATURES_FILE)

metrics = {
    'timestamp': datetime.now().isoformat(),
    'accuracy': float(acc),
    'f1_score': float(f1),
    'roc_auc': float(auc),
    'features': list(X.columns)
}
with open(METRICS_FILE, 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"\n✓ Model saved: {MODEL_FILE}")
print(f"✓ Ready for detection!")