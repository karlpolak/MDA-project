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
import re

#from graphs import make_plot
import plotly.express as px
from pyparsing import col

from app_data import dataset, countries

def convert_into_uppercase(a):
    return a.group(1) + a.group(2).upper()

app = dash.Dash(__name__,title='MDA Poland | Water Security',external_stylesheets=[dbc.themes.CERULEAN],serve_locally = True)
app._favicon = ("assets/favicon.ico")

# add this for heroku
server = app.server

# ### Tab 1: bubble map (colour per cluster)
# # Bubble map
# default_year = 2007
# df = dataset.query(f"Year=={default_year}")
# cluster_map = px.scatter_geo(df, 
#                         locations="iso_alpha", 
#                         color="cluster",
#                         hover_name="Country", 
#                         size="Water stress",
#                         projection="natural earth",
#                         size_max=30)  # TODO maybe add some animation (properties animation_frame & animation_group)

# # Year Options
# cluster_slider = dcc.Slider(
#         id='id_cluster_year',
#         min=1992,
#         max=2017,
#         step=5,
#         value=2007,
#         marks=None,
#         tooltip={"placement": "bottom", "always_visible": True}
#     )   


### Tab 2: bubble map (per region or whole world)
colorscales = px.colors.named_colorscales()

# Bubble map
default_region = 'All'
default_year = 2007
df = dataset.query(f"Continent=='{default_region}' & Year=={default_year}")
bubble_map = px.scatter_geo(df, 
                        locations="iso_alpha", 
                        color="Water stress level",
                        hover_name="Country", 
                        size="Water stress",
                        projection="natural earth",
                        size_max=30,
                        color_continuous_scale='bluered')  # TODO maybe add some animation (properties animation_frame & animation_group)

# Region Options 
dropdown_region = dcc.Dropdown(id='id_region',
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
slider = dcc.Slider(id='id_year',
        min=2004,
        max=2032,
        step=1,
        value=2017,
        marks=None,
        tooltip={"placement": "bottom", "always_visible": True}
    )   # TODO make slider values more modular (minimum & maximum from 'year' in dataset)

### Tab 3: line chart per country

# line chart with bands
default_country = 'China'
start_date = 2004
end_date = 2032
df = dataset.query(f"Country=='{default_country}' & Year>={start_date} & Year<={end_date}")
line_chart_bands = go.Figure([
    go.Scatter(
        name='Mean forecast',
        x=df['Year'],
        y=df['Water stress'],
        mode='lines',
        line=dict(color='rgb(31, 119, 180)'),
        showlegend=False
    ),
    go.Scatter(
        name='95% upper',
        x=df['Year'],
        y=df['Water stress_upper'],
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        showlegend=False
    ),
    go.Scatter(
        name='95% lower',
        x=df['Year'],
        y=df['Water stress_lower'],
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines',
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty',
        showlegend=False
    )
])
line_chart_bands.update_layout(
    yaxis_title='Water Stress (%)',
    title=f"Water stress in '{default_country}'",
    hovermode="x"
)


# Country options
dropdown_country = dcc.Dropdown(id='id_country',
    options=[{"label": re.sub("(^|\s)(\S)", convert_into_uppercase, country), 'value': country} for country in countries],
    value='China',
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


# # Input cluster bubble map
# input_cluster = dbc.Row(dbc.Col(
#     html.Div([
#     cluster_slider]
# )))

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
        # html.Div(children=[html.H4(children='cluster map ...',id='id_title_cluster')],
        #          style={'textAlign':'center','color':'black'}),
        # dbc.Row(
        #     [
        #         dbc.Col(input_cluster, md=3),
        #         dbc.Col(dcc.Graph(id="id_cluster_map",figure=cluster_map), md=9),
        #     ],
        #     align="center"
        # ),
        # html.Hr(),
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
                dbc.Col(dcc.Graph(id="id_line_chart_bands",figure=line_chart_bands), md=9),
            ],
            align="center"
        ),
    ],
    fluid=True,
)


# Update bubble map 
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
                        color="Water stress level",
                        hover_name="Country", 
                        size="Water stress",
                        projection="natural earth",
                        size_max=30,
                        color_continuous_scale='bluered')
    return title, bubble_map


# Update line chart
@app.callback(
    Output('id_title_line','children'),
    Output('id_line_chart_bands','figure'),
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
        start_date = max(new_start_date, 2004)  
        end_date = min(new_end_date, 2032) 

    df = dataset.query(f"Country=='{country}' & Year>={start_date} & Year <={end_date}")
    # line chart with bands
    line_chart_bands = go.Figure([
        go.Scatter(
            name='Mean forecast',
            x=df['Year'],
            y=df['Water stress'],
            mode='lines',
            line=dict(width=2,color='rgba(47, 164, 231,1)'),
            showlegend=False
        ),
        go.Scatter(
            name='95% upper',
            x=df['Year'],
            y=df['Water stress_upper'],
            mode='lines',
            marker=dict(color="rgba(255,103,92,0.8)"),
            line=dict(width=0.5,dash='dot'),
            showlegend=False
        ),
        go.Scatter(
            name='95% lower',
            x=df['Year'],
            y=df['Water stress_lower'],
            marker=dict(color="rgba(255,103,92,0.8)"),
            line=dict(width=0.5,dash='dot'),
            mode='lines',
            fillcolor='rgba(255,103,92,0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])
    line_chart_bands.update_layout(
        yaxis_title='Water stress (%)',
        title=f"Water stress in {country}",
        title_x=0.5,
        hovermode="x",
    )

    return f"Water stress for {country} from {start_date} to {end_date}", line_chart_bands


if __name__ == '__main__':
    app.run_server(debug=False)