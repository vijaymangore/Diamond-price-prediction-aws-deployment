# backend/pipeline.py
import os
import zipfile
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

def run_training_pipeline(zip_path, output_dir="../artifacts"):
    print("[INFO] Initiating Automated Machine Learning Training Pipeline...")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Automated Data Ingestion Layer from ZIP
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Missing resource dataset at path: {zip_path}")
        
    with zipfile.ZipFile(zip_path, 'r') as z:
        csv_file = [f for f in z.namelist() if f.endswith('.csv')][0]
        with z.open(csv_file) as f:
            df = pd.read_csv(f)
            
    # Remove index column if loaded from your archive format
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
        
    print(f"[INFO] Parsed dataset structure successfully. Shape: {df.shape}")
    
    # 2. Extract targets and declare precise schema matrices
    X = df.drop(columns=['price'])
    y = df['price']
    
    categorical_cols = ['cut', 'color', 'clarity']
    numerical_cols = ['carat', 'depth', 'table', 'x', 'y', 'z']
    
    # 3. Validation Splits
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Composite Preprocessing (Saves exact mathematical transformation mappings)
    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ]
    )
    
    # 5. Core Operational Model Integration
    regressor = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    
    # Unify Transformations + Model steps structurally
    full_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', regressor)
    ])
    
    # 6. Fit and Compute Metrics
    print("[INFO] Fitting composite algorithm architectures...")
    full_pipeline.fit(X_train, y_train)
    
    train_r2 = full_pipeline.score(X_train, y_train)
    test_r2 = full_pipeline.score(X_test, y_test)
    print(f"[METRIC] Training R² Accuracy Score: {train_r2:.4f}")
    print(f"[METRIC] Testing R² Accuracy Score: {test_r2:.4f}")
    
    # 7. Serialize Artifacts safely for backend consumption
    save_path = os.path.join(output_dir, "diamond_pipeline.pkl")
    joblib.dump(full_pipeline, save_path)
    print(f"[INFO] Operational pipeline artifact securely serialized to: {save_path}")

if __name__ == "__main__":
    run_training_pipeline("../data/archive_diamonds.zip")