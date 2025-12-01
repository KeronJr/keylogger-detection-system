# src/collectors/feature_extractor.py
"""Extract features from flow for model inference"""
import joblib
import pandas as pd
from pathlib import Path

def load_feature_names():
    """Load expected feature names from training"""
    features_file = Path(__file__).parent.parent.parent / "model" / "features.pkl"
    return joblib.load(features_file)

def flow_to_features(flow_dict):
    """Convert flow dict to feature DataFrame"""
    feature_names = load_feature_names()
    
    # Map flow dict keys to feature names
    mapping = {
        'Flow Duration': 'flow_duration',
        'Total Fwd Packets': 'total_fwd_packets',
        'Total Backward Packets': 'total_bwd_packets',
        'Total Length of Fwd Packets': 'total_fwd_bytes',
        'Total Length of Bwd Packets': 'total_bwd_bytes',
        'Fwd Packet Length Max': 'fwd_pkt_len_max',
        'Fwd Packet Length Min': 'fwd_pkt_len_min',
        'Fwd Packet Length Mean': 'fwd_pkt_len_mean',
        'Fwd Packet Length Std': 'fwd_pkt_len_std',
        'Bwd Packet Length Max': 'bwd_pkt_len_max',
        'Bwd Packet Length Min': 'bwd_pkt_len_min',
        'Bwd Packet Length Mean': 'bwd_pkt_len_mean',
        'Bwd Packet Length Std': 'bwd_pkt_len_std',
        'Flow Bytes/s': 'flow_bytes_per_s',
        'Flow Packets/s': 'flow_packets_per_s',
        'Flow IAT Mean': 'flow_iat_mean',
        'Flow IAT Std': 'flow_iat_std',
        'Flow IAT Max': 'flow_iat_max',
        'Flow IAT Min': 'flow_iat_min',
        'Fwd IAT Mean': 'fwd_iat_mean',
        'Fwd IAT Std': 'fwd_iat_std',
        'Bwd IAT Mean': 'bwd_iat_mean',
        'Bwd IAT Std': 'bwd_iat_std',
        'SYN Flag Count': 'syn_count',
        'ACK Flag Count': 'ack_count',
        'RST Flag Count': 'rst_count',
        'PSH Flag Count': 'psh_count',
        'URG Flag Count': 'urg_count',
        'FIN Flag Count': 'fin_count',
        'Subflow Fwd Packets': 'subflow_fwd_packets',
        'Subflow Bwd Packets': 'subflow_bwd_packets'
    }
    
    # Build feature vector
    row = {}
    for feat_name in feature_names:
        # Try to find matching key in flow_dict
        flow_key = mapping.get(feat_name, feat_name.lower().replace(' ', '_'))
        row[feat_name] = float(flow_dict.get(flow_key, 0.0))
    
    return pd.DataFrame([row], columns=feature_names)