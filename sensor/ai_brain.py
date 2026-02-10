import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Robust Path Handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "aegis_model.pkl")

def train_new_model():
    print(f"--- TRAINING AI MODEL ---")
    
    # 1. Synthetic Data Generation
    # Safe: Low Entropy, Low Speed
    safe_data = {
        'entropy': np.random.uniform(1.0, 4.5, 500),
        'rate': np.random.randint(0, 5, 500),
        'honeypot': [0] * 500,
        'label': 0 
    }
    # Malware: High Entropy + High Speed
    malware_data = {
        'entropy': np.random.uniform(7.0, 8.0, 500),
        'rate': np.random.randint(5, 100, 500),
        'honeypot': [0] * 500,
        'label': 1
    }
    # Trap: Honeypot Touched (Instant Guilt)
    trap_data = {
        'entropy': np.random.uniform(0.0, 8.0, 100),
        'rate': np.random.randint(0, 100, 100),
        'honeypot': [1] * 100,
        'label': 1
    }

    df = pd.concat([pd.DataFrame(safe_data), pd.DataFrame(malware_data), pd.DataFrame(trap_data)])

    # 2. Train
    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(df[['entropy', 'rate', 'honeypot']], df['label'])

    # 3. Save
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(clf, f)
    print(f"✅ Model Saved: {MODEL_PATH}")

def predict_threat(entropy, rate, honeypot):
    if not os.path.exists(MODEL_PATH):
        train_new_model()
    
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    
    # --- FIX START: We wrap the input in a DataFrame with names ---
    input_data = pd.DataFrame(
        [[entropy, rate, honeypot]], 
        columns=['entropy', 'rate', 'honeypot']
    )
    # --- FIX END ---

    confidence = model.predict_proba(input_data)[0][1]
    is_malware = confidence > 0.5
    return is_malware, confidence * 100

if __name__ == "__main__":
    train_new_model()