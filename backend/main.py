import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field

# --- Initialize FastAPI ---
app = FastAPI(title="Diamond Price Inference Server Component")

# --- Security Configuration ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Supported secure client api-keys
VALID_API_KEYS = {"Vijay@10", "123"}

async def verify_client_api_key(api_key: str = Depends(api_key_header)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized client signature credentials."
        )
    return api_key

# --- Robust Absolute Path Resolution ---
# Finds the directory containing this file (backend/)
BASE_DIR = Path(__file__).resolve().parent

# Moves up one level to the root directory, then steps into artifacts/
DEFAULT_PIPELINE_PATH = BASE_DIR.parent / "artifacts" / "diamond_pipeline.pkl"

# Fallback environment variable check for containerized deployment
PIPELINE_PATH = os.getenv("MODEL_PATH", str(DEFAULT_PIPELINE_PATH))

# --- Unified Pipeline Model Initialization ---
if os.path.exists(PIPELINE_PATH):
    engine_pipeline = joblib.load(PIPELINE_PATH)
    print(f"[INFO] Success: Unified ML Model pipeline loaded from {PIPELINE_PATH}")
else:
    engine_pipeline = None
    print(f"[ERROR] Executable pipeline file missing from path: {PIPELINE_PATH}")

# --- Input Payload Validation (Pydantic V2 Compliant) ---
class DiamondFeatures(BaseModel):
    carat: float = Field(..., examples=[0.23])
    cut: str = Field(..., examples=["Ideal"])
    color: str = Field(..., examples=["E"])
    clarity: str = Field(..., examples=["SI2"])
    depth: float = Field(..., examples=[61.5])
    table: float = Field(..., examples=[55.0])
    x: float = Field(..., examples=[3.95])
    y: float = Field(..., examples=[3.98])
    z: float = Field(..., examples=[2.43])

# --- API Endpoints ---
@app.get ('/')
def home():
    return {"message":"Welcome to diamomd price predictor"}



@app.get("/health")
def health_check():
    """Verifies API status and ensures the model weights are actively loaded."""
    return {"status": "healthy", "model_loaded": engine_pipeline is not None}

@app.post("/predict", dependencies=[Depends(verify_client_api_key)])
def execute_prediction(payload: DiamondFeatures):
    if engine_pipeline is None:
        raise HTTPException(
            status_code=503, 
            detail="ML Model pipeline is currently uninitialized."
        )
    
    try:
        # 1. Convert user's incoming payload dictionary into a pandas DataFrame
        input_df = pd.DataFrame([payload.model_dump()])
        
        # 2. Arrange features in the exact sequential order your training data split had
        raw_feature_order = ['carat', 'cut', 'color', 'clarity', 'depth', 'table', 'x', 'y', 'z']
        input_df = input_df[raw_feature_order]
        
        # 3. Fire processing inference directly! 
        # The pipeline handles scaling and One-Hot Encoding internally automatically.
        prediction = engine_pipeline.predict(input_df)
        
        return {
            "status": "success",
            "valuation_usd": float(np.round(prediction[0], 2))
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Runtime Inference Exception: {str(e)}"
        )