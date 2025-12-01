# scripts/demo_guaranteed.py
"""
GUARANTEED ALERT DEMO - For Live Presentations
Feeds real keylogger samples from dataset to trigger alerts 100%
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import joblib
import time
from datetime import datetime
from src.collectors.feature_extractor import flow_to_features
from src.core.alert_manager import AlertManager

def convert_row_to_flow(row):
    """Convert dataset row to flow dict"""
    flow = {}
    
    feature_map = {
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
    
    for dataset_col, flow_col in feature_map.items():
        flow[flow_col] = float(row.get(dataset_col, 0)) if pd.notna(row.get(dataset_col)) else 0.0
    
    # Add network info
    flow['src'] = str(row.get('Source IP', '192.168.1.100'))
    flow['dst'] = str(row.get('Destination IP', '203.0.113.42'))
    
    try:
        flow['sport'] = int(row.get('Source Port', 54321))
        flow['dport'] = int(row.get('Destination Port', 443))
    except:
        flow['sport'] = 54321
        flow['dport'] = 443
    
    flow['proto'] = str(row.get('Protocol', 'TCP'))
    
    return flow

def main():
    print("="*70)
    print("  GUARANTEED ALERT DEMO")
    print("  Testing with Real Keylogger Samples")
    print("="*70)
    
    BASE_DIR = Path(__file__).parent.parent
    
    # Load model
    print("\nLoading model...")
    model_file = BASE_DIR / "model" / "keylogger_model.pkl"
    try:
        model_data = joblib.load(model_file)
        model = model_data.get("model") or model_data
        print("✓ Model loaded")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("\nMake sure you've trained the model first:")
        print("  python src\\training\\train_model.py")
        return
    
    # Load dataset
    print("\nLoading dataset...")
    data_file = BASE_DIR / "data" / "Keylogger_Detection.csv"
    try:
        df = pd.read_csv(data_file, low_memory=False)
        df.columns = [c.strip() for c in df.columns]
        print(f"✓ Loaded {len(df):,} samples")
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return
    
    # Get keylogger samples
    label_col = [c for c in df.columns if c.lower() in ['class', 'label']][0]
    keylogger_df = df[df[label_col].astype(str).str.lower().str.contains('key|mal', na=False)]
    print(f"✓ Found {len(keylogger_df):,} keylogger samples\n")
    
    # Initialize alert manager
    alert_mgr = AlertManager()
    
    # Thresholds
    thresholds = {
        'CRITICAL': 0.85,
        'HIGH': 0.75,
        'MEDIUM': 0.50,
        'LOW': 0.30
    }
    
    # Test with 10 samples
    num_tests = min(10, len(keylogger_df))
    print(f"Testing {num_tests} keylogger samples...")
    print("These WILL trigger HIGH/CRITICAL alerts!\n")
    
    input("Press Enter to start demo...")
    print()
    
    results = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'MISS': 0}
    samples = keylogger_df.sample(n=num_tests)
    
    for idx, (_, row) in enumerate(samples.iterrows(), 1):
        print(f"{'='*70}")
        print(f"Test {idx}/{num_tests} - [{datetime.now().strftime('%H:%M:%S')}]")
        print(f"{'='*70}")
        
        # Convert to flow
        flow = convert_row_to_flow(row)
        
        print(f"Flow: {flow['src']}:{flow['sport']} → {flow['dst']}:{flow['dport']}")
        print(f"Protocol: {flow['proto']}")
        print(f"Bytes: {int(flow['total_fwd_bytes'] + flow['total_bwd_bytes']):,}")
        
        # Run detection
        try:
            # Extract features
            df_features = flow_to_features(flow)
            
            # Predict
            start = time.perf_counter()
            prob = float(model.predict_proba(df_features)[0][1])
            inference_ms = (time.perf_counter() - start) * 1000
            
            print(f"\n🎯 Detection Result:")
            print(f"   Probability: {prob:.3f} ({prob*100:.1f}%)")
            print(f"   Inference Time: {inference_ms:.2f}ms")
            
            # Classify
            if prob >= thresholds['CRITICAL']:
                threat_level = "CRITICAL"
                icon = "🔴"
                results['CRITICAL'] += 1
            elif prob >= thresholds['HIGH']:
                threat_level = "HIGH"
                icon = "🚨"
                results['HIGH'] += 1
            elif prob >= thresholds['MEDIUM']:
                threat_level = "MEDIUM"
                icon = "⚠️"
                results['MEDIUM'] += 1
            elif prob >= thresholds['LOW']:
                threat_level = "LOW"
                icon = "👁️"
                results['LOW'] += 1
            else:
                threat_level = "MISS"
                icon = "❌"
                results['MISS'] += 1
            
            print(f"   Threat Level: {icon} {threat_level}")
            
            # Show GUI alert for HIGH/CRITICAL
            if threat_level in ['HIGH', 'CRITICAL']:
                print(f"\n   📢 Showing GUI alert...")
                
                patterns = ['dataset_keylogger_sample', 'known_malicious_flow']
                total_bytes = flow['total_fwd_bytes'] + flow['total_bwd_bytes']
                if 1000 <= total_bytes <= 100000:
                    patterns.append('small_periodic_transfer')
                
                # Trigger GUI popup
                alert_mgr.show_alert(
                    threat_level,
                    prob,
                    flow['src'],
                    flow['dst'],
                    flow['sport'],
                    flow['dport'],
                    patterns
                )
                
                # Log alert
                flow_info = f"{flow['src']}:{flow['sport']} → {flow['dst']}:{flow['dport']}"
                alert_mgr.log_alert(threat_level, prob, flow_info, patterns)
                
                print(f"   ✓ GUI alert shown!")
            
            print()
            
        except Exception as e:
            print(f"\n❌ Detection failed: {e}\n")
            import traceback
            traceback.print_exc()
            results['MISS'] += 1
        
        # Pause between tests
        if idx < num_tests:
            time.sleep(3)
    
    # Summary
    print("\n" + "="*70)
    print("  DEMO SUMMARY")
    print("="*70)
    print(f"Total Tests:        {num_tests}")
    print(f"🔴 CRITICAL:        {results['CRITICAL']}")
    print(f"🚨 HIGH:            {results['HIGH']}")
    print(f"⚠️  MEDIUM:          {results['MEDIUM']}")
    print(f"👁️  LOW:             {results['LOW']}")
    print(f"❌ MISS:            {results['MISS']}")
    print()
    
    success_rate = ((results['CRITICAL'] + results['HIGH']) / num_tests) * 100
    print(f"Detection Rate (HIGH/CRITICAL): {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n✅ EXCELLENT - Demo successful!")
    elif success_rate >= 60:
        print("\n✓ GOOD - Demo successful")
    else:
        print("\n⚠️  MODERATE - Some samples not detected as expected")
    
    print("\n📁 Alert logs saved to: alerts/")
    print("="*70)

if __name__ == "__main__":
    main()