import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import joblib
import os

# Loading and preprocessing the CSV data
def load_and_preprocess_data(file_path):
    # Read CSV file
    df = pd.read_csv(file_path)
    
    # Handle missing or invalid values
    df = df.dropna()  # Drop rows with any NaN values
    df = df.replace([np.inf, -np.inf], np.nan).dropna()  # Remove infinite values
    
    # Define the 11 features to match pyclient.py
    features = [
        'track_1',              # S1: Track Sensor S1
        'track_17',             # S17: Track Sensor S17
        'track_9',              # S9: Track Sensor S9
        'trackPos',             # TPos: Track Position
        'angle',                # TAngle: Track Angle
        'prev_gear',            # PGear: Previous Gear
        'rpm',                  # RPM: Rotation Per Minute
        'speedX',               # PSpeed: Previous Speed
        'abs_diff_track_angle_pos',  # DIff: Absolute difference
        'prev_brake',           # PrevBreak: Previous Brake
        'brake'                 # CurrBreak: Current Brake
    ]
    
    # Compute derived features
    df['prev_brake'] = df['brake'].shift(1).fillna(0)  # Previous Brake
    df['prev_gear'] = df['gear'].shift(1).fillna(0)    # Previous Gear
    df['abs_diff_track_angle_pos'] = np.abs(df['angle'] - df['trackPos'])  # Absolute difference
    
    # Verify that we have exactly 11 features
    if len(features) != 11:
        raise ValueError(f"Expected 11 features, but got {len(features)}: {features}")
    
    # Extract input features
    X = df[features]
    
    # Apply PolynomialFeatures for accel, steer, brake models
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X)
    
    # Verify the number of polynomial features
    expected_poly_features = (13 * 12) // 2 - 1  # binomial(11+2, 2) - 1 = 77
    if X_poly.shape[1] != expected_poly_features:
        raise ValueError(f"Expected {expected_poly_features} polynomial features, but got {X_poly.shape[1]}")
    
    # Define target variables
    targets = {
        'accel': df['accel'],
        'gear': df['gear'],  # Predicting next gear
        'steer': df['steer'],
        'brake': df['brake']
    }
    
    return X, X_poly, targets

# Training regression models
def train_models(X, X_poly, targets):
    # Initialize separate LinearRegression instances
    linreg_poly = LinearRegression()  # For accel, steer, brake (77 features)
    linreg_raw = LinearRegression()   # For gear (11 features)
    
    # Dictionary to store models
    models = {}
    
    # Train a model for each target
    for target_name, y in targets.items():
        print(f"Training model for {target_name}...")
        if target_name == 'gear':
            # Train gear model with raw features (11 features)
            linreg_raw.fit(X, y)
            models[target_name] = linreg_raw
            n_input_features = linreg_raw.n_features_in_
            if n_input_features != 11:
                raise ValueError(f"Model {target_name} expected 11 input features, but got {n_input_features}")
            print(f"Model {target_name} expects {n_input_features} input features (no polynomial transformation)")
        else:
            # Train accel, steer, brake with polynomial features (77 features)
            linreg_poly.fit(X_poly, y)
            models[target_name] = linreg_poly
            n_input_features = linreg_poly.n_features_in_
            if n_input_features != 77:
                raise ValueError(f"Model {target_name} expected 77 input features, but got {n_input_features}")
            print(f"Model {target_name} expects {n_input_features} input features")
        print(f"Model for {target_name} trained.")
    
    return models

# Saving models to .sav files
def save_models(models, output_dir="../training/models"):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for target_name, model in models.items():
        filename = os.path.join(output_dir, f"{target_name}_model.sav")
        joblib.dump(model, filename)
        print(f"Saved model for {target_name} to {filename}")
        # Verify the saved model
        loaded_model = joblib.load(filename)
        n_input_features = loaded_model.n_features_in_
        print(f"Verified: Saved model {filename} expects {n_input_features} input features")
        # Print absolute path for debugging
        print(f"Absolute path of saved model: {os.path.abspath(filename)}")

def main():
    # Path to the CSV file
    file_path = './BEST/BEST/lancer oval2.csv'
    
    # Load and preprocess data
    X, X_poly, targets = load_and_preprocess_data(file_path)
    
    # Verify feature counts
    print(f"Training with {X.shape[1]} raw features: {X.columns.tolist()}")
    print(f"Training with {X_poly.shape[1]} polynomial features for accel, steer, brake")
    
    # Train models
    models = train_models(X, X_poly, targets)
    
    # Save models
    save_models(models)

if __name__ == '__main__':
    main()