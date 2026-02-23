from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import statsmodels.api as sm
import pandas as pd

app = FastAPI()

# Load the model
model = sm.load('ols_model.pickle') 

class HouseFeatures(BaseModel):
    overall_qual: int
    gr_liv_area: int
    total_bsmt_sf: float

@app.post("/predict")
def predict_price(features: HouseFeatures):
    
    # We must construct the DataFrame EXACTLY as the model sees it.
    # The model expects: ['const', 'Overall Qual', 'Gr Liv Area', 'Total Bsmt SF']
    input_data = {
        "const": 1.0,  # <--- CRITICAL FIX: Adding the intercept manually
        "Overall Qual": features.overall_qual,
        "Gr Liv Area": features.gr_liv_area,
        "Total Bsmt SF": features.total_bsmt_sf
    }
    
    input_df = pd.DataFrame([input_data])
    
    prediction_results = model.get_prediction(input_df)
    summary_frame = prediction_results.summary_frame(alpha=0.05)
    
    return {
        "point_estimate": round(summary_frame['mean'].iloc[0], 2),
        "lower_bound": round(summary_frame['obs_ci_lower'].iloc[0], 2),
        "upper_bound": round(summary_frame['obs_ci_upper'].iloc[0], 2)
    }

app.mount("/", StaticFiles(directory="static", html=True), name="static")