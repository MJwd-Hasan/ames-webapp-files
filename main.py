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
@app.get('/api/mapplot')
def mapplot_graph():
    # 1. Get the median sale price per neighborhood
    map_data = df_analysis.groupby('Neighborhood')['SalePrice'].median().reset_index()

    # 2. Inject approximate Latitude and Longitude for Ames, Iowa
    coords = {
        'NAmes': [42.042, -93.621], 'CollgCr': [42.019, -93.651], 'OldTown': [42.030, -93.614],
        'Edwards': [42.022, -93.663], 'Somerst': [42.052, -93.644], 'Gilbert': [42.107, -93.648],
        'NridgHt': [42.060, -93.655], 'Sawyer': [42.033, -93.666], 'NWAmes': [42.048, -93.633],
        'SawyerW': [42.034, -93.682], 'Mitchel': [41.990, -93.600], 'BrkSide': [42.029, -93.627],
        'Crawfor': [42.015, -93.644], 'IDOTRR': [42.022, -93.619], 'Timber': [41.998, -93.650],
        'NoRidge': [42.050, -93.650], 'StoneBr': [42.060, -93.620], 'SWISU': [42.013, -93.654],
        'ClearCr': [42.025, -93.670], 'MeadowV': [41.990, -93.605], 'BrDale': [42.052, -93.628],
        'Blmngtn': [42.062, -93.635], 'Veenker': [42.040, -93.650], 'NPkVill': [42.050, -93.625],
        'Blueste': [42.010, -93.645], 'GrnHill': [42.000, -93.640], 'Landmrk': [42.040, -93.640]
    }
    
    # 3. Inject the Full Names Translation Dictionary
    full_names = {
        'NAmes': 'North Ames', 'Gilbert': 'Gilbert', 'StoneBr': 'Stone Brook',
        'NWAmes': 'Northwest Ames', 'Somerst': 'Somerset', 'BrDale': 'Briardale',
        'NPkVill': 'Northpark Villa', 'NridgHt': 'Northridge Heights', 'Blmngtn': 'Bloomington Heights',
        'NoRidge': 'Northridge', 'SawyerW': 'Sawyer West', 'Sawyer': 'Sawyer',
        'Greens': 'Greens', 'BrkSide': 'Brookside', 'OldTown': 'Old Town',
        'IDOTRR': 'Iowa DOT and Rail Road', 'ClearCr': 'Clear Creek', 'SWISU': 'South & West of ISU',
        'Edwards': 'Edwards', 'CollgCr': 'College Creek', 'Crawfor': 'Crawford',
        'Blueste': 'Bluestem', 'Mitchel': 'Mitchell', 'Timber': 'Timberland',
        'MeadowV': 'Meadow Village', 'Veenker': 'Veenker', 'GrnHill': 'Green Hills',
        'Landmrk': 'Landmark'
    }

    # Apply coordinates to the dataframe
    map_data['Lat'] = map_data['Neighborhood'].map(lambda x: coords.get(x, [42.034, -93.620])[0])
    map_data['Lon'] = map_data['Neighborhood'].map(lambda x: coords.get(x, [42.034, -93.620])[1])
    
    # Apply the full names to a new column
    map_data['FullName'] = map_data['Neighborhood'].map(lambda x: full_names.get(x, x))

    # 4. Create the Interactive Map
    fig = px.scatter_mapbox(
        map_data,
        lat="Lat",
        lon="Lon",
        hover_name="FullName",  # <--- Now uses the beautiful full name!
        # Tell Plotly to hide the raw Lat, Lon, and original Neighborhood abbreviation
        hover_data={"SalePrice": True, "Lat": False, "Lon": False, "Neighborhood": False}, 
        color="SalePrice",
        size="SalePrice",
        color_continuous_scale=["#1a1a1a", "#4CAF50", "#a8ffaa"], 
        zoom=11.5,
        title='Median Sale Price by Neighborhood Map'
    )

    # 5. Apply your specific aesthetic theme
    fig.update_layout(
        mapbox_style="carto-darkmatter", 
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='antiquewhite'),
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    
    return json.loads(fig.to_json())

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