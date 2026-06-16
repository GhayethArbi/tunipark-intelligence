import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


DATASET_PATH = "dataset.csv"
MODEL_PATH = "model.pkl"

FEATURES = [
    "distanceKm",
    "availabilityScore",
    "conversionRate",
    "extensionRate",
    "price",
]

TARGET = "score"


def train_model():
    df = pd.read_csv(DATASET_PATH)

    missing_columns = [col for col in FEATURES + [TARGET] if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in dataset.csv: {missing_columns}")

    df = df.dropna(subset=FEATURES + [TARGET])

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    joblib.dump(model, MODEL_PATH)

    print("Training completed successfully.")
    print(f"Rows used: {len(df)}")
    print(f"MAE: {mae:.2f}")
    print(f"R2 score: {r2:.3f}")
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()