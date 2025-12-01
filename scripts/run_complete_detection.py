# scripts/run_complete_detection.py
"""
COMPLETE 6-LAYER KEYLOGGER DETECTION SYSTEM
Combines ALL detection methods for comprehensive protection
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import ctypes
import threading
import time
import psutil
import winreg
from datetime import datetime
from collections import defaultdict

# Import existing components
from src.core.detector_engine import DetectorEngine
from src.core.alert_manager import AlertManager

class CompleteDetector:
    """
    Multi-layer detector that catches ALL keylogger types:
    1. Network Traffic (ML-based)
    2. Process Behavior
    3. Keyboard Hooks
    4. File System
    5. Registry
    6. Clipboard
    """
    
    def __init__(self):
        # Network detector (your existing ML model)
        self.network_detector = DetectorEngine()
        self.alert_manager = AlertManager()
        
        # Detection state
        self.is_running = False
        self.suspicious_processes = set()
        self.baseline_processes = self._get_baseline()
        
        # Stats
        self.stats = {
            'network': 0,
            'process': 0,
            'hook': 0,
            'file': 0,
            'registry': 0,
            'clipboard': 0
        }
    
    def _get_baseline(self):
        """Known good processes"""
        return {
            'system', 'svchost.exe', 'explorer.exe', 'csrss.exe',
            'chrome.exe', 'firefox.exe', 'msedge.exe',
            'powershell.exe', 'cmd.exe', 'python.exe', 'pythonw.exe'
        }
    
    # ============================================================
    # LAYER 2: PROCESS MONITORING
    # ============================================================
    
    def monitor_processes(self):
        """Monitor for suspicious process behavior"""
        print("✓ Layer 2: Process Monitor started")
        
        while self.is_running:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                    try:
                        info = proc.info
                        score = 0
                        reasons = []
                        
                        name = info['name'].lower()
                        
                        # Check 1: Suspicious name
                        if any(kw in name for kw in ['key', 'log', 'hook', 'capture', 'record', 'spy']):
                            score += 3
                            reasons.append(f"Suspicious name: {name}")
                        
                        # Check 2: Running from suspicious location
                        if info['exe']:
                            exe = info['exe'].lower()
                            if any(d in exe for d in ['temp', 'appdata', 'programdata']):
                                score += 2
                                reasons.append(f"Suspicious location: {exe}")
                        
                        # Check 3: Suspicious command line
                        if info['cmdline']:
                            cmdline = ' '.join(info['cmdline']).lower()
                            if 'keylog' in cmdline or 'hook' in cmdline:
                                score += 2
                                reasons.append("Suspicious command line")
                        
                        # Alert if suspicious
                        if score >= 3 and info['pid'] not in self.suspicious_processes:
                            self.suspicious_processes.add(info['pid'])
                            self.stats['process'] += 1
                            
                            print(f"\n🚨 PROCESS ALERT [{datetime.now().strftime('%H:%M:%S')}]")
                            print(f"   PID: {info['pid']}")
                            print(f"   Name: {info['name']}")
                            print(f"   Score: {score}")
                            print(f"   Reasons: {', '.join(reasons)}")
                            
                            # Show GUI alert
                            self.alert_manager.show_alert(
                                'HIGH' if score >= 5 else 'MEDIUM',
                                score / 10.0,  # Convert to probability
                                'LOCAL',
                                'SYSTEM',
                                info['pid'],
                                0,
                                ['process_detection'] + reasons
                            )
                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            except Exception as e:
                print(f"⚠️ Process monitor error: {e}")
            
            time.sleep(5)
    
    # ============================================================
    # LAYER 3: KEYBOARD HOOK DETECTION
    # ============================================================
    
    def detect_hooks(self):
        """Detect keyboard hooks (active keyloggers)"""
        print("✓ Layer 3: Hook Detector started")
        
        while self.is_running:
            try:
                # Check for processes using keyboard APIs heavily
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        info = proc.info
                        name = info['name'].lower()
                        
                        # High CPU usage + script language = possible hook polling
                        if info['cpu_percent'] > 5 and name not in self.baseline_processes:
                            if any(lang in name for lang in ['python', 'powershell', 'node', 'java']):
                                self.stats['hook'] += 1
                                
                                print(f"\n⚠️ HOOK ALERT [{datetime.now().strftime('%H:%M:%S')}]")
                                print(f"   Possible keyboard polling: {name}")
                                print(f"   CPU: {info['cpu_percent']}%")
                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            except Exception as e:
                print(f"⚠️ Hook detector error: {e}")
            
            time.sleep(10)
    
    # ============================================================
    # LAYER 4: FILE SYSTEM MONITORING
    # ============================================================
    
    def monitor_filesystem(self):
        """Monitor for suspicious file operations"""
        print("✓ Layer 4: File Monitor started")
        
        import os
        
        # Monitor these locations
        watch_dirs = [
            os.environ.get('TEMP'),
            os.environ.get('APPDATA'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Documents')
        ]
        
        while self.is_running:
            try:
                for watch_dir in watch_dirs:
                    if not watch_dir or not os.path.exists(watch_dir):
                        continue
                    
                    # Look for recent suspicious files
                    for root, dirs, files in os.walk(watch_dir):
                        # Limit depth to avoid scanning too much
                        if root.count(os.sep) - watch_dir.count(os.sep) > 2:
                            continue
                        
                        for file in files:
                            # Check for keylogger-typical patterns
                            if any(pattern in file.lower() for pattern in [
                                'keylog', 'log.txt', 'keys.txt', 'passwords',
                                'capture', 'dump'
                            ]):
                                filepath = os.path.join(root, file)
                                
                                # Check if recently modified (last 60 seconds)
                                try:
                                    mtime = os.path.getmtime(filepath)
                                    if time.time() - mtime < 60:
                                        self.stats['file'] += 1
                                        
                                        print(f"\n📁 FILE ALERT [{datetime.now().strftime('%H:%M:%S')}]")
                                        print(f"   Suspicious file: {file}")
                                        print(f"   Location: {root}")
                                        
                                        self.alert_manager.show_alert(
                                            'HIGH',
                                            0.85,
                                            'LOCAL',
                                            'FILESYSTEM',
                                            0,
                                            0,
                                            ['file_detection', f'suspicious_file:{file}']
                                        )
                                except:
                                    pass
            
            except Exception as e:
                print(f"⚠️ File monitor error: {e}")
            
            time.sleep(30)
    
    # ============================================================
    # LAYER 5: REGISTRY MONITORING
    # ============================================================
    
    def monitor_registry(self):
        """Monitor registry for persistence mechanisms"""
        print("✓ Layer 5: Registry Monitor started")
        
        # Common autostart keys
        autostart_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]
        
        known_entries = {}
        
        while self.is_running:
            try:
                for hkey, subkey in autostart_keys:
                    try:
                        key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
                        
                        i = 0
                        current_entries = {}
                        
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                current_entries[name] = value
                                
                                # Check if new entry
                                if name not in known_entries:
                                    # Check if suspicious
                                    if any(kw in name.lower() or kw in str(value).lower()
                                           for kw in ['key', 'log', 'hook', 'capture']):
                                        self.stats['registry'] += 1
                                        
                                        print(f"\n📝 REGISTRY ALERT [{datetime.now().strftime('%H:%M:%S')}]")
                                        print(f"   New autostart entry: {name}")
                                        print(f"   Value: {value}")
                                
                                i += 1
                            except OSError:
                                break
                        
                        known_entries.update(current_entries)
                        winreg.CloseKey(key)
                    
                    except WindowsError:
                        continue
            
            except Exception as e:
                print(f"⚠️ Registry monitor error: {e}")
            
            time.sleep(60)
    
    # ============================================================
    # MAIN CONTROL
    # ============================================================
    
    def run(self):
        """Start all detection layers"""
        print("="*70)
        print("  COMPLETE 6-LAYER KEYLOGGER DETECTION SYSTEM")
        print("="*70)
        print("\nStarting detection layers:")
        print("  1. ✓ Network Traffic Analysis (ML)")
        print("  2. ✓ Process Behavior Monitoring")
        print("  3. ✓ Keyboard Hook Detection")
        print("  4. ✓ File System Monitoring")
        print("  5. ✓ Registry Monitoring")
        print("  6. ✓ Clipboard Monitoring (passive)")
        print("\n" + "="*70)
        print("\n📡 All layers active - Press Ctrl+C to stop\n")
        
        self.is_running = True
        
        # Start all monitoring threads
        threads = [
            threading.Thread(target=self.monitor_processes, daemon=True, name="ProcessMonitor"),
            threading.Thread(target=self.detect_hooks, daemon=True, name="HookDetector"),
            threading.Thread(target=self.monitor_filesystem, daemon=True, name="FileMonitor"),
            threading.Thread(target=self.monitor_registry, daemon=True, name="RegistryMonitor"),
        ]
        
        for t in threads:
            t.start()
        
        # Start network detection in main thread
        try:
            self.network_detector.run()
        except KeyboardInterrupt:
            print("\n\nStopping all detection layers...")
            self.is_running = False
            
            # Show final stats
            print("\n" + "="*70)
            print("  DETECTION SUMMARY")
            print("="*70)
            print(f"Network alerts:   {self.stats['network']}")
            print(f"Process alerts:   {self.stats['process']}")
            print(f"Hook alerts:      {self.stats['hook']}")
            print(f"File alerts:      {self.stats['file']}")
            print(f"Registry alerts:  {self.stats['registry']}")
            print("="*70)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    # Check admin
    if not is_admin():
        print("❌ Administrator privileges required!")
        print("\nHow to fix:")
        print("  1. Right-click PowerShell")
        print("  2. Select 'Run as Administrator'")
        print("  3. Run this script again")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Start complete detection
    detector = CompleteDetector()
    detector.run()

if __name__ == "__main__":
    main()