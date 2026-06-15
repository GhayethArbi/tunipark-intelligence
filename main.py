from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).parent / "model.pkl"

app = FastAPI(title="TuniPark AI Recommendation Service")

model = joblib.load(MODEL_PATH)


class ParkingPredictionInput(BaseModel):
    distanceKm: float = Field(..., ge=0)
    availabilityScore: float = Field(..., ge=0, le=1)
    conversionRate: float = Field(..., ge=0, le=1)
    extensionRate: float = Field(..., ge=0, le=1)
    price: float = Field(..., ge=0)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(input_data: ParkingPredictionInput):
    df = pd.DataFrame(
        [
            {
                "distanceKm": input_data.distanceKm,
                "availabilityScore": input_data.availabilityScore,
                "conversionRate": input_data.conversionRate,
                "extensionRate": input_data.extensionRate,
                "price": input_data.price,
            }
        ]
    )

    raw_score = float(model.predict(df)[0])
    score = max(0, min(100, round(raw_score)))

    if score >= 70:
        recommendation = "HIGHLY_RECOMMENDED"
    elif score >= 40:
        recommendation = "RECOMMENDED"
    else:
        recommendation = "LOW_PRIORITY"

    return {
        "score": score,
        "recommendation": recommendation,
    }