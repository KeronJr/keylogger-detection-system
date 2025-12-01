# scripts/trigger_demo_alerts.py
"""
Trigger demo alerts by feeding real keylogger samples to the detector.
Run this WHILE the detector is running in another window.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import time
from datetime import datetime
from src.collectors.feature_extractor import flow_to_features
from src.core.alert_manager import AlertManager
import joblib

def trigger_demo_alerts():
    print("="*70)
    print("  DEMO ALERT TRIGGER")
    print("  (Feeds real keylogger samples to detector)")
    print("="*70)
    
    # Load model and data
    BASE_DIR = Path(__file__).parent.parent
    model_data = joblib.load(BASE_DIR / "model" / "keylogger_model.pkl")
    model = model_data.get("model") or model_data
    
    df = pd.read_csv(BASE_DIR / "data" / "Keylogger_Detection.csv", low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    
    # Get keylogger samples
    label_col = [c for c in df.columns if c.lower() in ['class', 'label']][0]
    keyloggers = df[df[label_col].astype(str).str.lower().str.contains('key|mal', na=False)]
    
    print(f"\n✓ Found {len(keyloggers):,} keylogger samples")
    print(f"\nTriggering 5 demo alerts...")
    print("Watch for GUI popups and sounds!\n")
    
    alert_mgr = AlertManager()
    
    # Trigger 5 alerts
    samples = keyloggers.sample(n=min(5, len(keyloggers)))
    
    for i, (_, row) in enumerate(samples.iterrows(), 1):
        # Convert to flow format
        flow = {
            'flow_duration': float(row.get('Flow Duration', 1.0)),
            'total_fwd_packets': int(row.get('Total Fwd Packets', 10)),
            'total_bwd_packets': int(row.get('Total Backward Packets', 8)),
            'total_fwd_bytes': int(row.get('Total Length of Fwd Packets', 5000)),
            'total_bwd_bytes': int(row.get('Total Length of Bwd Packets', 4000)),
            'fwd_pkt_len_max': float(row.get('Fwd Packet Length Max', 1500)),
            'fwd_pkt_len_min': float(row.get('Fwd Packet Length Min', 60)),
            'fwd_pkt_len_mean': float(row.get('Fwd Packet Length Mean', 500)),
            'fwd_pkt_len_std': float(row.get('Fwd Packet Length Std', 200)),
            'bwd_pkt_len_max': float(row.get('Bwd Packet Length Max', 1400)),
            'bwd_pkt_len_min': float(row.get('Bwd Packet Length Min', 60)),
            'bwd_pkt_len_mean': float(row.get('Bwd Packet Length Mean', 450)),
            'bwd_pkt_len_std': float(row.get('Bwd Packet Length Std', 180)),
            'flow_bytes_per_s': float(row.get('Flow Bytes/s', 6000)),
            'flow_packets_per_s': float(row.get('Flow Packets/s', 12)),
            'flow_iat_mean': float(row.get('Flow IAT Mean', 0.15)),
            'flow_iat_std': float(row.get('Flow IAT Std', 0.05)),
            'flow_iat_max': float(row.get('Flow IAT Max', 0.3)),
            'flow_iat_min': float(row.get('Flow IAT Min', 0.05)),
            'fwd_iat_mean': float(row.get('Fwd IAT Mean', 0.15)),
            'fwd_iat_std': float(row.get('Fwd IAT Std', 0.05)),
            'bwd_iat_mean': float(row.get('Bwd IAT Mean', 0.18)),
            'bwd_iat_std': float(row.get('Bwd IAT Std', 0.06)),
            'syn_count': int(row.get('SYN Flag Count', 1)),
            'ack_count': int(row.get('ACK Flag Count', 15)),
            'rst_count': int(row.get('RST Flag Count', 0)),
            'psh_count': int(row.get('PSH Flag Count', 5)),
            'urg_count': int(row.get('URG Flag Count', 0)),
            'fin_count': int(row.get('FIN Flag Count', 1)),
            'subflow_fwd_packets': int(row.get('Subflow Fwd Packets', 10)),
            'subflow_bwd_packets': int(row.get('Subflow Bwd Packets', 8))
        }
        
        # Predict
        df_features = flow_to_features(flow)
        prob = float(model.predict_proba(df_features)[0][1])
        
        # Determine threat level
        if prob >= 0.85:
            threat = 'CRITICAL'
            icon = '🔴'
        elif prob >= 0.75:
            threat = 'HIGH'
            icon = '🚨'
        else:
            threat = 'MEDIUM'
            icon = '⚠️'
        
        # Fake IPs for demo
        src_ip = row.get('Source IP', '192.168.1.100')
        dst_ip = row.get('Destination IP', '203.0.113.42')
        src_port = int(row.get('Source Port', 54321)) if pd.notna(row.get('Source Port')) else 54321
        dst_port = int(row.get('Destination Port', 443)) if pd.notna(row.get('Destination Port')) else 443
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Alert {i}/5: {icon} {threat}")
        print(f"  Flow: {src_ip}:{src_port} → {dst_ip}:{dst_port}")
        print(f"  Probability: {prob:.3f}")
        
        # Trigger GUI alert
        alert_mgr.show_alert(
            threat, prob,
            str(src_ip), str(dst_ip),
            src_port, dst_port,
            ['demo_keylogger_sample', 'known_malicious_pattern']
        )
        
        print(f"  ✓ GUI popup shown!\n")
        
        time.sleep(3)  # Pause between alerts
    
    print("="*70)
    print("  DEMO COMPLETE")
    print("="*70)
    print("\n✓ Triggered 5 alerts with GUI popups")
    print(f"✓ Alerts logged to: {Path(__file__).parent.parent / 'alerts'}")
    print("\nCheck the alerts folder for JSON logs!")
    print("="*70)

if __name__ == "__main__":
    trigger_demo_alerts()