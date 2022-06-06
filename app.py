import dash
#import dash_html_components as html
from dash import html
#import dash_core_components as dcc
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from plotly.subplots import make_subplots

import plotly.graph_objects as go
import numpy as np
import pandas as pd

#from graphs import make_plot
import plotly.express as px
from pyparsing import col



app = dash.Dash(__name__,title='Water security',external_stylesheets=[dbc.themes.CERULEAN],serve_locally = True)

# add this for heroku
server = app.server

# dataset
# dataset = px.data.gapminder()  # some built-in data for now
from app_data import dataset


### Tab 1: bubble map (per region or whole world)
# Bubble map
default_region = 'Asia'
default_year = 2007
df = dataset.query(f"Continent=='{default_region}' & Year=={default_year}")
bubble_map = px.scatter_geo(df, 
                        locations="iso_alpha", 
                        color="Continent",
                        hover_name="Country", 
                        size="Water stress",
                        projection="natural earth",
                        size_max=30)  # TODO maybe add some animation (properties animation_frame & animation_group)

# Region Options 
dropdown_region = dcc.Dropdown(
    id='id_region',
    options=[{"label":'All','value':'All'},
             {"label":'Asia','value':'Asia'},
             {"label":'Europe','value':'Europe'},
             {"label":'Africa','value':'Africa'},
             {"label":'Americas','value':'Americas'},
             {"label":'Oceania','value':'Oceania'}
             ],
    value='All',
    searchable=False)

# Year Options
slider = dcc.Slider(
        id='id_year',
        min=2004,
        max=2032,
        step=1,
        value=2017,
        marks=None,
        tooltip={"placement": "bottom", "always_visible": True}
    )   # TODO make slider values more modular (minimum & maximum from 'year' in dataset)

### Tab 2: line chart per country
# line chart
default_country = 'China'
start_date = 2004
end_date = 2032
df = dataset.query(f"Country=='{default_country}' & Year>={start_date} & Year<={end_date}")
line_chart = px.line(df, x="Year", y="Water stress", title=f"Water stress in '{default_country}'")

# Country options
dropdown_country = dcc.Dropdown(
    id='id_country',
    options=[{"label":'China','value':'China'},
             {"label":'Finland','value':'Finland'},
             {"label":'Morocco','value':'Morocco'},
             ],
    value='Afghanistan',
    searchable=False)

# History options
range_slider = dcc.RangeSlider(id='id_range',
                            min=2004, 
                            max=2032, 
                            step=2, 
                            value=[2010, 2022],
                            tooltip={"placement": "bottom", "always_visible": True},
                            pushable=2,
                            marks=None) # TODO make slider values more modular (e.g. min & max from the 'year' column of the dataset)

# Input bubble map
input_bubble = dbc.Row(dbc.Col(
    html.Div([
    dropdown_region,
    html.Br(),
    slider]
)))

# Input line chart
input_line = dbc.Row(dbc.Col(
    html.Div([
    dropdown_country,
    html.Br(),
    range_slider]
)))

app.layout = dbc.Container(
    [
        html.Div(children=[html.H1(children='Water Security'),
                           html.H2(children='MDA Team Poland')],
                 style={'textAlign':'center','color':'black'}),
        html.Hr(),
        html.Div(children=[html.H4(children='...',id='id_title_bubble')],
                 style={'textAlign':'center','color':'black'}),
        dbc.Row(
            [
                dbc.Col(input_bubble, md=3),
                dbc.Col(dcc.Graph(id="id_bubble_map",figure=bubble_map), md=9),
            ],
            align="center"
        ),
        html.Hr(),
        html.Div(children=[html.H4(children='...',id='id_title_line')],
                 style={'textAlign':'center','color':'black'}),
        dbc.Row([
                dbc.Col(input_line, md=3),
                dbc.Col(dcc.Graph(id="id_line_chart",figure=line_chart), md=9),
            ],
            align="center"
        )
    ],
    fluid=True,
)

@app.callback(
    Output('id_title_bubble','children'),
    Output('id_bubble_map','figure'),
    [Input('id_region', 'value'),
    Input('id_year', 'value')
     ]
)
def update_map(region, year):
    if region == 'All' or region is None:
        df = dataset.query(f"Year=={year}")
        title = f"Global water stress in {year}"
        
    else:
        df = dataset.query(f"Continent=='{region}' & Year=={year}")
        title = f"Water stress for {region} in {year}"

    bubble_map = px.scatter_geo(df, 
                        locations="iso_alpha", 
                        color="Continent",
                        hover_name="Country", 
                        size="Water stress",
                        projection="natural earth",
                        size_max=30)  # TODO maybe add some animation (properties animation_frame & animation_group)
    return title, bubble_map

@app.callback(
    Output('id_title_line','children'),
    Output('id_line_chart','figure'),
    [Input('id_country', 'value'),
    Input('id_range', 'value')
     ]
)
def update_chart(country, range):
    if country is None:
        country = default_country

    start_date = range[0]
    end_date = range[1]

    # always make sure range for plot is at least 5 years
    if start_date == end_date:
        new_start_date = start_date - 2
        new_end_date = end_date + 2
        start_date = max(new_start_date, 2004)  # TODO make 1952 more modular (minimum of years in dataset)
        end_date = min(new_end_date, 2032)  # TODO make 2007 more modular (minimum of years in dataset)

    df = dataset.query(f"Country=='{country}' & Year>={start_date} & Year <={end_date}")
    line_chart = px.line(df, x="Year", y="Water stress", title=f"Water stress in {country}")
    return f"Water stress for {country} from {start_date} to {end_date}", line_chart

if __name__ == '__main__':
    app.run_server(debug=True)