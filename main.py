from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import statsmodels.api as sm
import pandas as pd
import plotly.express as px
import json


app = FastAPI()

# Load the model
model = sm.load('ols_model.pickle') 

class HouseFeatures(BaseModel):
    overall_qual: int
    gr_liv_area: int
    total_bsmt_sf: float

df_analysis = pd.read_csv('AMES_Selected.csv')  # Ensure this file exists and has the correct columns


@app.get('/api/analysis-graph')
def get_analysis_graph():
    fig = px.scatter(
        df_analysis, 
        x='Gr Liv Area', 
        y='SalePrice',
        title='Above Ground Living Area vs. Sale Price',
        labels={'Gr Liv Area': 'Above Ground Living Area (sq ft)', 'SalePrice': 'Sale Price ($)'},
        color_discrete_sequence=['#4CAF50'], # Matching your site's green accent
        opacity=0.7
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='antiquewhite')
    )
    graph_json = json.loads(fig.to_json())
    return graph_json

boxplot_analysis = pd.read_csv('boxplot.csv')

@app.get('/api/boxplot-graph')
def get_boxplot_graph():
    fig = px.box(
        boxplot_analysis, 
        x='Building Type', 
        y='SalePrice',
        title='Sale Price Distribution by Building Type',
        labels={'Building Type': 'Building Type', 'SalePrice': 'Sale Price ($)'},
        color_discrete_sequence=['#4CAF50'] # Matching your site's green accent
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='antiquewhite')
    )
    graph_json = json.loads(fig.to_json())
    return graph_json


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