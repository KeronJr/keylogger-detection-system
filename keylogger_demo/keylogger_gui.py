# keylogger_demo/keylogger_gui.py
"""
CONSENT-BASED KEYLOGGER WITH GUI
For research/testing - shows VISIBLE keylogging with user consent
"""
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