# -*- coding: utf-8 -*-
import sys
from random import randint

import dash
import dash_core_components as dcc
import dash_html_components as html
from coronadash.dash_components import Col, Row
from coronadash.conf.config import myapp
from coronadash.conf.config import mydash
import pandas as pd 
import datetime
from dash.dependencies import Input, Output 
#import dash_dangerously_set_inner_html
from collections import OrderedDict
import plotly.graph_objs as go
import random
import requests
from tornado import httpclient
from coronadash.dash_server import app
#
# Setup the embedded Dash App and create the actual dash layout, callbacks, etc.:
# see: _create_app()
# 

def _create_app_layout(*args, **kwargs):
    ''' 
        Creates the actual dash application and layout
        Just put any Dash layout in here.
        Documentation and examples: https://dash.plot.ly/

        The default route is: /dash which calls the handler/dash.py which creates the app
        and renders the pow_dash template.    
    '''

    import os
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "data/2019_ncov_data.csv"))
    df["Date"] = pd.to_datetime(df["Date"])
    #add a new column that only contains the day
    df['day'] = df['Date'].dt.day
    # same for the month
    df['month'] = df['Date'].dt.month

    #groupby day, month and aggregate the Confirmed as sum
    #df_confirmed_by_day = df.groupby(["Date"]).agg({"Confirmed": "sum"}) 
    #df = df_confirmed_by_day
    app.layout = html.Div([
        dcc.Graph(id='corona_graph'),
        dcc.Slider(
            id='day-slider',
            min=df['Date'].min(),
            max=df['Date'].max(),
            value=df['Date'].min(),
            marks={str(i): str(i) for i in df['Date'].unique()},
            step=None
        )
    ])


    @app.callback(
        Output('corona_graph', 'figure'),
        [Input('day-slider', 'value')])
    def update_figure(selected_day):
        filtered_df = df[df.Date == selected_day]
        traces = []
        #for i in filtered_df["Province/State"].unique():
        #    df_by_continent = filtered_df[filtered_df['Province/State'] == i]
        #    traces.append(go.Bar(
        #        x=str(i),
        #        y=df_by_continent['Confirmed'],
        #        
        #    ))

        return {
            'data': [
                { 
                    "y" : [12,22,33,44,55],
                    "x" : str(df['Date'].unique()),
                    "type" : "bar"
                }
            ],
            'layout': {
                "title" : "Confirmed infections by Province/State and date"
            }
        }

    return app.layout


def dispatcher(request, index=True, **kwargs):
    '''
        Dispatch the Dash and Dash Ajax requests
    '''
    #kwargs["external_stylesheets"] = mydash["external_stylesheets"]
    #
    # only serve the base layout once. 
    # 
    if index:
        try:
            app.layout = _create_app_layout(**kwargs)
        except dash.exceptions.DuplicateCallbackOutput:
            pass
        
    params = {
        'data': request.body,
        'method': request.method,
        'content_type': request.headers.get('Content-type')
    }
    with app.server.test_request_context(request.path, **params):
        app.server.preprocess_request()
        try:
            response = app.server.full_dispatch_request()
        except Exception as e:
            response = app.server.make_response(app.server.handle_exception(e))
            print(70*"=")
            print("done dash dispatching")
            print(70*"=")

        response.direct_passthrough = False
        return response.get_data()