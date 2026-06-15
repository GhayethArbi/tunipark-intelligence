import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

DATASET_PATH = "dataset.csv"
MODEL_PATH = "model.pkl"

data = pd.read_csv(DATASET_PATH)

features = [
    "distanceKm",
    "availabilityScore",
    "conversionRate",
    "extensionRate",
    "price",
]

X = data[features]
y = data["score"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("MAE:", mean_absolute_error(y_test, predictions))
print("R2:", r2_score(y_test, predictions))

joblib.dump(model, MODEL_PATH)

print("Model saved to", MODEL_PATH)