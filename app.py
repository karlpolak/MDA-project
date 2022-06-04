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
from pyparsing import col  # imported this to make line charts



app = dash.Dash(__name__,title='Water security',external_stylesheets=[dbc.themes.CERULEAN],serve_locally = False)

# add this for heroku
server = app.server

# Chart
fig = make_subplots(rows=1, cols=1)
fig.add_trace(
    go.Scatter(x=np.arange(0,10,1),
               y=np.arange(0,10,1)*2 + np.random.randn(),
               name='Example'),
    row=1, col=1)
fig.update_layout(width=1500)

# Country Options
dropdown = dcc.Dropdown(
    id='id_country',
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

# Text input (if any)
# text = dbc.InputGroup([
#         dbc.Input(id='id_start_date',value="2020-01-01", type="text")],)

# Start Date, End Date & Number of Mixtures
input_groups = dbc.Row(dbc.Col(
    html.Div([
    dropdown,
    html.Br(),
    slider]
)))

app.layout = dbc.Container(
    [
        html.Div(children=[html.H1(children='Water Security'),
                           html.H2(children='MDA Team Poland'),
                           html.H4(children='...',id='id_title')],
                 style={'textAlign':'center','color':'black'}),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(input_groups, md=3),
                dbc.Col(dcc.Graph(id="id_graph",figure=fig), md=9),
            ],
            align="center",
        ),
    ],
    fluid=True,
)

@app.callback(
    Output('id_title','children'),
    [Input('id_country', 'value'),
    Input('id_year', 'value')
     ]
)
def update_chart(country, year):
    return 'Water stress for ' + country + ' in ' + str(year)

if __name__ == '__main__':
    app.run_server(debug=True)