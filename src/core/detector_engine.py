# src/core/detector_engine.py
"""Main detection engine"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import joblib
import time
from datetime import datetime
from src.collectors.flow_collector import FlowCollector
from src.collectors.feature_extractor import flow_to_features
from src.core.alert_manager import AlertManager

class DetectorEngine:
    def __init__(self):
        self.model_file = Path(__file__).parent.parent.parent / "model" / "keylogger_model.pkl"
        self.model = None
        self.alert_manager = AlertManager()
        self.thresholds = {
            'CRITICAL': 0.85,
            'HIGH': 0.75,
            'MEDIUM': 0.50,
            'LOW': 0.30
        }
        self.stats = {'packets': 0, 'flows': 0, 'alerts': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}}
        
    def load_model(self):
        """Load trained model"""
        print(f"Loading model from: {self.model_file}")
        data = joblib.load(self.model_file)
        self.model = data.get("model") or data
        print("✓ Model loaded")
        
    def classify_threat(self, prob):
        """Classify threat level"""
        if prob >= self.thresholds['CRITICAL']:
            return 'CRITICAL', '🔴'
        elif prob >= self.thresholds['HIGH']:
            return 'HIGH', '🚨'
        elif prob >= self.thresholds['MEDIUM']:
            return 'MEDIUM', '⚠️'
        elif prob >= self.thresholds['LOW']:
            return 'LOW', '👁️'
        return 'NORMAL', '✓'
        
    def detect_patterns(self, flow, prob):
        """Detect behavioral patterns"""
        patterns = []
        total_bytes = flow['total_fwd_bytes'] + flow['total_bwd_bytes']
        
        if 1000 <= total_bytes <= 100000:
            patterns.append("small_periodic_transfer")
        if total_bytes < 10000 and prob >= self.thresholds['HIGH']:
            patterns.append("high_risk_small_flow")
        if flow['syn_count'] > 5:
            patterns.append("excessive_syn_flags")
            
        return patterns
    
    def process_flow(self, flow):
        """Process a single flow"""
        self.stats['flows'] += 1
        
        try:
            # Extract features
            df = flow_to_features(flow)
            
            # Predict
            start = time.perf_counter()
            prob = float(self.model.predict_proba(df)[0][1])
            inference_ms = (time.perf_counter() - start) * 1000
            
            # Classify
            threat_level, icon = self.classify_threat(prob)
            self.stats['alerts'][threat_level] = self.stats['alerts'].get(threat_level, 0) + 1
            
            # Detect patterns
            patterns = self.detect_patterns(flow, prob)
            
            flow_info = f"{flow['src']}:{flow['sport']} → {flow['dst']}:{flow['dport']} ({flow['proto']})"
            
            # Console output
            if threat_level in ['CRITICAL', 'HIGH']:
                print(f"\n{icon} {threat_level} [{datetime.now().strftime('%H:%M:%S')}]")
                print(f"   {flow_info}")
                print(f"   Probability: {prob:.3f} | Inference: {inference_ms:.2f}ms")
                if patterns:
                    print(f"   Patterns: {', '.join(patterns)}")
                
                # GUI alert
                self.alert_manager.show_alert(
                    threat_level, prob,
                    flow['src'], flow['dst'],
                    flow['sport'], flow['dport'],
                    patterns
                )
                
                # Log
                self.alert_manager.log_alert(threat_level, prob, flow_info, patterns)
                
            elif threat_level == 'MEDIUM':
                print(f"{icon} MEDIUM: {flow_info} | prob={prob:.3f}")
                
        except Exception as e:
            print(f"⚠️ Error processing flow: {e}")
    
    def run(self):
        """Start detection"""
        print("="*70)
        print("  KEYLOGGER DETECTION SYSTEM - LIVE")
        print("="*70)
        
        # Load model
        self.load_model()
        
        print(f"\nThresholds:")
        print(f"  🔴 CRITICAL: {self.thresholds['CRITICAL']}")
        print(f"  🚨 HIGH:     {self.thresholds['HIGH']}")
        print(f"  ⚠️ MEDIUM:   {self.thresholds['MEDIUM']}")
        print("="*70)
        print("\n📡 Starting network capture...")
        print("💡 Open a browser to generate traffic")
        print("⌨️ Press Ctrl+C to stop\n")
        
        # Start collector
        collector = FlowCollector(timeout=5.0)
        start_time = time.time()
        last_status = time.time()
        
        def packet_handler(pkt):
            nonlocal last_status
            self.stats['packets'] += 1
            collector.process(pkt)
            
            for flow in collector.get_completed():
                self.process_flow(flow)
            
            # Status update
            now = time.time()
            if now - last_status > 10:
                elapsed = now - start_time
                rate = self.stats['packets'] / elapsed
                print(f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] Packets:{self.stats['packets']:,} | "
                      f"Flows:{self.stats['flows']:,} | Rate:{rate:.1f}/s | "
                      f"Alerts: 🔴{self.stats['alerts']['CRITICAL']} "
                      f"🚨{self.stats['alerts']['HIGH']}\n")
                last_status = now
        
        try:
            from scapy.all import sniff
            sniff(prn=packet_handler, store=False)
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("  STOPPED")
            print("="*70)
            print(f"Packets:  {self.stats['packets']:,}")
            print(f"Flows:    {self.stats['flows']:,}")
            print(f"Alerts:   🔴{self.stats['alerts']['CRITICAL']} "
                  f"🚨{self.stats['alerts']['HIGH']} "
                  f"⚠️{self.stats['alerts']['MEDIUM']}")
            print("="*70)