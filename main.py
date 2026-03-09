from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import plotly.express as px
import json
import joblib
from scipy.special import inv_boxcox

app = FastAPI()

model_package = joblib.load('elasticnet_model.joblib')
model = model_package['model']
boxcox_lambda = model_package['lambda_value']

class HouseFeatures(BaseModel):
    overall_qual: int
    gr_liv_area: float
    total_bsmt_sf: float
    tot_rms_abv_grd: int
    full_bath: int
    garage_cars: int
    age: int
    neighborhood: str
    foundation: str
    building_type: str
    sale_type: str
    sale_condition: str

df_analysis = pd.read_csv('ames.csv')

@app.get('/api/analysis-graph')
def get_analysis_graph():
    fig = px.scatter(
        df_analysis,
        x='GrLivArea',
        y='SalePrice',
        title='Above Ground Living Area vs. Sale Price',
        labels={'GrLivArea': 'Above Ground Living Area (sq ft)', 'SalePrice': 'Sale Price ($)'},
        color_discrete_sequence=['#4CAF50'],
        opacity=0.7
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='antiquewhite')
    )
    return json.loads(fig.to_json())

boxplot_analysis = pd.read_csv('ames.csv')

@app.get('/api/boxplot-graph')
def get_boxplot_graph():
    fig = px.box(
        boxplot_analysis,
        x='BldgType',
        y='SalePrice',
        title='Sale Price Distribution by Building Type',
        labels={'BldgType': 'Building Type', 'SalePrice': 'Sale Price ($)'},
        color_discrete_sequence=['#4CAF50']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='antiquewhite')
    )
    return json.loads(fig.to_json())

@app.get('/api/lineplot')
def lineplot_graph():
    line_data = df_analysis.groupby('OverallQual')['SalePrice'].mean().reset_index()
    fig = px.line(
        line_data,
        x='OverallQual',
        y='SalePrice',
        title='Average Sale Price by Overall Quality',
        labels={
            'OverallQual': 'Overall Quality (1-10)',
            'SalePrice': 'Average Sale Price ($)'
        },
        color_discrete_sequence=['#4CAF50']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='antiquewhite')
    )
    return json.loads(fig.to_json())

@app.post("/predict")
def predict_price(features: HouseFeatures):
    sf_interaction = features.gr_liv_area + features.total_bsmt_sf
    rms_bath = features.tot_rms_abv_grd * features.full_bath

    input_data = {
        'SFinteraction': sf_interaction,
        'OverallQual': features.overall_qual,
        'RmsBath': rms_bath,
        'GarageCars': features.garage_cars,
        'Age': features.age,
        'Neighborhood': features.neighborhood,
        'Foundation': features.foundation,
        'BuildingType': features.building_type,
        'SaleType': features.sale_type,
        'SaleCondition': features.sale_condition
    }
    input_df = pd.DataFrame([input_data])

    transformed_prediction = model.predict(input_df)[0]
    actual_price = inv_boxcox(transformed_prediction, boxcox_lambda)

    margin = actual_price * 0.08
    lower_bound = actual_price - margin
    upper_bound = actual_price + margin

    return {
        "point_estimate": round(actual_price, 2),
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2)
    }

app.mount("/", StaticFiles(directory="static", html=True), name="static")