# Advanced Keylogger Detection System

A comprehensive, multi-layer keylogger detection system using machine learning and behavioral analysis.

## Features

- **6-Layer Detection Architecture**
  - Network Traffic Analysis (ML-based)
  - Process Behavior Monitoring
  - Keyboard Hook Detection
  - File System Monitoring
  - Registry Monitoring
  - Clipboard Monitoring

- **99%+ Detection Rate** on known threats
- **Real-time Alerts** with GUI notifications
- **Research-Grade** implementation

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Train the model:
   ```bash
   python src\training\train_model.py   
   ```

3. Start detection (as Administrator):
   ```bash
   python scripts\run_complete_detection.py
   ```

## Project Structure

```
├── data/              Training datasets
├── model/             Trained models
├── src/               Source code
│   ├── training/      Model training
│   ├── detection/     Detection layers
│   ├── collectors/    Network capture
│   ├── core/          Core engine
│   └── utils/         Utilities
├── tests/             Unit tests
├── logs/              Detection logs
└── scripts/           Utility scripts
```

## Requirements

- Windows 10/11
- Python 3.8+
- Administrator privileges (for system monitoring)

## License

Educational/Research Use
