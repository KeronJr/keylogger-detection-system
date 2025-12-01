# src/core/alert_manager.py
"""Alert management with GUI popups and sound"""
import tkinter as tk
import threading
import winsound
from datetime import datetime
import json
from pathlib import Path

class AlertManager:
    def __init__(self):
        self.alerts_dir = Path(__file__).parent.parent.parent / "alerts"
        self.alerts_dir.mkdir(exist_ok=True)
        
    def show_alert(self, threat_level, probability, src_ip, dst_ip, src_port, dst_port, patterns=None):
        """Show non-blocking alert popup"""
        def _alert_thread():
            # Play sound
            try:
                if threat_level == 'CRITICAL':
                    for _ in range(3):
                        winsound.Beep(1000, 200)
                        winsound.Beep(1500, 200)
                elif threat_level == 'HIGH':
                    winsound.Beep(1000, 300)
                    winsound.Beep(1500, 300)
                else:
                    winsound.Beep(800, 300)
            except:
                pass
            
            # Create popup
            root = tk.Tk()
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            w, h = 450, 350
            x = (screen_w - w) // 2
            y = (screen_h - h) // 2
            root.geometry(f"{w}x{h}+{x}+{y}")
            root.attributes('-topmost', True)
            
            colors = {'CRITICAL': '#d32f2f', 'HIGH': '#f57c00', 'MEDIUM': '#fbc02d', 'LOW': '#afb42b'}
            bg = colors.get(threat_level, '#666')
            root.configure(bg=bg)
            root.title(f"{threat_level} ALERT")
            
            msg = f"""
KEYLOGGER DETECTED

Threat Level: {threat_level}
Confidence: {probability:.1%}

Suspicious Connection:
{src_ip}:{src_port} -> {dst_ip}:{dst_port}

Patterns:
{chr(10).join('* ' + p for p in (patterns or ['Unknown']))}

RECOMMENDED ACTIONS:
* Disconnect from network if suspicious
* Run antivirus scan
* Check running processes

Auto-closing in 10 seconds...
            """
            
            tk.Label(root, text=msg, font=("Consolas", 9), bg=bg, fg="white",
                    justify=tk.LEFT, padx=15, pady=15).pack(expand=True, fill=tk.BOTH)
            
            tk.Button(root, text="ACKNOWLEDGE", command=root.destroy,
                     bg="white", fg=bg, font=("Arial", 11, "bold"),
                     padx=20, pady=8).pack(pady=10)
            
            root.after(10000, root.destroy)
            root.mainloop()
        
        threading.Thread(target=_alert_thread, daemon=True).start()
    
    def log_alert(self, threat_level, probability, flow_info, patterns):
        """Save alert to JSON"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'threat_level': threat_level,
            'probability': probability,
            'flow': flow_info,
            'patterns': patterns
        }
        
        filename = self.alerts_dir / f"alert_{threat_level}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(alert, f, indent=2)