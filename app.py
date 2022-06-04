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



app = dash.Dash(__name__,title='Water security',external_stylesheets=[dbc.themes.CERULEAN],serve_locally = False)

# add this for heroku
server = app.server

# dataset
dataset = px.data.gapminder()  # some built-in data for now


### Tab 1: bubble map (per region or whole world)
# Bubble map
df = dataset.query("year==2007")
bubble_map = px.scatter_geo(df, locations="iso_alpha", color="continent",
                     hover_name="country", size="pop",
                     projection="natural earth")

# Region Options 
dropdown_region = dcc.Dropdown(
    id='id_region',
    options=[{"label":'Africa','value':'Africa'},
             {"label":'Central & East Asia','value':'Central & East Asia'},
             {"label":'Southwest Asia and Middle East','value':'Southwest Asia and Middle East'},
             ],
    value='Africa')

# Year Options
slider = dcc.Slider(
        id='id_year',
        min=1992,
        max=2032,
        step=5,
        value=2017,
        marks=None,
        tooltip={"placement": "bottom", "always_visible": True}
    )

### Tab 2: line chart per country
# line chart
country = 'Afghanistan'
start_date = 1957
end_date = 1992
df = dataset.query(f"country=='{country}' & year>={start_date} & year <={end_date}")
line_chart = px.line(df, x="year", y="gdpPercap", title='GDP per capita in {country}'.format(country="'Afghanistan'"))

# Country options
dropdown_country = dcc.Dropdown(
    id='id_country',
    options=[{"label":'Afghanistan','value':'Afghanistan'},
             {"label":'Finland','value':'Finland'},
             {"label":'Morocco','value':'Morocco'},
             ],
    value='Afghanistan')

# History options
range_slider = dcc.RangeSlider(id='id_range',
                            min=1952, 
                            max=2007, 
                            step=5, 
                            value=[1957, 1987],
                            tooltip={"placement": "bottom", "always_visible": True},
                            pushable=2,
                            marks=None)

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
    [Input('id_region', 'value'),
    Input('id_year', 'value')
     ]
)
def update_chart(region, year):
    return 'Water stress for ' + region + ' in ' + str(year)

@app.callback(
    Output('id_title_line','children'),
    Output('id_line_chart','figure'),
    [Input('id_country', 'value'),
    Input('id_range', 'value')
     ]
)
def update_chart(country, range):
    start_date = range[0]
    end_date = range[1]
    df = dataset.query(f"country=='{country}' & year>={start_date} & year <={end_date}")
    line_chart = px.line(df, x="year", y="gdpPercap", title=f"GDP per capita in {country}")
    return 'Water stress for ' + country + ' from ' + str(range[0]) + ' to ' + str(range[1]), line_chart

if __name__ == '__main__':
    app.run_server(debug=True)