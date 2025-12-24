"""
Predictive Delay Modeling

Uses historical bus arrival data to predict future delays
based on time patterns, routes, and traffic conditions.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from database import get_database
import pickle
import os

MODEL_FILE = "delay_prediction_model.pkl"
ENCODERS_FILE = "label_encoders.pkl"


class DelayPredictor:
    """ML model for predicting bus arrival delays"""

    def __init__(self):
        """Initialize the predictor"""
        self.model = None
        self.encoders = {}
        self.is_trained = False
        self.load_model()

    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features from raw data

        Features:
        - hour_of_day: 0-23
        - day_of_week: 0-6 (Monday=0)
        - is_weekend: 0 or 1
        - is_peak_hour: 0 or 1 (7-9 AM, 5-8 PM)
        - bus_stop_code: encoded
        - bus_number: encoded
        - load_status: encoded (SEA=0, SDA=1, LSD=2)
        """
        df = data.copy()

        # Convert timestamp to datetime if needed
        if 'recorded_at' in df.columns:
            df['recorded_at'] = pd.to_datetime(df['recorded_at'])
            df['hour_of_day'] = df['recorded_at'].dt.hour
            df['day_of_week'] = df['recorded_at'].dt.dayofweek
        else:
            # Use current time
            now = datetime.now()
            df['hour_of_day'] = now.hour
            df['day_of_week'] = now.weekday()

        # Derived features
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_peak_hour'] = (
            ((df['hour_of_day'] >= 7) & (df['hour_of_day'] <= 9)) |
            ((df['hour_of_day'] >= 17) & (df['hour_of_day'] <= 20))
        ).astype(int)

        # Encode categorical variables
        for col in ['bus_stop_code', 'bus_number', 'load_status']:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.encoders[col].fit_transform(df[col].astype(str))
            else:
                # Handle unknown categories
                known_classes = set(self.encoders[col].classes_)
                df[f'{col}_encoded'] = df[col].astype(str).apply(
                    lambda x: self.encoders[col].transform([x])[0]
                    if x in known_classes else -1
                )

        return df

    def train(self, min_records: int = 100) -> Dict:
        """
        Train the prediction model using historical data

        Args:
            min_records: Minimum number of records needed for training

        Returns:
            Training metrics dictionary
        """
        print("="*60)
        print("Training Delay Prediction Model")
        print("="*60)

        # Fetch historical data
        db = get_database()
        records = db.get_historical_arrivals(days=30)  # Last 30 days

        if len(records) < min_records:
            print(f"✗ Insufficient data: {len(records)} records (need {min_records})")
            return {"error": "Insufficient training data"}

        print(f"✓ Loaded {len(records)} historical records")

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Remove records without delay information
        df = df[df['delay_minutes'].notna()]

        if len(df) < min_records:
            print(f"✗ Insufficient valid records: {len(df)}")
            return {"error": "Insufficient valid records"}

        # Prepare features
        df = self.prepare_features(df)

        # Feature columns
        feature_cols = [
            'hour_of_day', 'day_of_week', 'is_weekend', 'is_peak_hour',
            'bus_stop_code_encoded', 'bus_number_encoded', 'load_status_encoded'
        ]

        X = df[feature_cols]
        y = df['delay_minutes']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        print(f"✓ Training set: {len(X_train)} records")
        print(f"✓ Test set: {len(X_test)} records")

        # Train model (using Gradient Boosting for better performance)
        print("\nTraining Gradient Boosting model...")
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )

        self.model.fit(X_train, y_train)

        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        # Predictions
        y_pred = self.model.predict(X_test)
        mae = np.mean(np.abs(y_test - y_pred))
        rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))

        metrics = {
            "training_records": len(records),
            "valid_records": len(df),
            "train_r2_score": round(train_score, 3),
            "test_r2_score": round(test_score, 3),
            "mean_absolute_error": round(mae, 2),
            "rmse": round(rmse, 2)
        }

        print("\n" + "="*60)
        print("Training Results:")
        print("="*60)
        for key, value in metrics.items():
            print(f"  {key}: {value}")
        print("="*60)

        # Save model
        self.save_model()
        self.is_trained = True

        return metrics

    def predict(self, bus_stop_code: str, bus_number: str,
                load_status: str = "SDA") -> Tuple[float, float]:
        """
        Predict delay for a given bus

        Args:
            bus_stop_code: Bus stop code
            bus_number: Bus service number
            load_status: Current load status (SEA, SDA, LSD)

        Returns:
            Tuple of (predicted_delay_minutes, confidence)
        """
        if not self.is_trained or self.model is None:
            return (0.0, 0.0)

        # Create feature DataFrame
        now = datetime.now()
        data = pd.DataFrame([{
            'bus_stop_code': bus_stop_code,
            'bus_number': bus_number,
            'load_status': load_status,
            'recorded_at': now
        }])

        # Prepare features
        data = self.prepare_features(data)

        feature_cols = [
            'hour_of_day', 'day_of_week', 'is_weekend', 'is_peak_hour',
            'bus_stop_code_encoded', 'bus_number_encoded', 'load_status_encoded'
        ]

        X = data[feature_cols]

        # Predict
        prediction = self.model.predict(X)[0]

        # Calculate confidence (simplified: based on prediction magnitude)
        # Lower delays = higher confidence
        confidence = max(0.5, min(0.95, 1.0 - abs(prediction) / 20.0))

        return (round(prediction, 2), round(confidence, 2))

    def predict_multiple(self, arrivals: List[Dict]) -> List[Dict]:
        """Predict delays for multiple bus arrivals"""
        predictions = []

        for arrival in arrivals:
            delay, confidence = self.predict(
                arrival.get('BusStop'),
                arrival.get('BusNo'),
                arrival.get('Load', 'SDA')
            )

            predictions.append({
                **arrival,
                'predicted_delay': delay,
                'confidence': confidence
            })

        return predictions

    def save_model(self):
        """Save trained model and encoders to disk"""
        if self.model:
            with open(MODEL_FILE, 'wb') as f:
                pickle.dump(self.model, f)

            with open(ENCODERS_FILE, 'wb') as f:
                pickle.dump(self.encoders, f)

            print(f"✓ Model saved to {MODEL_FILE}")

    def load_model(self):
        """Load trained model and encoders from disk"""
        if os.path.exists(MODEL_FILE) and os.path.exists(ENCODERS_FILE):
            try:
                with open(MODEL_FILE, 'rb') as f:
                    self.model = pickle.load(f)

                with open(ENCODERS_FILE, 'rb') as f:
                    self.encoders = pickle.load(f)

                self.is_trained = True
                print(f"✓ Model loaded from {MODEL_FILE}")
                return True
            except Exception as e:
                print(f"⚠ Error loading model: {e}")

        return False


# Singleton instance
_predictor_instance = None


def get_predictor() -> DelayPredictor:
    """Get singleton predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = DelayPredictor()
    return _predictor_instance


if __name__ == "__main__":
    # Test and train model
    print("Testing Predictive Model...")

    predictor = get_predictor()

    # Train if not already trained
    if not predictor.is_trained:
        print("\nNo trained model found. Training new model...")
        metrics = predictor.train()
    else:
        print("\n✓ Model already trained")

    # Test prediction
    print("\nTesting prediction...")
    delay, confidence = predictor.predict("01012", "7", "SEA")
    print(f"Predicted delay: {delay} minutes (confidence: {confidence})")
