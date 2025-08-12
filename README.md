# TORCS AI Bot

## Overview
This project is an AI-powered autonomous racing car controller for **TORCS**. It uses polynomial regression models to predict acceleration, steering, braking, and gear shifting based on sensor data, enabling the car to navigate tracks autonomously.

## Features
- **Autonomous Driving**: Controls car using real-time sensor data.
- **Polynomial Regression**: Models accel, steer, and brake with degree-2 polynomial features; gear uses linear features.
- **Sensors**: Processes 11 features (e.g., track position, angle, speed, RPM).
- **Modules**: Python client (`pyclient.py`), driver logic (`driver.py`), training script (`regression_training.py`), and utilities.
- **UDP Communication**: Exchanges data with TORCS server.

## Prerequisites
- Python 3.x with `pandas`, `numpy`, `scikit-learn`.
- TORCS simulator with UDP support.
- Dataset CSV (e.g., `lancer oval2.csv`).

## Installation
1. Clone repo:
   ```bash
   git clone https://github.com/yourusername/torcs-ai-bot.git
   ```
2. Install dependencies:
   ```bash
   pip install pandas numpy scikit-learn
   ```
3. Install TORCS and configure for UDP.

## Usage
### Train Models
```bash
python regression_training.py
```
- Trains models on CSV data, saves them as `.sav` files.

### Run Bot
1. Start TORCS in server mode.
2. Run client:
   ```bash
   python pyclient.py
   ```
- Bot drives autonomously using pre-trained models.

## Limitations
- Trained for specific tracks; may need retraining.
- No real-time learning.
- Depends on dataset quality.

## Future Work
- Add reinforcement learning.
- Support multiple tracks.
- Use neural networks for complex tracks.

## Author
- Ali Usman

## License
MIT License. TORCS has its own licensing terms.

*Date: August 12, 2025*
