# scripts/run_detection.py
"""Main entry point - run this to start detection"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import ctypes
from src.core.detector_engine import DetectorEngine

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
    
    # Start detection
    engine = DetectorEngine()
    engine.run()

if __name__ == "__main__":
    main()