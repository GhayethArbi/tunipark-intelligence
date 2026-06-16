from fastapi import FastAPI
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler

import joblib
import subprocess
import os
from datetime import datetime


MODEL_PATH = "model.pkl"

app = FastAPI(title="TuniPark AI Service")

model = joblib.load(MODEL_PATH)


class PredictionInput(BaseModel):
    distanceKm: float
    availabilityScore: float
    conversionRate: float
    extensionRate: float
    price: float


def load_model():
    global model
    model = joblib.load(MODEL_PATH)


def retrain_model():
    print(f"[{datetime.now()}] Starting automatic retraining...")

    subprocess.run(["python", "export_dataset.py"], check=True)
    subprocess.run(["python", "train.py"], check=True)

    load_model()

    print(f"[{datetime.now()}] Retraining completed. Model reloaded.")


@app.get("/")
def health_check():
    return {
        "status": "OK",
        "service": "TuniPark AI Service",
        "model": MODEL_PATH,
    }


@app.post("/predict")
def predict(input_data: PredictionInput):
    features = [[
        input_data.distanceKm,
        input_data.availabilityScore,
        input_data.conversionRate,
        input_data.extensionRate,
        input_data.price,
    ]]

    score = float(model.predict(features)[0])
    score = max(0, min(100, round(score, 2)))

    if score >= 75:
        recommendation = "HIGHLY_RECOMMENDED"
    elif score >= 55:
        recommendation = "RECOMMENDED"
    else:
        recommendation = "LOW_PRIORITY"

    return {
        "score": score,
        "recommendation": recommendation,
    }


@app.post("/retrain")
def manual_retrain():
    retrain_model()

    return {
        "status": "SUCCESS",
        "message": "Model retrained successfully",
        "timestamp": datetime.now().isoformat(),
    }


scheduler = BackgroundScheduler()
scheduler.add_job(
    retrain_model,
    trigger="interval",
    hours=24,
    id="daily_ai_retraining",
    replace_existing=True,
)
scheduler.start()